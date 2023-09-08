import subprocess as sp
import os
from threading import Thread , Timer
import sched, time
import torch

def get_gpu_memory():
    output_to_list = lambda x: x.decode('ascii').split('\n')[:-1]
    ACCEPTABLE_AVAILABLE_MEMORY = 1024
    COMMAND = "nvidia-smi --query-gpu=memory.used,memory.total --format=csv"
    try:
        memory_use_info = output_to_list(sp.check_output(COMMAND.split(),stderr=sp.STDOUT))[1:]
        print(output_to_list(sp.check_output(COMMAND.split(),stderr=sp.STDOUT)))
    except sp.CalledProcessError as e:
        raise RuntimeError("command '{}' return with error (code {}): {}".format(e.cmd, e.returncode, e.output))
    
    memory_use_values = [int(x.split()[0]) for i, x in enumerate(memory_use_info)]
    memory_total_values = [int(x.split()[2]) for i, x in enumerate(memory_use_info)]
    # print(memory_use_values)
    return memory_use_values, memory_total_values

def print_gpu_memory_every_5secs():
    """
        This function calls itself every 5 secs and print the gpu_memory.
    """
    Timer(5.0, print_gpu_memory_every_5secs).start()
    print(get_gpu_memory())


def get_gpu_info():
    if torch.cuda.is_available():
        print(torch.cuda.get_device_name(torch.cuda.current_device()))


print_gpu_memory_every_5secs()
get_gpu_info()