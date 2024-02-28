"""
ronnya by Orb-H, omija_tea

Summary:
Cherry-picked version of universal utility file for message handling. Cherry-picked only the functions needed for the router module.
"""

#############################################################
# default
from . import message_pb2

# for debugging mode(use main function in web_socket_client.py)
# import message_pb2
#############################################################

ENUM_TO_SERVER_NAME = {message_pb2.Server.JP: "jp", message_pb2.Server.US: "us"}


def unwrap_request(msg: bytes) -> dict:
    request = message_pb2.Request()
    request.ParseFromString(msg)

    res = {
        "fid": request.fid,
        "server": ENUM_TO_SERVER_NAME[request.server],
    }
    return res
