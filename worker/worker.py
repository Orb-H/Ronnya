'''
ronnya by Orb-H, omija_tea

Summary:
router로부터 받은 uid를 통해 작혼서버와 통신. 이후 처리된 데이터를 다시 router에게 전송

TODO:
1. 테스트용임. 다양한 방면에서 고쳐야함
'''

import os
import zmq
import logging
import sys
import asyncio
from modules import web_socket_client
from random import randint

SV_ROUTER_BACK = "tcp://localhost:5556"
LRU_READY = "\x01"

async def main():
    #작혼 서버 연결
    try:
        #TODO : 임시로 등록. 나중에 환경변수화 예정

        #TODO : 임시로 등록. 나중에 환경변수화 예정
        
        uid = os.getenv('ronnya_uid')
        token = os.getenv('ronnya_token')
        
        client = web_socket_client.WebSocketClient()
        await client.connect()
        await client.login(token, uid, 8)
        logging.info("mahjong server connection succeed")
    except:
        logging.critical("mahjong server connection failed")
        sys.exit(0)
    #zmq 소켓 설정 및 connect
    try:
        context = zmq.Context(1)
        worker = context.socket(zmq.REQ)
        identity = "%04X-%04X" % (randint(0, 0x10000), randint(0,0x10000))
        worker.setsockopt_string(zmq.IDENTITY, identity)
        worker.connect(SV_ROUTER_BACK)
        worker.send_string(LRU_READY) #worker 등록
        logging.info("zmq connection succeed")
    except:
        logging.critical("zmq connection failed")
        sys.exit(0)
    print("worker on")
    while True:
        msg = worker.recv_multipart() #데이터 수신
        if not msg:
            break

        ###############아래는 받은 데이터를 처리하는 부분. 현재는 *2해서 반환하는 예제로 작성함
        data = int(msg.pop())
        data = data*2
        msg.append(str(data).encode())
        ###############
        
        worker.send_multipart(msg) #데이터 송신
    

if __name__ == "__main__":
    asyncio.run(main())