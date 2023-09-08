import socket 
import multiprocessing
import time
import pickle

from apscheduler.schedulers.blocking import BlockingScheduler

import torch


class MonitorClient(multiprocessing.Process):
    def __init__(self, ip, bandwidth_value, port=8090, interval=5):
        super(MonitorClient, self).__init__()
        self.ip = ip
        self.bandwidth_value = bandwidth_value
        self.port = port
        self.interval = interval

        self.servers = []

        self.conn = self.get_socket_client(self.ip, self.port)



    def get_socket_client(self, ip, port):
        conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        conn.connect((ip, port))
        return conn


    def send_data(self, conn, x, msg='msg', show=True):
        send_x = pickle.dumps(x)
        conn.sendall(pickle.dumps(len(send_x)))
        resp_len = conn.recv(1024).decode()

        conn.sendall(send_x)
        resp_data = conn.recv(1024).decode()
        
        if show:
            print(f'get {resp_data}, {msg} has been sent successfully')


    def send_short_data(self, conn, x, msg='msg', show=True):
        send_x = pickle.dumps(x)
        conn.sendall(send_x)

        if show:
            print(f'short message, {msg} has been sent successfully')


    def get_short_data(self, conn):
        return pickle.loads(conn.recv(1024))


    def start_client(self):
        data = torch.rand((1, 3, 224, 224))

        try:
            self.send_data(self.conn, data, 'data', show=True)
            self.send_short_data(self.conn, 'break', show=True)

            latency = self.get_short_data(self.conn)

            if latency is not None:
                self.bandwidth_value.value = latency

            time.sleep(1)

        except ConnectionRefusedError:
            print('[ERROR] Connection refused, try again')
            pass


    def scheduler(self):
        scheduler = BlockingScheduler()

        scheduler.add_job(self.start_client, 'interval', seconds=self.interval, id='get_server_status')
        scheduler.start()

    
    def run(self):
        self.scheduler()



if __name__ == '__main__':
    bandwidth_value = multiprocessing.Value('d', 0.0)
    monitor_client = MonitorClient(ip='localhost', bandwidth_value=bandwidth_value)
    monitor_client.start()

    while True:
        print(bandwidth_value.value)
        time.sleep(1)

