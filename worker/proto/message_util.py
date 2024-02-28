"""
ronnya by Orb-H, omija_tea

Summary:
Cherry-picked version of universal utility file for message handling. Cherry-picked only the functions needed for the worker module.
"""

#############################################################
# default
from . import message_pb2

# for debugging mode(use main function in web_socket_client.py)
# import message_pb2
#############################################################

SERVER_NAME_TO_ENUM = {"jp": message_pb2.Server.JP, "us": message_pb2.Server.US}
ENUM_TO_SERVER_NAME = {message_pb2.Server.JP: "jp", message_pb2.Server.US: "us"}


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
