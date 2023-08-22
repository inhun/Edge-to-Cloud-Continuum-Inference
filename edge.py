import torch
import multiprocessing
import time

from utils.monitor_client import *

import warnings
warnings.filterwarnings('ignore')







if __name__ == '__main__':
    ip, port = '127.0.0.1', 8090



    bandwidth_value = multiprocessing.Value('d', 0.0)
    monitor_client = MonitorClient(ip=ip, bandwidth_value=bandwidth_value)
    monitor_client.start()

    while True:
        print(bandwidth_value.value)
        time.sleep(1)















