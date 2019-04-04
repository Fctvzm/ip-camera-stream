import os

SOCKET_SERVER = "127.0.0.1"  # Server ip-address
SOCKET_PORT = 8000  # Server Port
SOCKET_URL = "ws://{0}/ws/openface-stream/".format(SOCKET_SERVER).format(":").format(SOCKET_PORT)

PROTOCOLS = ['rtsp', 'mjpg']
PROTOCOL_USED = PROTOCOLS

# rtsp://admin:AVdev0021@192.168.1.64:554
RTSP_USERNAME, RTSP_PASSWORD = "admin", "AVdev0021"
RTSP_IP_CAM_URL = "rtsp://{}:{}@192.168.1.64:554".format(RTSP_USERNAME, RTSP_PASSWORD)

# http://admin:admin@192.168.1.101/video.mjpg?mute
MJPG_IP_CAM_URL = "http://192.168.1.101/video.mjpg?mute"
MJPG_USERNAME, MJPG_PASSWORD = "admin", "admin"

SLEEP_SECONDS = 0  # in seconds
SEND_ONCE_IN_TIME = 1  # in seconds

WAIT_AFTER_SUCCESS = 10  # in seconds

SLEEP_FOR_NEW_TRY_CONNECTION = 3  # in seconds

CHUNK_SIZE = 1024

NOT_RECOGNIZED = "Not recognized!"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

LOGGING_FILE = os.path.join(BASE_DIR, 'debug.log')
