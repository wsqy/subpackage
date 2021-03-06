#### 项目主要分为四个子模块:
```
分包模块:根据接收到的分包上传请求,生成子包,并记录分包的一些信息
上传模块:根据配置信息,传到对应的云存储中
消息通知:根据通知级别按对应的通知级别进行消息通知
日志系统:对任务关键时刻,错误信息进行记录,为接入ELK日志系统预留
```
#### 项目的解决方案选定:
##### 线程与协程的选择
由于分包需要大量的磁盘IO操作,子包上传需要大量的网络IO操作,在程序运行中让高速的cpu运算等待龟速的IO操作肯定不合算,在综合考虑之后决定采用协程来异步IO操作,程序运行中不需要考虑IO操作,在IO操作完成后的合适的时刻跳转回来继续执行.
关于线程和协程选择时的考虑:协程最大的优势就是极高的执行效率.因为协程本质只有一个线程,所以子程序切换不是线程切换,而是由程序自身控制,因此,没有线程切换的开销,和多线程比,线程数量越多,协程的性能优势就越明显.
第二大优势就是不需要多线程的锁机制,因为只有一个线程,也不存在同时写变量冲突,在协程中控制共享资源不加锁,只需要判断状态就好了,所以执行效率比多线程高很多.
第三大优势就是存储开销:线程的开销是1M左右,而协程只需要保存一些用户态信息,开销不过1K左右

##### 消息队列的选择
现在流行的用作消息队列的技术有RabbitMQ和redis两种,考虑到公司服务端现在用的是redis做消息队列的,为了保证运维工具和服务端的统一,初期工具只实现了redis的接口,但是考虑到redis实现的是简单的队列,而且没有持久化,负载均衡可以说是没有（一个KEY不可能放到多台服务器）,为了服务以后的可升级性,决定将加载的方式做成动态加载,在接受任务或者配置项内指定消息队列的类型

##### 任务失败的多次尝试的方法:
在任务进行的过程中,总会遇到一些不可控的因素,比如:分包的时候参数的全,母包不存在,母包所在目录权限问题等等,在程序运行过程中首先要能捕获这些可能的不可控因素,既可以保证程序的流畅运行,也可以程序再运行一段时间后重试此任务.打包遇到错误的时候,记录失败时间,扔到失败尝试的队列中,单独开个协程监控此队列.

##### 任务恢复机制
取到任务后再下一步分包之前先把任务进行下备份,分包完成后不管是否成功都先从打包备份队列中删除此任务信息,如果成功将分包后的状态信息备份到上传备份队列,如果失败将打包任务扔到失败重试队列中.如果子包上传成功就从上传备份队列中删除信息.
当程序重新启动的时候 先检查上传备份队列中是否有任务,如果有就先将这些任务上传完成,再检查备份的打包队列中是否有任务,如果有就将任务塞到打包队列的前端.这样任务恢复的过程就完成了,下面正常启动程序就好.


#### 项目实现:
##### 协程控制:
```
def gevent_join():
    gevent_task = []
    for each in range(packet_count):
        gevent_task.append(gevent.spawn(packet))
    for each in range(retry_packet_count):
        gevent_task.append(gevent.spawn(retry_packet))
    for each in range(message_count):
        message = initialize_message()
        gevent_task.append(gevent.spawn(message.message_queue()))
    for each in range(retry_upload_count):
        upload = initialize_upload()
        gevent_task.append(gevent.spawn(upload.get_upload_task))
    gevent.joinall(gevent_task)
```


`packet`方法是取任务调用分包的方法,retry_packet是重试失败的打包任务的方法,取任务都是调用的`get_data_info(self, retry=False)` retry参数是指定是不是取重试的任务,默认是False,即取的是正常的任务   

`get_upload_task`是子包上传的方法,分包完成后要读取配置信息,完成子包上传

`message_queue`是消息通知系统,任务完成将信息通知给服务端

##### 分包模块:
在开始打包前需要进行一系列检查:
- 确认参数完整性
- 检查游戏母包是否存在
- 检查游戏母包权限
- 生成channel_file文件名并检查是否存在   

检查过程中项目的难点在于子包的命名中中包含母包的版本号,在apk文件中此信息是保存在AndroidManifest.xml文件中的,是一个二进制文件,百度上的是有一些解决方法,但是局限于纯ascll字符,对含中文的解包不了,公司的实际需求中,大部分子包还都是还有中文的,最后采用了github上一位大牛的解决方案[AxmlParserPY](https://github.com/antitree/AxmlParserPY)

接下来就是生成待填充的文件,写入apk文件中就好了.这里有个问题是打包任务多的话每个子包生成一些待填充的文件,等填充完再删除那肯定是不行的 所以使用了`python中的临时文件库tempfile`中的`tempfile.NamedTemporaryFile`方法创建临时文件,使用完自动销毁    


##### 上传模块:
现在用的两个云存储提供商为阿里云和金山云.这两个提供商都提供了Python实现的SDK OSS2和ks3.关于上传部分这两份SDK也都实现了上传,断点续传,分块上传的方法,考虑到子包的大小都是300MB左右,加上可以使用内网的因素决定项目中主要采用分块上传的方式,但是OSS2中只提供了分块上传的方式但是并不能异步上传,项目中这又是个很重要的点,ks3中实现了异步上传的功能,阅读其源码发现,他是使用了`filechunkio`这个第三方库实现的,按照ks3中的实现方式,自己又为oss2写了个.

##### 消息通知模块:
在实现 分包模块和上传模块后 消息通知的难度就不是很大了.知识要针对各种消息的请求类型,请求的数据格式完成对应的接口就好,各种可能情况还是很多的.
