import json
import logging
import datetime
import threading
from autobahn.twisted.websocket import WebSocketClientProtocol, WebSocketClientFactory
from twisted.internet.protocol import ReconnectingClientFactory

import configs
import utils

logging.basicConfig(format='%(asctime)s %(message)s', datefmt='%m/%d/%Y %I:%M:%S %p',
                    filename=configs.LOGGING_FILE, level=logging.DEBUG)


class StreamConnection:
    def run(self, socket_protocol, ip_cam_url=configs.IP_CAM_URL, username=configs.USERNAME, password=configs.PASSWORD):
        if configs.PROTOCOL_USED == configs.PROTOCOLS[0]:
            utils.use_rtsp_con(socket_protocol, ip_cam_url)
        elif configs.PROTOCOL_USED == configs.PROTOCOLS[1]:
            utils.use_mjpeg_con(socket_protocol, ip_cam_url, username, password)


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
                if utils.is_enough_waited_after_success(temp_now):
                    utils.last_rec_timestamp = datetime.datetime.now().timestamp()
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
