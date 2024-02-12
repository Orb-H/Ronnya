import asyncio
import aioconsole
import websockets
import lq_proto_util
import lq_proto_pb2
import datetime
import os
import uuid
import logging

import threading

import getData


LANG = 'jp'

class WebSocketClient:
    class HeatbeatTimer:
        def __init__(self, func, log):
            self.keep_sending = False
            self.func = func
            self.log = log
            self.task = None

        def start(self):
            self.keep_sending = True
            self.task = asyncio.create_task(self.callback(), name='heatbeat')
            asyncio.shield(self.task)

        def stop(self):
            self.task.cancel()
            self.keep_sending = False

        async def callback(self):
            while True:
                await asyncio.sleep(360)
                await self.func()
                self.log('Heatbeat sent\n> ', end='')

    def __init__(self):
        self.index = 1
        self.lock = threading.Lock()

        assert not os.path.isfile('.ws_client.lock'), 'Other instance already running...'

        self.file = open('.ws_client.lock', 'w')

    async def connect(self):
        self.client = await websockets.connect(os.getenv('_'.join(['ws_server_addr', LANG])))
        self.ht = WebSocketClient.HeatbeatTimer(self.send_heatbeat, self.log)
        self.ht.start()
        return await self.send_heatbeat()

    async def send_msg(self, msg: bytes, type: str) -> bytes:
        wrapped = lq_proto_util.wrap_root_msg(msg, type, self.index)
        self.index += 1

        self.lock.acquire()
        await self.client.send(wrapped)
        resp = await self.client.recv()
        self.lock.release()

        unwrapped = lq_proto_util.unwrap_root_msg(resp)
        return unwrapped

    async def send_type_msg(self, msg: dict, type: str) -> bytes:
        types = lq_proto_util.get_types(type)
        msg = lq_proto_util.wrap_msg(msg, types[1])
        resp = await self.send_msg(msg, types[0])
        if len(resp) > 0:
            return lq_proto_util.unwrap_msg(resp, types[2])
        return ''

    async def send_heatbeat(self):
        return await self.send_type_msg({
            'no_operation_counter': 0
        }, 'heatbeat')

    async def send_oauth2auth_msg(self, login_type: int, code: str, uid: str, version_str: str) -> dict:
        return await self.send_type_msg({
            'type': login_type,
            'code': code,
            'uid': uid,
            'client_version_string': version_str
        }, 'oauth2Auth')

    async def send_oauth2check_msg(self, login_type: int, access_token: str) -> dict:
        return await self.send_type_msg({
            'type': login_type,
            'access_token': access_token
        }, 'oauth2Check')

    async def send_oauth2login_msg(self, login_type: int, access_token: str, version: str, version_str: str):
        deviceInfo = lq_proto_pb2.ClientDeviceInfo(**{
            'platform': 'pc',
            'hardware': 'pc',
            'os': 'windows',
            'os_version': 'win10',
            'is_browser': True,
            'software': 'Chrome',
            'sale_platform': 'web'
        })
        versionInfo = lq_proto_pb2.ClientVersionInfo(**{
            'resource': version
        })
        request = lq_proto_pb2.ReqOauth2Login(**{
            'type': login_type,
            'access_token': access_token,
            'reconnect': False,
            'device': deviceInfo,
            'random_key': str(uuid.uuid4()),
            'client_version': versionInfo,
            'client_version_string': version_str,
            'currency_platforms': []
        })
        response = await self.send_msg(request.SerializeToString(), '.lq.Lobby.oauth2Login')
        return lq_proto_util.unwrap_msg(response, 'ResLogin')

    async def login(self, token: str, uid: str, login_type: int) -> bool:
        # LOGIN: OAuth2Auth -> OAuth2Check -> OAuth2Login
        code = getData.GetToken(uid, token)['accessToken']
        version = getData.GetVersion()['version']
        version_str = 'web-' + '.'.join(version.split('.')[:-1])
        
        self.log('Send Oauth2Auth')
        response = await self.send_oauth2auth_msg(8, code, uid, version_str)
        assert 'access_token' in response.keys(), 'Oauth2Auth Failed'
        access_token = response['access_token']
        self.log('Done Oauth2Auth: access_token = ' + access_token)

        self.log('Send Oauth2Check')
        response = await self.send_oauth2check_msg(login_type, access_token)
        assert 'has_account' in response.keys(), 'Oauth2Check Failed'
        has_account = response['has_account']
        self.log('Done Oauth2Check: has_account = ' + str(has_account))
        assert has_account, ('No account found with uid ' + uid)

        self.log('Send Oauth2Login')
        response = await self.send_oauth2login_msg(login_type, access_token, version, version_str)
        assert 'account_id' in response.keys(), 'Oauth2Login Failed'

        self.log('Done Oauth2Login')

    async def send_searchaccountbypattern_msg(self, fid: str) -> dict:
        return await self.send_type_msg({
            'search_next': False,
            'pattern': fid
        }, 'searchAccountByPattern')

    async def send_fetchmultiaccountbrief_msg(self, uid: int) -> dict:
        request = lq_proto_pb2.ReqMultiAccountId(**{
            'account_id_list': [uid]
        })
        response = await self.send_msg(request.SerializeToString(), '.lq.Lobby.fetchMultiAccountBrief')
        return lq_proto_util.unwrap_msg(response, 'ResMultiAccountBrief')

    async def find_user(self, fid: str) -> dict:
        # INFO_QUERY: searchAccountByPattern -> fetchMultiAccountBrief
        self.log('Send SearchAccountByPattern')
        response = await self.send_searchaccountbypattern_msg(fid)
        assert response['decode_id'] != 0, 'No account found'
        uid = response['decode_id']
        self.log('Done SearchAccountByPattern: decode_id = ' + str(uid))

        self.log('Send FetchMultiAccountBrief')
        response = await self.send_fetchmultiaccountbrief_msg(uid)
        assert 'players' in response, 'No user information found'
        self.log('Done FetchMultiAccountBrief: user information ↓')


        info = response['players'][0]
        self.log(str(info))
        return info

    async def close(self):
        self.file.close()
        os.remove('.ws_client.lock')
        self.ht.stop()
        return await self.client.close()

    def log(self, msg: str, **print_options) -> None:
        logging.info("[" + datetime.datetime.now().isoformat() + "] " + msg)


async def main():
    print('----- Manual Mode -----')
    print('Enter fid to find user, leave blank to quit')
    try:
        uid = os.getenv('_'.join(['ronnya_uid', LANG]))
        token = os.getenv('_'.join(['ronnya_token', LANG]))

        client = WebSocketClient()
        print('Intialize connection')
        await client.connect()
        print('First heatbeat complete')

        print('Attempt to login')
        await client.login(token, uid, 8)

        while True:
            fid = await aioconsole.ainput('> ')
            if len(fid) == 0:
                break
            print((await client.find_user(fid))['nickname'])
        await client.close()
    except Exception as e:
        print(type(e))
        print(e.args)
        print(e)

if __name__ == "__main__":
    asyncio.run(main())
