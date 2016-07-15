import subprocess, os
from os.path import expanduser

# parameters
config_file = ".bashrc"

def script(cmd):
    subprocess.call(cmd,  shell=True)
home = expanduser("~")


script("sudo yum install openssl -y")
script("sudo yum install openssl-devel openssl-static readline readline-devel readline-static sqlite-devel bzip2-devel bzip2-libs -y")
script("sudo yum install gcc -y")
script("sudo yum install git-y")
script("git clone git://github.com/yyuu/pyenv.git ~/.pyenv")

# install pyenv
env_path = home+"/"+".pyenv"
if not os.path.exists(env_path):
    os.makedirs(env_path)


config_file = home+"/"+config_file
print config_file
if os.path.exists(config_file) is False:
    print "Error: can't find config file "+ config_file
    exit()
with open(config_file, 'a') as file:
    file.write('export PYENV_ROOT="$HOME/.pyenv"\n')
    file.write('export PATH="$PYENV_ROOT/bin:$PATH"\n')
    file.write('eval "$(pyenv init -)"\n')
os.environ["PYENV_ROOT"] = home+"/"+".pyenv"
os.environ["PATH"]  +=  ":"+os.environ["PYENV_ROOT"]+"/bin"
script("pyenv init")
print os.environ["PATH"]
script("source "+config_file)
python_version = "2.7.11"
script("pyenv install %s" % python_version)
script("pyenv rehash")
script("pyenv global %s" % python_version)
script("rm -rf ./pyenv-master")

script("git clone https://github.com/ks3sdk/ks3-python-sdk.git")
script("cd ks3-python-sdk")
script("python setup.py install")
script("cd ..")
script("rm -rf ks3-python-sdk")

script("pip install -r require")
