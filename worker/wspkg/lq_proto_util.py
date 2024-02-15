import json

#############################################################
#default
from . import lq_proto_pb2
lq = json.loads(''.join(open('wspkg/data/lq_proto.json').readlines()))['nested']

#for debugging mode(use main function in web_socket_client.py)
#import lq_proto_pb2
#lq = json.loads(''.join(open('data/lq_proto.json').readlines()))['nested']
#############################################################

lq = lq['lq']['nested']
fasttest = lq['FastTest']
lobby = lq['Lobby']


def get_types(type: str) -> list[str]:
    '''
    Args:
        type (str): Type of wrapper without prefix

    Returns:
        list[str]: Type of wrapper, request type of message, response type of message
    '''
    for k, v in lobby['methods'].items():
        if k == type:
            return '.lq.Lobby.' + type, v['requestType'], v['responseType']
    for k, v in fasttest['methods'].items():
        if k == type:
            return '.lq.FastTest.' + type, v['requestType'], v['responseType']
    return None


def to_dict(message: bytes, n: int = 0) -> dict:
    '''
    Args:
        msg (bytes): Serialized message
        n (int): Indent number for printing, not used

    Returns:
        dict: Deserialized content of message
    '''
    message_dict = {}

    for descriptor in message.DESCRIPTOR.fields:
        key = descriptor.name
        value = getattr(message, descriptor.name)
        # print('  ' * n + key, end='\t')

        if descriptor.label == descriptor.LABEL_REPEATED:
            message_list = []

            for sub_message in value:
                if descriptor.type == descriptor.TYPE_MESSAGE:
                    # print()
                    message_list.append(to_dict(sub_message, n + 1))
                    message_list[-1]['_type_'] = sub_message.DESCRIPTOR.name
                elif descriptor.type == descriptor.TYPE_BYTES:
                    # print()
                    if len(value) != 0:
                        wrapper = lq_proto_pb2.Wrapper()
                        wrapper.ParseFromString(value)
                        # print(wrapper.name, end='\t')
                        try:
                            d = getattr(
                                lq_proto_pb2, wrapper.name.split('.')[-1])()
                            d.ParseFromString(wrapper.data)
                            message_dict[key] = to_dict(d, n + 1)
                            message_dict[key]['_type_'] = wrapper.name
                        except:
                            message_dict[key] = str(value)
                else:
                    # print(sub_message, end='\t')
                    message_list.append(sub_message)

            # print()
            message_dict[key] = message_list
        else:
            if descriptor.type == descriptor.TYPE_MESSAGE:
                # print()
                message_dict[key] = to_dict(value, n + 1)
                message_dict[key]['_type_'] = value.DESCRIPTOR.name
            elif descriptor.type == descriptor.TYPE_BYTES:
                if len(value) != 0:
                    wrapper = lq_proto_pb2.Wrapper()
                    wrapper.ParseFromString(value)
                    # print(wrapper.name, end='\t')
                    try:
                        d = getattr(
                            lq_proto_pb2, wrapper.name.split('.')[-1])()
                        d.ParseFromString(wrapper.data)
                        message_dict[key] = to_dict(d, n + 1)
                        message_dict[key]['_type_'] = wrapper.name
                    except:
                        message_dict[key] = str(value)
            else:
                # print(value)
                message_dict[key] = value

    return message_dict


def wrap_root_msg(msg: bytes, type: str, idx: int) -> bytes:
    '''
    Args:
        msg (bytes): Serialized message
        type (str): Type of wrapper
        idx (int): Index number of this message

    Returns:
        bytes: Wrapped message. This is ready to be sent to the server.
    '''
    wrapper = lq_proto_pb2.Wrapper()
    wrapper.name = type
    wrapper.data = msg
    res = bytes([2, idx & 0xff, idx >> 8]) + wrapper.SerializeToString()
    return res


def wrap_msg(msg: dict, reqtype: str) -> bytes:
    '''
    Args:
        msg (dict): content of message to be sent
        reqtype (str): Request type of message

    Returns:
        bytes: Serialized message.
    '''
    Target = getattr(lq_proto_pb2, reqtype)
    wrapper = Target(**msg)
    return wrapper.SerializeToString()


def unwrap_root_msg(msg: bytes) -> bytes:
    '''
    Args:
        msg (bytes): Message received from the server

    Returns:
        bytes: Unwrapped message of the message. Should be deserialized to use.
    '''
    wrapper = lq_proto_pb2.Wrapper()
    wrapper.ParseFromString(msg[3:])
    return wrapper.data


def unwrap_msg(msg: bytes, restype: str) -> dict:
    '''
    Args:
        msg (bytes): Serialized message

    Returns:
        dict: Deserialized content of the message.
    '''
    Target = getattr(lq_proto_pb2, restype)
    wrapper = Target()
    wrapper.ParseFromString(msg)
    return to_dict(wrapper, 0)
