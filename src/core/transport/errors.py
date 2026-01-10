from __future__ import annotations


class TransportError(Exception):
    """传输层基础异常。"""


class ValidationError(TransportError):
    """入站消息校验失败。"""


class DuplicateMessageError(TransportError):
    """检测到入站重复消息。"""


class RoutingError(TransportError):
    """路由缺失或处理失败。"""


class SenderNotFoundError(TransportError):
    """出站频道未注册发送器。"""
