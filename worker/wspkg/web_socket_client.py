import asyncio
import aioconsole
import websockets
import datetime
import os
import uuid
import logging
import threading

#############################################################
#default
from . import getData
from . import lq_proto_util
from . import lq_proto_pb2

#for debugging mode(use main function)
# import lq_proto_util
# import lq_proto_pb2
# import getData
#############################################################
LANG = "jp"


class WebSocketClientError(Exception):
    def __init__(
        self, message: str, is_critical: bool, data: dict | None, *args: object
    ):
        super().__init__(*args)
        self.message: str = message
        self.is_critical: bool = is_critical
        self.data: dict = data if data is not None else {}

    def __str__(self) -> str:
        return self.message

    def __getitem__(self, key):
        return self.data[key]


class WebSocketClientInitError(WebSocketClientError):
    def __init__(self, message: str, *args: object):
        super().__init__(message, True, None, *args)


class WebSocketClientLoginError(WebSocketClientError):
    def __init__(self, message: str, login_info: dict, *args: object):
        super().__init__(message, True, {"login_info": login_info}, *args)


class WebSocketClientFindUserError(WebSocketClientError):
    def __init__(self, message: str, login_info: dict, user_info: dict, *args: object):
        super().__init__(
            message, False, {"login_info": login_info, "user_info": user_info}, *args
        )



