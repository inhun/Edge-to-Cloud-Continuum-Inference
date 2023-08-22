from multiprocessing import Process
from apscheduler.schedulers.blocking import BlockingScheduler
from net import net_utils

def get_bandwidth(conn):
    """
    하나의 신호 전송에 의한 대역폭 계산
    :param conn: 연결된 연결
    :return: 대역폭 MB/s
    """
    # 전송 지연 가져오기
    _,latency = net_utils.get_data(conn)
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
    def __init__(self, ip, port=9922, interval=3):
        super(MonitorServer, self).__init__()
        self.ip = ip
        self.port = port
        self.interval = interval


    def start_server(self) -> None:
        # 소켓 서버 생성
        socket_server = net_utils.get_socket_server(self.ip, self.port)
        # 연결 없이 10초 이상 지나면 차단 및 대기 없이 자동으로 연결이 해제됩니다.
        # socket_server.settimeout(10)

        # 클라이언트 연결 대기 클라이언트 연결이 없으면 항상 차단 및 대기
        conn, client = socket_server.accept()

        # 전송 대역폭 MB/s 가져오기
        bandwidth = get_bandwidth(conn)

        # 데이터 고착을 방지하기 위해 수신할 break 메시지 삽입
        net_utils.get_short_data(conn)

        # 획득한 대역폭을 클라이언트로 전송
        net_utils.send_short_data(conn, bandwidth, "bandwidth", show=False)

        # close connection
        net_utils.close_conn(conn)
        net_utils.close_socket(socket_server)


    def schedular(self):
        # 타이밍 메커니즘을 사용하여 일정 기간 후 대역폭 모니터링
        # 스케줄러 만들기
        scheduler = BlockingScheduler()

        # 작업 추가
        scheduler.add_job(self.start_server, 'interval', seconds=self.interval)
        scheduler.start()


    def run(self) -> None:
        # self.schedular()
        self.start_server()



# if __name__ == '__main__':
#     ip = "127.0.0.1"
#     monitor_ser = MonitorServer(ip=ip)
#
#     monitor_ser.start()
#     monitor_ser.join()
#
#


