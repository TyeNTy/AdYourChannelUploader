from __future__ import annotations
from utils.extendedEnum import ExtendedEnum

class UploaderStatus(ExtendedEnum):
    INIT = "INIT"
    IDLE = "IDLE"
    STREAMING = "STREAMING"
    DELETING = "DELETING"
    
    def getStatus(status : str) -> UploaderStatus:
        if status == UploaderStatus.INIT.value:
            return UploaderStatus.INIT
        elif status == UploaderStatus.IDLE.value:
            return UploaderStatus.IDLE
        elif status == UploaderStatus.STREAMING.value:
            return UploaderStatus.STREAMING
        elif status == UploaderStatus.DELETING.value:
            return UploaderStatus.DELETING
        else:
            raise Exception("Unknown status")