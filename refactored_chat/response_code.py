from enum import Enum, auto


class BadNickname(Exception):
    """Exception raised if the nickname is invalid"""
    pass


class ResponseCode(Enum):
    """Values used for the nickname verification protocol."""
    ACCEPTED = auto()
    REJECTED = auto()