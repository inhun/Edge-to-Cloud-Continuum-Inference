import socket
import time
import pickle
import platform
import threading

from multiprocessing import Process
from apscheduler.schedulers.blocking import BlockingScheduler

import torch 



class MonitorServer(Process):
    def __init__(self, ip, status_port=8091, interval=5):
        super(MonitorServer, self).__init__()
        self.ip = ip
        self.status_port = status_port
        self.interval = interval

        self.socket_server = self.get_socket_server(self.status_port)
        self.clients = []        


    def get_new_client(self):
        while True:
            conn, _ = self.socket_server.accept()
            self.clients.append(conn)
            print(self.clients)
            print(f'new client {id(self.clients)}')
            


    def broadcast(self, clients, msg):
        for i in clients:
            message = pickle.dumps(msg)
            i.sendall(message)


    def get_socket_server(self, port):
        socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        sys_platform = platform.platform().lower()
        if 'windows' in sys_platform:
            socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # windows
        else:
            socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) # macos or linux


        print(socket_server)

        socket_server.bind(('0.0.0.0', port))
        socket_server.listen(10)
        
        return socket_server



    def get_data(self, conn):
        data_len = pickle.loads(conn.recv(1024))
        conn.sendall("yes len".encode())

        # 데이터 수신 및 대기 시간 기록
        sum_time = 0.0
        data = [conn.recv(1)]
        while True:
            start_time = time.perf_counter()
            packet = conn.recv(40960)
            end_time = time.perf_counter()
            transport_time = (end_time - start_time) * 1000  # 단위를 ms로 변환
            sum_time += transport_time

            data.append(packet)
            if len(b"".join(data)) >= data_len:
                break
            # if len(packet) < 4096: break

        parse_data = pickle.loads(b"".join(data))
        conn.sendall("yes".encode())

        return parse_data,sum_time
    

    def get_short_data(self, conn):
        return pickle.loads(conn.recv(1024))


    def send_short_data(self, conn, x, msg='msg', show=True):
        send_x = pickle.dumps(x)
        conn.sendall(send_x)

        if show:
            print(f'short message, {msg} has been sent successfully')


    def get_bandwidth(self, conn):
        _, latency = self.get_data(conn)

        x = torch.rand((1, 3, 224, 224))
        print(len(pickle.dumps(x)))

        data_size = 602541

        bandwidth = (data_size/1024/1024) / (latency / 1000)
        print(f"monitor server get bandwidth : {bandwidth} MB/s ")
        return bandwidth

    

    def start_server(self):
        print(f'start server2 {id(self.clients)}')
        clients = self.clients
        for client in clients:
            bandwidth = self.get_bandwidth(client)

            self.get_short_data(client)
            self.send_short_data(client, bandwidth, 'bandwidth', show=True)


    def scheduler(self):
        print(f'scheduler {id(self.clients)}')
        scheduler = BlockingScheduler(timezone='Asia/Seoul')

        scheduler.add_job(self.start_server, 'interval', args=(), seconds=self.interval, id='send_server_status', )
        scheduler.start()


    def run(self):
        thread = threading.Thread(target=self.get_new_client, args=(), daemon=True)
        thread.start()
         
        self.scheduler()



if __name__ == '__main__':
    while True:
        ip = '0.0.0.0'

        monitor_server = MonitorServer(ip=ip)
        monitor_server.start()
        monitor_server.join()
        print('restart')









