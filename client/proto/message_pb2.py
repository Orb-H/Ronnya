# -*- coding: utf-8 -*-
# Generated by the protocol buffer compiler.  DO NOT EDIT!
# source: message.proto
# Protobuf Python Version: 4.25.3
"""Generated protocol buffer code."""
from google.protobuf import descriptor as _descriptor
from google.protobuf import descriptor_pool as _descriptor_pool
from google.protobuf import symbol_database as _symbol_database
from google.protobuf.internal import builder as _builder
# @@protoc_insertion_point(imports)

_sym_db = _symbol_database.Default()




DESCRIPTOR = _descriptor_pool.Default().AddSerializedFile(b'\n\rmessage.proto\"/\n\x07Request\x12\x0b\n\x03\x66id\x18\x01 \x01(\t\x12\x17\n\x06server\x18\x02 \x01(\x0e\x32\x07.Server\"\xa0\x01\n\x08Response\x12\x15\n\x05\x65rror\x18\x01 \x01(\x0b\x32\x06.Error\x12\x0b\n\x03\x66id\x18\x02 \x01(\t\x12\x17\n\x06server\x18\x03 \x01(\x0e\x32\x07.Server\x12\x0b\n\x03uid\x18\x04 \x01(\t\x12\x0c\n\x04name\x18\x05 \x01(\t\x12\r\n\x05rank4\x18\x06 \x01(\r\x12\x0e\n\x06score4\x18\x07 \x01(\r\x12\r\n\x05rank3\x18\x08 \x01(\r\x12\x0e\n\x06score3\x18\t \x01(\r\"&\n\x05\x45rror\x12\x0c\n\x04\x63ode\x18\x01 \x01(\r\x12\x0f\n\x07message\x18\x02 \x01(\t*\x18\n\x06Server\x12\x06\n\x02JP\x10\x00\x12\x06\n\x02US\x10\x01\x62\x06proto3')

_globals = globals()
_builder.BuildMessageAndEnumDescriptors(DESCRIPTOR, _globals)
_builder.BuildTopDescriptorsAndMessages(DESCRIPTOR, 'message_pb2', _globals)
if _descriptor._USE_C_DESCRIPTORS == False:
  DESCRIPTOR._options = None
  _globals['_SERVER']._serialized_start=269
  _globals['_SERVER']._serialized_end=293
  _globals['_REQUEST']._serialized_start=17
  _globals['_REQUEST']._serialized_end=64
  _globals['_RESPONSE']._serialized_start=67
  _globals['_RESPONSE']._serialized_end=227
  _globals['_ERROR']._serialized_start=229
  _globals['_ERROR']._serialized_end=267
# @@protoc_insertion_point(module_scope)