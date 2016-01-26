from communication import Controller as ct
import time
tmp = ct("/dev/ttyACM0", ack_tries=10)

time.sleep(10)

frequency = 5

tmp.send_binary("./binary/test_binary_file2.txt", frequency)

time.sleep(10)
