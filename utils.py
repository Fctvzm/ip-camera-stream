import io
import rtsp
import json
import time
import base64
import logging
import urllib3
import datetime
import requests
import threading

import configs

last_rec_timestamp = None


def is_send_once_in_time(temp_now, prev_now):
    return temp_now - prev_now > configs.SEND_ONCE_IN_TIME


def is_enough_waited_after_success(temp_now):
    l_r_t, w_a_s = last_rec_timestamp, configs.WAIT_AFTER_SUCCESS
    return not l_r_t or temp_now - l_r_t > w_a_s


def is_valid_img(prev_now):
    temp_now = datetime.datetime.now().timestamp()
    return is_send_once_in_time(temp_now, prev_now) and is_enough_waited_after_success(temp_now)


def send_img(image, prev_now, socket_protocol):
    dataURL = 'data:image/jpeg;base64,{}'.format(base64.b64encode(image).decode())
    msg = {'type': 'FRAME', 'dataURL': dataURL}
    if is_valid_img(prev_now):
        thread = threading.Thread(target=socket_protocol.sendMessage,
                                  kwargs={'payload': bytes(json.dumps(msg).encode("utf-8"))})
        thread.daemon = True  # Daemonize thread
        thread.start()
        time.sleep(configs.SLEEP_SECONDS)
        return datetime.datetime.now().timestamp()


def use_rtsp_con(socket_protocol, ip_cam_url=configs.RTSP_IP_CAM_URL):
    client = rtsp.Client(ip_cam_url)._capture
    image = client.read()
    now_ = datetime.datetime.now().timestamp()
    while True:
        img_bytes = io.BytesIO()
        image.save(img_bytes, format='JPEG')
        img_bytes = img_bytes.getvalue()
        new_now = send_img(img_bytes, now_, socket_protocol)
        now_ = new_now if new_now else now_
        image = client.read()


def use_mjpg_con(socket_protocol, ip_cam_url=configs.MJPG_IP_CAM_URL,
                 username=configs.MJPG_USERNAME, password=configs.MJPG_PASSWORD):
    try:
        r = requests.get(ip_cam_url, auth=(username, password), stream=True)
        now_ = datetime.datetime.now().timestamp()
        if (r.status_code == 200):
            bytes_ = bytes()
            for chunk in r.iter_content(chunk_size=configs.CHUNK_SIZE):
                bytes_ += chunk
                a = bytes_.find(b'\xff\xd8')
                b = bytes_.find(b'\xff\xd9')
                if a != -1 and b != -1:
                    image = bytes_[a:b + 2]
                    bytes_ = bytes_[b + 2:]
                    new_now = send_img(image, now_, socket_protocol)
                    now_ = new_now if new_now else now_
    except (urllib3.exceptions.HeaderParsingError, requests.exceptions.ConnectionError) as e:
        logging.info("Exception with connection to camera: {}".format(e))
        time.sleep(configs.SLEEP_FOR_NEW_TRY_CONNECTION)
        use_mjpg_con(socket_protocol, ip_cam_url, username, password)
    else:
        logging.info("Received unexpected status code {}".format(r.status_code))
