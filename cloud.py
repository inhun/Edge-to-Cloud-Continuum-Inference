import torch
import socket

from utils import utils
from utils.monitor_server import *

import warnings
warnings.filterwarnings('ignore')




if __name__ == '__main__':
    ip, port = '0.0.0.0', 8090
    device = 'cpu'

    if device == 'cuda' and torch.cuda.is_available() == False:
        raise RuntimeError('cuda is not available')
    
    while True:
        socket_server = utils.get_socket_server(ip, port)

        monitor_server = MonitorServer(ip=ip)
        monitor_server.start()
        monitor_server.join()





