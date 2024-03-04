'''
ronnya by Orb-H, omija_tea

Summary:
유저로부터 uid를 입력받아서 router에게 넘김. 이후 돌아온 요청을 유저에게 송신

TODO:
1. 로깅
2. 타임아웃 처리
3. robustness강화(연결 끊겼을때 재생성)
4. production 환경으로 전환
5. 등등... 테스트용임
'''
from flask import Flask
import zmq
import os
import datetime

from dbpkg.ronnyaDB import RonnyaDB
from proto import message_util

if not os.environ.get('IN_CONTAINER'):
    from dotenv import load_dotenv
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(BASE_DIR, ".env.client.dev"))

ZMQ_ROUTER_FRONT = os.getenv("ZMQ_ROUTER_FRONT")
REQUEST_TIMEOUT = 3000
SERVERS = ["jp", "us"]

app = Flask(__name__)

@app.route("/request/<any(" + ",".join(SERVERS) + "):server>/<fid>")
def handle_fid(server, fid):
    '''
    fid를 받아서 zmq통신 후 결과 반환
    '''
    global client, ronnyadb

    current_data = ronnyadb.read_data(fid, server)
    if current_data != None:
        if (datetime.datetime.now() - current_data["last_update"]).total_seconds() < 600: # 10분, 추후 확정하면 수정
            current_data.pop("uid")
            return current_data

    msg = message_util.wrap_request(fid, server) # TODO: test needed
    client.send_string(msg)

    if (client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0: #정보 수신
        reply = client.recv()

        result = message_util.unwrap_response(reply) # TODO: test needed
        result = RonnyaDB.ws_to_db(result)
        ronnyadb.update_data(fid, result, server)
        result.pop("uid")
        return result
    else:
        return 500, "Server Operation Failed"

if __name__=="__main__":
    #zmq socket 선언 후 연결
    context = zmq.Context()
    client = context.socket(zmq.REQ)
    client.connect(ZMQ_ROUTER_FRONT)
    
    ronnyadb = RonnyaDB()

    app.run(host="0.0.0.0", port=5000) #플라스크 서버 구동