import json
import time
import base64
import requests
import threading
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.internet.protocol import ReconnectingClientFactory
import configs


class StreamConnection:

    def run(self, socket_protocol, ip_cam_url=configs.IP_CAM_URL, username=configs.USERNAME, password=configs.PASSWORD):
        r = requests.get(ip_cam_url, auth=(username, password), stream=True)
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
                    msg = {'type': 'FRAME',
                           'dataURL': dataURL}
                    socket_protocol.sendMessage(payload=bytes(json.dumps(msg).encode("utf-8")))
                    time.sleep(configs.SLEEP_SECONDS)
        else:
            print("Received unexpected status code {}".format(r.status_code))


class AppProtocol(WebSocketClientProtocol):

    def onConnect(self, response):
        print("Connected to the server")
        self.factory.resetDelay()

        stream_conn = StreamConnection()

        thread = threading.Thread(target=stream_conn.run, args=(self,))
        thread.daemon = True  # Daemonize thread
        thread.start()

    def onOpen(self):
        print("Connection is open.")

    def onMessage(self, payload, isBinary):
        if (isBinary):
            print("Got Binary message {0} bytes".format(len(payload)))
        else:
            print("Got Text message from the server {0}".format(payload.decode('utf8')))

    def onClose(self, wasClean, code, reason):
        print("Connect closed {0}".format(reason))


class AppFactory(WebSocketClientFactory, ReconnectingClientFactory):
    protocol = AppProtocol

    def clientConnectionFailed(self, connector, reason):
        print("Unable connect to the server {0}".format(reason))
        self.retry(connector)

    def clientConnectionLost(self, connector, reason):
        print("Lost connection and retrying... {0}".format(reason))
        self.retry(connector)


if __name__ == '__main__':
    import sys
    from twisted.python import log
    from twisted.internet import reactor

    log.startLogging(sys.stdout)
    factory = AppFactory(configs.SOCKET_URL)
    reactor.connectTCP(configs.SOCKET_SERVER, configs.SOCKET_PORT, factory)
    reactor.run()