class WebSocketClient:
    class HeatbeatTimer:
        def __init__(self, func, log):
            self.keep_sending = False
            self.func = func
            self.log = log
            self.task = None

        def start(self):
            self.keep_sending = True
            self.task = asyncio.create_task(self.callback(), name="heatbeat")
            asyncio.shield(self.task)

        def stop(self):
            self.task.cancel()
            self.keep_sending = False

        async def callback(self):
            while True:
                await asyncio.sleep(360)
                await self.func()
                self.log("Heatbeat sent\n> ", end="")

    def __init__(self):
        self.index = 1
        self.lock = threading.Lock()

        if os.path.isfile(".ws_client.lock"):
            raise WebSocketClientInitError("Other instance already running...")

        self.file = open(".ws_client.lock", "w")

    async def connect(self):
        self.client = await websockets.connect(
            os.getenv("_".join(["ws_server_addr", LANG]))
        )
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
        return ""

    async def send_heatbeat(self):
        return await self.send_type_msg({"no_operation_counter": 0}, "heatbeat")

    async def send_oauth2auth_msg(
        self, login_type: int, code: str, uid: str, version_str: str
    ) -> dict:
        return await self.send_type_msg(
            {
                "type": login_type,
                "code": code,
                "uid": uid,
                "client_version_string": version_str,
            },
            "oauth2Auth",
        )

    async def send_oauth2check_msg(self, login_type: int, access_token: str) -> dict:
        return await self.send_type_msg(
            {"type": login_type, "access_token": access_token}, "oauth2Check"
        )

    async def send_oauth2login_msg(
        self, login_type: int, access_token: str, version: str, version_str: str
    ):
        deviceInfo = lq_proto_pb2.ClientDeviceInfo(
            **{
                "platform": "pc",
                "hardware": "pc",
                "os": "windows",
                "os_version": "win10",
                "is_browser": True,
                "software": "Chrome",
                "sale_platform": "web",
            }
        )
        versionInfo = lq_proto_pb2.ClientVersionInfo(**{"resource": version})
        request = lq_proto_pb2.ReqOauth2Login(
            **{
                "type": login_type,
                "access_token": access_token,
                "reconnect": False,
                "device": deviceInfo,
                "random_key": str(uuid.uuid4()),
                "client_version": versionInfo,
                "client_version_string": version_str,
                "currency_platforms": [],
            }
        )
        response = await self.send_msg(
            request.SerializeToString(), ".lq.Lobby.oauth2Login"
        )
        return lq_proto_util.unwrap_msg(response, "ResLogin")

    async def login(self, token: str, uid: str, login_type: int) -> bool:
        # LOGIN: OAuth2Auth -> OAuth2Check -> OAuth2Login
        code = getData.GetToken(uid, token)['accessToken']
        version = getData.GetVersion()['version']
        version_str = 'web-' + '.'.join(version.split('.')[:-1])

        self.login_info = {
            "token": token,
            "type": login_type,
            "code": code,
            "uid": uid,
            "client_version_string": version_str,
        }

        self.log('Send Oauth2Auth')
        response = await self.send_oauth2auth_msg(8, code, uid, version_str)

        if 'access_token' not in response.keys():
            raise WebSocketClientLoginError('Oauth2Auth Failed', self.login_info)
        access_token = response['access_token']
        self.login_info['access_token'] = access_token
        self.log('Done Oauth2Auth: access_token = ' + access_token)


        self.log("Send Oauth2Check")
        response = await self.send_oauth2check_msg(login_type, access_token)

        if 'has_account' not in response.keys():
            raise WebSocketClientLoginError('Oauth2Check Failed', self.login_info)
        has_account = response['has_account']
        self.log('Done Oauth2Check: has_account = ' + str(has_account))

        if not has_account:
            raise WebSocketClientLoginError('No account found with given uid', self.login_info)

        self.log('Send Oauth2Login')
        response = await self.send_oauth2login_msg(login_type, access_token, version, version_str)

        if 'account_id' not in response.keys():
            raise WebSocketClientLoginError('Oauth2Login Failed', self.login_info)


        self.log("Done Oauth2Login")

    async def send_searchaccountbypattern_msg(self, fid: str) -> dict:
        return await self.send_type_msg(
            {"search_next": False, "pattern": fid}, "searchAccountByPattern"
        )

    async def send_fetchmultiaccountbrief_msg(self, uid: int) -> dict:
        request = lq_proto_pb2.ReqMultiAccountId(**{"account_id_list": [uid]})
        response = await self.send_msg(
            request.SerializeToString(), ".lq.Lobby.fetchMultiAccountBrief"
        )
        return lq_proto_util.unwrap_msg(response, "ResMultiAccountBrief")

    async def find_user(self, fid: str) -> dict:
        # INFO_QUERY: searchAccountByPattern -> fetchMultiAccountBrief
        self.log("Send SearchAccountByPattern")
        response = await self.send_searchaccountbypattern_msg(fid)

        user_info = {
            "fid": fid
        }

        if response['decode_id'] == 0:
            raise WebSocketClientFindUserError('No account found', self.login_info, user_info)
        uid = response['decode_id']
        user_info['uid'] = uid
        self.log('Done SearchAccountByPattern: decode_id = ' + str(uid))


        self.log("Send FetchMultiAccountBrief")
        response = await self.send_fetchmultiaccountbrief_msg(uid)

        if 'players' not in response.keys():
            raise WebSocketClientFindUserError('No user information found', self.login_info, user_info)
        self.log('Done FetchMultiAccountBrief: user information ↓')

        info = response['players'][0]

        self.log(str(info))
        return info

    async def close(self):
        self.file.close()
        os.remove(".ws_client.lock")
        self.ht.stop()
        return await self.client.close()

    def log(self, msg: str, **print_options) -> None:
        logging.info("[" + datetime.datetime.now().isoformat() + "] " + msg)


async def main():
    print("----- Manual Mode -----")
    print("Enter fid to find user, leave blank to quit")
    try:
        uid = os.getenv("_".join(["ronnya_uid", LANG]))
        token = os.getenv("_".join(["ronnya_token", LANG]))

        client = WebSocketClient()
        print("Intialize connection")
        await client.connect()
        print("First heatbeat complete")

        print("Attempt to login")
        await client.login(token, uid, 8)

        while True:
            fid = await aioconsole.ainput("> ")
            if len(fid) == 0:
                break
            try:
                print((await client.find_user(fid))["nickname"])
            except Exception as e:
                print(type(e))
                print(e.args)
        await client.close()
    except Exception as e:
        print(type(e))
        print(e.args)
        print(e)


if __name__ == "__main__":
    asyncio.run(main())