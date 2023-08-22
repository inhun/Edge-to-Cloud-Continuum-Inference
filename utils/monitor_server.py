from multiprocessing import Process
from apscheduler.schedulers.blocking import BlockingScheduler
from utils import utils

def get_bandwidth(conn):
    """
    하나의 신호 전송에 의한 대역폭 계산
    :param conn: 연결된 연결
    :return: 대역폭 MB/s
    """
    # 전송 지연 가져오기
    _,latency = utils.get_data(conn)
    # print(f"{latency} ms \n")
    # 데이터 Byte의 바이트 수 계산 수신 데이터 크기는 [1,3,224,224]로 고정
    # data_size = 1 * 3 * 224 * 224 * 8

    # x = torch.rand((1, 3, 224, 224))
    # print(len(pickle.dumps(x)))
    # 결과 데이터 크기는 602541바이트입니다.
    data_size = 602541

    # 컴퓨팅 대역폭 MB/s
    bandwidth = (data_size/1024/1024) / (latency / 1000)
    print(f"monitor server get bandwidth : {bandwidth} MB/s ")
    return bandwidth


class MonitorServer(Process):
    """
        대역폭 모니터 서버의 작업 프로세스는 다음과 같습니다. ip는 들어오는 ip 포트는 기본적으로 9922입니다.
        1. 대역폭 모니터 클라이언트가 보낸 데이터: 타이밍 메커니즘에 의해 켜지고 가끔씩 켜집니다.
        2. 전송 시간(ms)에 필요한 전송 지연을 기록합니다.
        3. 대역폭을 계산하고 속도를 MB/s로 변환
        4. 대역폭 데이터를 클라이언트에 반환
    """
    def __init__(self, ip, port=9922, interval=10):
        super(MonitorServer, self).__init__()
        self.ip = ip
        self.port = port
        self.interval = interval

        self.socket_server = utils.get_socket_server(self.ip, self.port)
        self.conn, self.client = self.socket_server.accept()

        print(f'socket_server: {self.socket_server}')
        print(f'conn: {self.conn}')
        print(f'client: {self.client}')
    
    def __del__(self):
        # close connection
        utils.close_conn(self.conn)
        utils.close_socket(self.socket_server)


    def start_server(self) -> None:
        # 전송 대역폭 MB/s 가져오기
        bandwidth = get_bandwidth(self.conn)

        # 데이터 고착을 방지하기 위해 수신할 break 메시지 삽입
        utils.get_short_data(self.conn)

        # 획득한 대역폭을 클라이언트로 전송
        utils.send_short_data(self.conn, bandwidth, "bandwidth", show=False)



    def schedular(self):
        # 타이밍 메커니즘을 사용하여 일정 기간 후 대역폭 모니터링
        # 스케줄러 만들기
        scheduler = BlockingScheduler(timezone='Asia/Seoul')

        # 작업 추가
        scheduler.add_job(self.start_server, 'interval', seconds=self.interval, id='send_server_status')
        scheduler.start()


    def run(self) -> None:
        self.schedular()
        # self.start_server()



# if __name__ == '__main__':
#     ip = "127.0.0.1"
#     monitor_ser = MonitorServer(ip=ip)
#
#     monitor_ser.start()
#     monitor_ser.join()
#
#


