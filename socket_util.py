# -*- coding: utf-8 -*-
import socket
import threading

logger = logging.getLogger('django')


def socket_connect(host, port, timeout=10):
    """
    |##@函数目的：连接远程服务器端口
    |##@参数说明：
    |##@返回值：
    |##@函数逻辑：
    |##@开发人：jhuang
    |##@时间：
    """
    port = int(port)
    sk = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sk.settimeout(timeout)
    logger.debug('socket_connect->%s:%s' % (host, port))
    try:
        sk.connect((host, port))
        sk.close()
        return True
    except Exception as e:
        logger.exception('socket_connect')
        return False


def socket_is_open(PORT=65531, HOST='0.0.0.0'):
    """
    | ##@函数目的: 判断端口是否开启
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        s.connect((HOST, int(PORT)))
        s.shutdown(2)
        logger.debug('%d is open' % PORT)
        return True
    except:
        logger.debug('%d is down' % PORT)
        return False


# a listen thread, listen remote connect
# when a remote machine request to connect, it will create a read thread to handle
class Listener(threading.Thread):
    """
    | ##@函数目的: 监听端口
    | ##@参数说明：
    | ##@返回值：
    | ##@函数逻辑：
    | ##@开发人：jhuang
    | ##@时间：
    """

    def __init__(self, port=65531):
        logger.debug('尝试监听：%s,端口:%s' % ("0.0.0.0", port))
        threading.Thread.__init__(self)
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind(("0.0.0.0", port))
        self.sock.listen(0)
        logger.debug('监听成功：%s,端口:%s' % ("0.0.0.0", port))

    def run(self):
        logger.debug("listener started")
        while True:
            client, cltadd = self.sock.accept()
            cltadd = cltadd
            logger.debug("accept a connect")
