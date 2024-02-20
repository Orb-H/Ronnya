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

if not os.environ.get('IN_CONTAINER'):
    from dotenv import load_dotenv
    BASE_DIR = os.path.dirname(os.path.abspath(__file__))
    load_dotenv(os.path.join(BASE_DIR, ".env.client.dev"))

ZMQ_ROUTER_FRONT = os.getenv("ZMQ_ROUTER_FRONT")
REQUEST_TIMEOUT = 3000

app = Flask(__name__)

@app.route('/request/<server>/<fid>')
def handle_fid(server, fid):
    '''
    fid를 받아서 zmq통신 후 결과 반환
    '''
    global client
    client.send_string(str(fid)) #fid 정보 송신
    if (client.poll(REQUEST_TIMEOUT) & zmq.POLLIN) != 0: #정보 수신
        reply = client.recv()
        return reply

if __name__=="__main__":
    #zmq socket 선언 후 연결
    context = zmq.Context()
    client = context.socket(zmq.REQ)
    client.connect(ZMQ_ROUTER_FRONT)
    
    app.run(host="0.0.0.0", port=5000) #플라스크 서버 구동