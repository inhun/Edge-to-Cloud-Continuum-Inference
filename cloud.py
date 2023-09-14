import torch
import socket

from utils import net_utils
from utils.monitor_server import *
from utils.utils import load_config, get_ip

import warnings
warnings.filterwarnings('ignore')



if __name__ == '__main__':
    config_path = 'config.json'
    config = load_config(config_path)

    cloud_config = config['cloud']
    ip, data_port, status_port = cloud_config['external_ip'], cloud_config['data_port'], cloud_config['status_port']
    
    device = 'cpu'






    if device == 'cuda' and torch.cuda.is_available() == False:
        raise RuntimeError('cuda is not available')
    
    while True:
        # socket_server = net_utils.get_socket_server(ip, port)

        monitor_server = MonitorServer(ip=ip, status_port=8091)
        monitor_server.start()
        monitor_server.join()





