import json
import requests
import socket


def load_config(filename):
    config = {}
    with open(filename, 'r', encoding='utf-8') as f:
        config = json.load(f)

    return config


def get_ip():
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('pwnbit.kr', 443))
    
    internal_ip = sock.getsockname()[0]
    external_ip = requests.get('http://ip.jsontest.com').json()['ip']

    return internal_ip, external_ip

