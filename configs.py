SOCKET_SERVER = "127.0.0.1" # Server ip-address
SOCKET_PORT = 8000  # Server Port
SOCKET_URL = "ws://{0}/ws/openface-stream/".format(SOCKET_SERVER).format(":").format(SOCKET_PORT)

streaming_process = None

IP_CAM_URL = 'http://192.168.1.101/video.mjpg?mute'
USERNAME, PASSWORD = 'admin', 'admin'

SLEEP_SECONDS = 0.25

CHUNK_SIZE = 1024
