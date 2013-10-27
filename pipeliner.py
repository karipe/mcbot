# -*- coding: utf-8 -*-

from socket import *
import sys, subprocess
from threading  import Thread

from Queue import Queue, Empty

ON_POSIX = 'posix' in sys.builtin_module_names

cmd = sys.argv[1:]

args = subprocess.Popen(cmd, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, bufsize=1)
que = Queue()

_stdin = args.stdin

def enqueue_output(out, queue):
    while True:
        data = out.readline()
        if data:
            queue.put(data)

t1 = Thread(target=enqueue_output, args=(args.stdout, que))
t2 = Thread(target=enqueue_output, args=(args.stderr, que))
t1.daemon = True
t1.start()
t2.daemon = True
t2.start()

s = socket(AF_INET, SOCK_DGRAM)
s.bind(('0.0.0.0', 25560))
s.setblocking(0)

while True:
    # SEND_PART

    messages = ''
    while True:
        try:
            messages += que.get_nowait()
        except Empty:
            break

    if messages:
        for message in messages.split("\n"):
            if not message:
                continue
            print message
            s.sendto(message, ('127.0.0.1', 25561))

    # RECV_PART
    try:
        recv, addr = s.recvfrom(65536)
    except error:
        recv = ""

    if recv:
        for message in recv.split("\n"):
            if not message:
                continue
            _stdin.write(message + "\n")
            _stdin.flush()
            print message

