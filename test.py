import multiprocessing
import time


def f(bandwidth):
    while True:
        for i in range(1000):
            bandwidth.value = i




if __name__ == '__main__':

    band = multiprocessing.Value('d', 0.0)

    p =  multiprocessing.Process(target=f, args=(band,))
    p.start()

    for j in range(100):
        print(band.value)
        time.sleep(1)



