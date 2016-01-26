from communication import Controller as ct
import time
import sys

def send_file(binary_file, frequency, port, sleep_duration=10):
    connection = ct(port, ack_tries=10)
    time.sleep(sleep_duration)
    connection.send_binary(binary_file, frequency)

def main():
    if (len(sys.argv) != 3 and len(sys.argv) != 4):
        print("Usage: python test_binary.py path_to_file frequency [port]")
        sys.exit()
    else:
        binary_file = sys.argv[1]
        frequency = float(sys.argv[2])
        port = "/dev/ttyACM0"
        if len(sys.argv) == 4:
            port = sys.argv[3]
        send_file(binary_file, frequency, port)

if __name__ == '__main__':
    main()