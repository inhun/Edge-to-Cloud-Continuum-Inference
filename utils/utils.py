import socket
import time
import pickle
import torch
import platform
import speedtest as spt

def get_socket_server(ip, port, max_client_num=10):
    """
    클라이언트가 연결되기를 기다리는 서버-클라우드 장치용 소켓 생성
    :param ip: 클라우드 장치 머신의 ip
    :param port: 소켓의 네트워크 포트
    :param max_client_num: 접속 가능한 최대 사용자 수
    :return: 생성된 소켓
    """
    socket_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)  # 소켓 생성

    # 사용 중인 플랫폼 확인
    sys_platform = platform.platform().lower()
    if "windows" in sys_platform:
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)  # windows
    else:
        socket_server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEPORT, 1) # macos or linux

    socket_server.bind((ip, port))  # 바인드 포트 번호
    socket_server.listen(max_client_num)  # 오픈 모니터
    return socket_server


def get_socket_client(ip, port):
    """
    클라이언트(에지 장치)는 클라우드 장치에 연결하기 위한 소켓을 생성합니다.
    :param ip: 연결할 클라우드 디바이스 머신의 ip
    :param port: 클라우드 장치 소켓의 포트
    :return: 생성된 연결
    """
    conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conn.connect((ip, port))
    return conn


def close_conn(conn):
    """
    에지 장치가 conn 연결을 종료합니다.
    :param conn: 연결 연결
    :return: 연결 종료
    """
    conn.close()



def close_socket(p):
    """
    클라우드 장치 닫기 소켓
    :param p: 소켓
    :return: 연결을 닫습니다.
    """
    p.close()


def wait_client(p):
    """
    conn 연결을 기다리는 중
    :param p: 소켓
    :반품:
    """
    conn, client = p.accept()
    print(f"successfully connection :{conn}")
    return conn,client


def send_data(conn, x, msg="msg", show=True):
    """
    DNN 모델의 중간층에서 생성된 텐서와 같이 더 긴 데이터를 상대방에게 전송
    참고: 데이터를 수신하려면 get_data 함수를 사용해야 합니다.
    이 send_data 메시지는 주로 데이터 길이 전송 - 응답 수신 - 실제 데이터 전송 - 응답 수신으로 나뉩니다.
    :param conn: 클라이언트의 conn 연결
    :param x: 보낼 데이터
    :param msg: 해당 프롬프트
    :param show: 데이터 통신 메시지 표시 여부
    :반품:
    """
    send_x = pickle.dumps(x)
    conn.sendall(pickle.dumps(len(send_x)))
    resp_len = conn.recv(1024).decode()


    conn.sendall(send_x)
    resp_data = conn.recv(1024).decode()
    if show:
        print(f"get {resp_data} , {msg} has been sent successfully")  # 상대방이 데이터를 수신했음을 나타냅니다.



def send_short_data(conn, x, msg="msg", show=True):
    """ 비교적 짧은 데이터를 상대방에게 보내고 get_short_data를 사용하여 직접 데이터 받기"""
    send_x = pickle.dumps(x)
    conn.sendall(send_x)
    if show:
        print(f"short message , {msg} has been sent successfully")  # 상대방이 데이터를 수신했음을 나타냅니다.



def get_data(conn):
    """
    긴 데이터 획득은 크게 데이터 길이 획득 - 응답 - 데이터 획득 - 응답으로 나뉩니다.
    :param conn: 설정된 연결
    :return: 구문 분석된 데이터 및 데이터 소비를 가져오는 지연
    """
    # 수신 데이터 길이
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


def get_short_data(conn):
    """ 짧은 데이터 가져오기"""
    return pickle.loads(conn.recv(1024))


def get_bandwidth():
    """
    현재 네트워크 대역폭 가져오기
    :return: 네트워크 대역폭 MB/s
    """
    print("네트워크 대역폭을 확보하는 중입니다. 잠시 기다려 주세요....")
    spd = spt.Speedtest(secure=True)
    spd.get_best_server()

    # download = int(spd.download() / 1024 / 1024)
    upload = int(spd.upload() / 1024 / 1024)

    # print(f'현재 다운로드 속도는 다음과 같습니다: {str(download)} MB/s')
    print(f'현재 업로드 속도는 다음과 같습니다. {str(upload)} MB/s')
    return upload


