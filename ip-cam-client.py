import json
import time
import base64
import datetime
import logging
import urllib3
import requests
import threading
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.internet.protocol import ReconnectingClientFactory
import configs

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename=configs.LOGGING_FILE, level=logging.DEBUG)


class StreamConnection:
    last_rec_timestamp = None

    @classmethod
    def is_send_once_in_time(cls, temp_now, prev_now):
        return temp_now - prev_now > configs.SEND_ONCE_IN_TIME

    @classmethod
    def is_enough_waited_after_success(cls, temp_now):
        l_r_t, w_a_s = cls.last_rec_timestamp, configs.WAIT_AFTER_SUCCESS
        return not l_r_t or temp_now - l_r_t > w_a_s

    @classmethod
    def is_valid_img(cls, prev_now):
        temp_now = datetime.datetime.now().timestamp()
        return cls.is_send_once_in_time(temp_now, prev_now) and cls.is_enough_waited_after_success(temp_now)

    def run(self, socket_protocol, ip_cam_url=configs.IP_CAM_URL, username=configs.USERNAME, password=configs.PASSWORD):
        try:
            r = requests.get(ip_cam_url, auth=(username, password), stream=True)
        except urllib3.exceptions.HeaderParsingError as e:
            logging.info("Exception with connection to camera: {}".format(e))
            time.sleep(configs.SLEEP_FOR_NEW_TRY_CONNECTION)
            self.run(socket_protocol, ip_cam_url, username, password)
        now_ = datetime.datetime.now().timestamp()
        if (r.status_code == 200):
            bytes_ = bytes()
            for chunk in r.iter_content(chunk_size=configs.CHUNK_SIZE):
                bytes_ += chunk
                a = bytes_.find(b'\xff\xd8')
                b = bytes_.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    jpg = bytes_[a:b + 2]
                    bytes_ = bytes_[b + 2:]
                    dataURL = 'data:image/jpeg;base64,{}'.format(base64.b64encode(jpg).decode())
                    msg = {'type': 'FRAME', 'dataURL': dataURL}
                    if self.is_valid_img(now_):
                        thread = threading.Thread(target=socket_protocol.sendMessage,
                                                  kwargs={'payload': bytes(json.dumps(msg).encode("utf-8"))})
                        thread.daemon = True  # Daemonize thread
                        thread.start()
                        time.sleep(configs.SLEEP_SECONDS)
                        now_ = datetime.datetime.now().timestamp()
        else:
            logging.info("Received unexpected status code {}".format(r.status_code))


class AppProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        logging.info("Connected to the server")
        self.factory.resetDelay()

        stream_conn = StreamConnection()

        thread = threading.Thread(target=stream_conn.run, args=(self,))
        thread.daemon = True  # Daemonize thread
        thread.start()

    def onOpen(self):
        logging.info("Connection is open.")

    def onMessage(self, payload, isBinary):
        if (isBinary):
            logging.info("Got Binary message {0} bytes".format(len(payload)))
        else:
            data = payload.decode('utf8')
            msg_data = json.loads(data)
            if msg_data['type'] == 'RECOGNIZED' and msg_data['name'] != configs.NOT_RECOGNIZED:
                temp_now = datetime.datetime.now().timestamp()
                if StreamConnection.is_enough_waited_after_success(temp_now):
                    StreamConnection.last_rec_timestamp = datetime.datetime.now().timestamp()
                logging.info("Got Text message from the server {0}".format(data))

    def onClose(self, wasClean, code, reason):
        logging.info("Connect closed {0}".format(reason))


class AppFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = AppProtocol

    def clientConnectionFailed(self, connector, reason):
        logging.info("Unable connect to the server {0}".format(reason))
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        logging.info("Lost connection and retrying... {0}".format(reason))
        self.retry(connector)


if __name__ == '__main__':
    import sys
    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)
    factory = AppFactory(configs.SOCKET_URL)
    reactor.connectTCP(configs.SOCKET_SERVER, configs.SOCKET_PORT, factory)
    reactor.run()
