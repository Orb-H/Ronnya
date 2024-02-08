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

def info_to_str(info: dict):
    """
    process user info data

    Args:
        info (dict): user info from mahjong soul server

    Returns:
        str: str type data of processed user info
    """
    essential_info = ["account_id","nickname","level","level3"]
    post_info = {}
    for key in essential_info:
        post_info[key] = info[key]
    del post_info["level"]["_type_"]
    del post_info["level3"]["_type_"]
    return str(post_info)

async def main():
    #작혼 서버 연결
    try:
        #TODO : 임시로 등록. 나중에 환경변수화 예정
        #worker의 uid, token, 서버 주소 가져와야함
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

        ###############아래는 받은 데이터를 처리하는 부분
        fid = msg.pop()

        user_info = await client.find_user(fid)
        user_info = info_to_str(user_info)

        msg.append(user_info.encode())
        ###############

        worker.send_multipart(msg) #데이터 송신


if __name__ == "__main__":
    asyncio.run(main())