from init import initUploader
from sys import argv

def main(configuration: dict[str, str]) -> None:
    initUploader(configuration)

if __name__ == "__main__":
    configuration = {
        "DATABASE_CONNECTION_STRING": argv[1],
        "DATABASE_NAME": argv[2],
        "CLUSTER_NAME": argv[3],
        "GET_STREAM_ID": argv[4],
        "URL_CALL_BACK": argv[5],
        "APP_ID": argv[6],
        "APP_SECRET": argv[7],
        "STREAM_CHANNEL": argv[8],
        "LANGUAGE": argv[9],
    }
    main(configuration)