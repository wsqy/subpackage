import time

a = 0
print(a)
while True:
    if int(time.time()) % 3 == 0:
        a += 1