def get_speed(network_type,bandwidth):
    """
    speed_type에 따라 네트워크 대역폭 확보
    :param network_type: 3g lte 또는 와이파이
    :param 대역폭은 네트워크 속도에 해당합니다. 3g 단위는 KB/s lte이고 wifi 단위는 MB/s입니다.
    :return: 대역폭 속도 단위: Bpms bytes_per_ms 전송 가능한 바이트 수(밀리초)
    """
    transfer_from_MB_to_B = 1024 * 1024
    transfer_from_KB_to_B = 1024

    if network_type == "3g":
        return bandwidth * transfer_from_KB_to_B / 1000
    elif network_type == "lte" or network_type == "wifi":
        return bandwidth * transfer_from_MB_to_B / 1000
    else:
        raise RuntimeError(f"현재 지원되지 않는 network type - {network_type}")


def create_server(p):
    """
    소켓을 사용하여 서버 만들기 - 클라이언트가 루프에서 요청을 보낼 때까지 기다립니다.
    일반적으로 테스트용으로만 사용됨
    :param p: 소켓 연결
    :반환: 없음
    """
    while True:
        conn, client = p.accept()  # 접수된 클라이언트 요청
        print(f"connect with client :{conn} successfully ")

        sum_time = 0.0
        # 메시지 보내기 및 받기
        data = [conn.recv(1)]  # 보다 정확하게 시간을 기록하기 위해 먼저 길이가 1인 메시지를 얻은 다음 타이밍을 시작합니다.
        while True:
            start_time = time.perf_counter()  # 녹음 시작 시간
            packet = conn.recv(1024)
            end_time = time.perf_counter()  # 기록 종료 시간
            transport_time = (end_time - start_time) * 1000
            sum_time += transport_time  # 전송 시간은 sum_time 변수에 누적됩니다.

            data.append(packet)
            if len(packet) < 1024:  # 길이 < 1024는 모든 데이터가 승인되었음을 의미합니다.
                break

        parse_data = pickle.loads(b"".join(data))  # 송수신 데이터 모두 pickle 패키지를 사용하므로 여기에서 pickle을 구문 분석합니다.
        print(f"get all data come from :{conn} successfully ")

        if torch.is_tensor(parse_data):  # 주로 텐서 데이터의 데이터 크기 측정
            total_num = 1
            for num in parse_data.shape:
                total_num += num
            data_size = total_num * 4
        else:
            data_size = 0.0

        print(f"data size(bytes) : {data_size} \t transfer time : {sum_time:.3} ms")
        print("=====================================")
        conn.send("yes".encode("UTF-8"))  # 모든 요청을 받은 후 고객에게 회신
        conn.close()


def show_speed(data_size,actual_latency,speed_Bpms):
    """
    비교하려고:
    (1) iperf 실제 대역폭과 예상 대역폭
    (2) 공식에 따라 계산된 실제 전송 지연과 예상 전송 지연
    일반적으로 테스트용으로만 사용됨
    :param data_size: 데이터 크기 - 바이트
    :param actual_latency: 실제 전송 지연
    :param speed_Bpms: iperf에서 얻은 실제 대역폭
    :return: 디스플레이 비교는 비교 결과와 유사해야 합니다.
    """
    print(f"actual speed : {speed_Bpms:.3f} B/ms")  # iperf가 확보한 대역폭
    print(f"predicted speed : {(data_size/actual_latency):.3f} B/ms")  # 데이터 크기와 실제 전송 시간으로 계산된 대역폭
    print(f"actual latency for {data_size} bytes : {actual_latency:.3f} ms")  # 실제 기록된 대기 시간
    print(f"predicted latency for {data_size} bytes : {(data_size / speed_Bpms):.3f} ms")  # iperf 대역폭으로 예측되는 대기 시간