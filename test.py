import multiprocessing
import time
import socket
import psutil
import os



def f(bandwidth):
    while True:
        for i in range(1000):
            bandwidth.value = i




if __name__ == '__main__':
    print(os.getpid())
    while True:
        # 코어당 CPU 사용량
        print(psutil.cpu_percent(0.1, True))

        # boot 이후 일어난 context switch, interrupt, software interrupt, systemcall 수들
        # print(psutil.cpu_stats())


        # cpu 클럭 주파수
        print(psutil.cpu_freq())





        print(f'RAM available: {(psutil.virtual_memory().available)/(1024*1024):0.2f} MB')
        print(f'RAM total: {psutil.virtual_memory().total/1024/1024:0.2f} MB')
        print("RAM: ", psutil.virtual_memory().available / psutil.virtual_memory().total * 100)
        print('=================================================================')

        time.sleep(1)


    