"""
ronnya by Orb-H, omija_tea

Summary:
Universal utility file for message handling. May be used by cherry-picking functions as needed according to functionality of module. e.g. wrap_request, unwrap_response for front / wrap_response, unwrap_request for worker
"""

#############################################################
# default
from . import message_pb2

# for debugging mode(use main function in web_socket_client.py)
# import message_pb2
#############################################################

SERVER_NAME_TO_ENUM = {"jp": message_pb2.Server.JP, "us": message_pb2.Server.US}
ENUM_TO_SERVER_NAME = {message_pb2.Server.JP: "jp", message_pb2.Server.US: "us"}


def wrap_request(fid: str, server: str) -> bytes:
    request = message_pb2.Request()
    request.fid = fid
    if server not in SERVER_NAME_TO_ENUM:
        raise ValueError("Invalid server")
    request.server = SERVER_NAME_TO_ENUM[server]
    return request.SerializeToString()


def unwrap_request(msg: bytes) -> dict:
    request = message_pb2.Request()
    request.ParseFromString(msg)

    res = {
        "fid": request.fid,
        "server": ENUM_TO_SERVER_NAME[request.server],
    }
    return res


def wrap_response(fid: str, server: str, data: dict) -> bytes:
    response = message_pb2.Response(**data)
    response.fid = fid
    if server not in SERVER_NAME_TO_ENUM:
        raise ValueError("Invalid server")
    response.server = SERVER_NAME_TO_ENUM[server]
    return response.SerializeToString()


def wrap_response_error(fid: str, server: str, code: int, message: str) -> bytes:
    response = message_pb2.Response()
    response.fid = fid
    if server not in SERVER_NAME_TO_ENUM:
        raise ValueError("Invalid server")
    response.server = SERVER_NAME_TO_ENUM[server]

    response.error.code = code
    response.error.message = message
    return response.SerializeToString()


def unwrap_response(msg: bytes) -> dict:
    response = message_pb2.Response()
    response.ParseFromString(msg)

    keys = ["uid", "name", "rank4", "score4", "rank3", "score3"]
    res = {
        "fid": response.fid,
        "server": ENUM_TO_SERVER_NAME[response.server],
    }

    if response.error.code != 0:
        res["error"] = {
            "code": response.error.code,
            "message": response.error.message,
        }
        return res
    else:
        for key in keys:
            res[key] = response.__getattribute__(key)
        return res
