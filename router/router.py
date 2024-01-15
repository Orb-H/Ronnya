'''
ronnya by Orb-H, omija_tea

Summary:
client와 worker사이를 중개

TODO:
1. 테스트용임. 다양한 방면에서 고쳐야함
'''

import zmq

SV_ROUTER_FRONT = "tcp://*:5555"
SV_ROUTER_BACK = "tcp://*:5556"
LRU_READY = "\x01"

if __name__ == "__main__":
    #zmq socket설정 및 bind
    context = zmq.Context(1)
    frontend = context.socket(zmq.ROUTER)
    backend = context.socket(zmq.ROUTER)
    frontend.bind(SV_ROUTER_FRONT)
    backend.bind(SV_ROUTER_BACK)

    #worker 초기 등록을 위한 Poller 선언
    poll_workers = zmq.Poller()
    poll_workers.register(backend, zmq.POLLIN)

    #데이터 송수신을 위한 Poller 선언
    poll_both = zmq.Poller()
    poll_both.register(frontend, zmq.POLLIN)
    poll_both.register(backend, zmq.POLLIN)
    
    print("server on")
    
    workers=[]
    while True:
        if workers:
            socks = dict(poll_both.poll())
        else:
            socks = dict(poll_workers.poll())

        # Handle worker activity on backend
        if socks.get(backend) == zmq.POLLIN:
            # Use worker address for LRU routing
            msg = backend.recv_multipart()
            if not msg:
                break
            address = msg[0]
            workers.append(address)

            # Everything after the second (delimiter) frame is reply
            reply = msg[2:]

            # Forward message to client if it's not a READY
            if reply[0] != LRU_READY:
                frontend.send_multipart(reply)

        if socks.get(frontend) == zmq.POLLIN:
            #  Get client request, route to first available worker
            msg = frontend.recv_multipart()
            request = [workers.pop(0), ''.encode()] + msg
            backend.send_multipart(request)