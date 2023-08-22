import torch
import multiprocessing
import time
import requests

from utils.monitor_client import *
from utils.config import load_config

import warnings
warnings.filterwarnings('ignore')







if __name__ == '__main__':
    print(requests.get('http://ip.jsontest.com').json()['ip'])



    ip, port = '163.180.117.39', 8090

    config = load_config('config.json')
    edge_info = config['edge']
    for i in edge_info:
        print(i)


    bandwidth_value = multiprocessing.Value('d', 0.0)
    monitor_client = MonitorClient(ip=ip, bandwidth_value=bandwidth_value)
    monitor_client.start()

    while True:
        print(bandwidth_value.value)
        time.sleep(1)















