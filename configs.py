import os

SOCKET_SERVER = "127.0.0.1"  # Server ip-address
SOCKET_PORT = 8000  # Server Port
SOCKET_URL = "ws://{0}/ws/openface-stream/".format(SOCKET_SERVER).format(":").format(SOCKET_PORT)

PROTOCOLS = ['rtsp', 'mjpg']
PROTOCOL_USED = PROTOCOLS[0]

if PROTOCOL_USED == PROTOCOLS[0]:
    # rtsp://admin:AVdev0021@192.168.1.64:554
    USERNAME, PASSWORD = "admin", "AVdev0021"
    IP_CAM_URL = "rtsp://{}:{}@192.168.1.64:554".format(USERNAME, PASSWORD)
else:
    # http://admin:admin@192.168.1.101/video.mjpg?mute
    IP_CAM_URL = "http://192.168.1.101/video.mjpg?mute"
    USERNAME, PASSWORD = "admin", "admin"

RTSP_DROP_FRAME_LIMIT = 10

SLEEP_SECONDS = 0  # in seconds
SEND_ONCE_IN_TIME = 1  # in seconds

WAIT_AFTER_SUCCESS = 10  # in seconds

SLEEP_FOR_NEW_TRY_CONNECTION = 3  # in seconds

CHUNK_SIZE = 1024

NOT_RECOGNIZED = "Not recognized!"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGGING_FILE = os.path.join(BASE_DIR, 'debug.log')
