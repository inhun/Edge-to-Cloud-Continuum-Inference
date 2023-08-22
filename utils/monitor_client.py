import time
import torch
from multiprocessing import Process
from utils import utils
from apscheduler.schedulers.blocking import BlockingScheduler
import multiprocessing


class MonitorClient(Process):
    """
        워크플로우가 다음과 같은 대역폭 모니터 클라이언트: 타이밍 메커니즘을 통해 일정한 간격으로 측정
        1. 데이터를 생성하여 서버로 전송하면 서버에서 시간을 기록합니다.
        2. 데이터 획득의 전송 지연은 프로세스 통신 사용 - 에지에서 모델 분할을 위해
    """
    def __init__(self, ip, bandwidth_value, port=9922, interval=10):
        super(MonitorClient, self).__init__()
        self.ip = ip
        self.bandwidth_value = bandwidth_value
        self.port = port
        self.interval = interval

        self.conn = utils.get_socket_client(self.ip, self.port)


    def __del__(self):
        utils.close_conn(self.conn)

    def start_client(self) -> None:
        # 들어오는 데이터 크기
        data = torch.rand((1, 3, 224, 224))

        try:
            print(1)
            # 서버와 연결하여 사고가 발생하면 계속 시도하십시오.
            # 데이터 보내기

            utils.send_data(self.conn, data, "data", show=False)

            # 끈끈한 패킷을 방지하기 위해 break 메시지를 삽입하십시오.
            utils.send_short_data(self.conn, "break", show=False)

            # 응답의 데이터 지연이 수신될 때까지 루프를 종료합니다.
            latency = utils.get_short_data(self.conn)
            # print(f"monitor client get latency : {latency} MB/s ")
            if latency is not None:
                self.bandwidth_value.value = latency

            time.sleep(1)
        except ConnectionRefusedError:
            print("[Errno 61] Connection refused, try again.")
            pass
                

    def schedular(self):
        # 타이밍 메커니즘을 사용하여 일정 기간 후 대역폭 모니터링
        # 스케줄러 만들기
        scheduler = BlockingScheduler()

        # 작업 추가
        scheduler.add_job(self.start_client, 'interval', seconds=self.interval, id='get_server_status')
        scheduler.start()


    def run(self) -> None:
        self.schedular()
        # self.start_client()


# if __name__ == '__main__':
#     ip = "127.0.0.1"
#     bandwidth_value = multiprocessing.Value('d', 0.0)
#     monitor_cli = MonitorClient(ip=ip, bandwidth_value=bandwidth_value)
#
#     monitor_cli.start()
#     monitor_cli.join()