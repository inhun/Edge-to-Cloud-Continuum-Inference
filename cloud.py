import torch
import warnings
warnings.filterwarnings('ignore')


from utils.utils import *
from utils.monitor_server import *






if __name__ == '__main__':
    ip, port = '0.0.0.0', 8090
    device = 'cpu'

    if device == 'cuda' and torch.cuda.is_available() == False:
        raise RuntimeError('cuda is not available')
    
    while True:
        socket_server = get_socket_server(ip, port)

        monitor_server = MonitorServer(ip=ip)
        monitor_server.start()
        monitor_server.join()





