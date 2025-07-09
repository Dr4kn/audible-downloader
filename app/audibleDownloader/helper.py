
from enum import Enum

class Status(Enum):
    ERROR = -1
    NOT_DOWNLOADED = 0
    DOWNLOADED = 1
    CONVERTED = 2
    MOVED = 3