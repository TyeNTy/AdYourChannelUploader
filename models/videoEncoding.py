from utils.extendedEnum import ExtendedEnum

class Resolution(ExtendedEnum):
    RES_1080_60 = "1080p60"
    RES_1080_30 = "1080p30"
    RES_720_60 = "720p60"
    RES_720_30 = "720p30"
    RES_480_60 = "480p60"
    RES_480_30 = "480p30"
    HIGH = "high"
    BEST = "best"

class Encoding:
    def __init__(self, resolution : Resolution, bitRate : int, possibleFrameRates : list[int], keyFrameSec : int) -> None:
        self.resolution = resolution
        self.bitRate = bitRate
        self.possibleFrameRates = possibleFrameRates
        self.keyFrameSec = keyFrameSec

class VideoEncoding(ExtendedEnum):
    ENCODING_1080_60 = Encoding(Resolution.RES_1080_60, 6000, [60, 50], 2)
    ENCODING_1080_30 = Encoding(Resolution.RES_1080_30, 4500, [30, 25], 2)
    ENCODING_720_60 = Encoding(Resolution.RES_720_60, 4000, [60, 50], 2)
    ENCODING_720_30 = Encoding(Resolution.RES_720_30, 2500, [30, 25], 2)
    
    def getEncoding(resolution : str) -> Encoding:
        if resolution == Resolution.RES_1080_60.value:
            return VideoEncoding.ENCODING_1080_60.value
        elif resolution == Resolution.RES_1080_30.value:
            return VideoEncoding.ENCODING_1080_30.value
        elif resolution == Resolution.RES_720_60.value:
            return VideoEncoding.ENCODING_720_60.value
        elif resolution == Resolution.RES_720_30.value:
            return VideoEncoding.ENCODING_720_30.value
        else:
            raise Exception("Unknown resolution")