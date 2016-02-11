import time

LOG_FILE = open("msg_log_{0}.log".format(int(time.time())), 'w+')


class Logger(object):
    @staticmethod
    def log_write(msg, flush=False):
        msg_format = "[{time:.3f}] {msg}\n"
        msg = msg.replace('\r', '\\r').replace('\n', '\\n')
        LOG_FILE.write(msg_format.format(time=time.time(), msg=msg))
        LOG_FILE.flush()
