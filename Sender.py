import socket
import sys
# import _thread
import time
import string
import packet
import udt
import random
from timer import Timer

# Some already defined parameters
PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
SLEEP_INTERVAL = 0.05 # (In seconds)
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 4

# You can use some shared resources over the two threads
# base = 0
# mutex = _thread.allocate_lock()
# timer = Timer(TIMEOUT_INTERVAL)

# Need to have two threads: one for sending and another for receiving ACKs


# Generate random payload of any length
def generate_payload(length=10):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


def read_payload():
    print("read bio.txt")
    return "data"


# Send using Stop_n_wait protocol
def send_snw(sock):
    # Fill out the code here
    seq = 0
    clock = Timer(TIMEOUT_INTERVAL)
    while seq < 20:
        # read packet from bio
        data = read_payload()
        # create packet from data
        pkt = packet.make(seq, data)
        # send packet
        udt.send(pkt, sock, RECEIVER_ADDR)
        seq += 512
        # start timer
        clock.start()
        # wait to receive packet
        while not clock.timeout():
            pktR, addrR = udt.recv()
            # check_corrupt(pktR), check_seq_num() continue
            # if not corrupt, is ack and has proper sequence number break
            # if timeout resend pkt and restart timer
        # if we receive packet and is not corrupt or is ack with improper sequence number stay in loop
        # if we timeout resend packet and start timer
        # if we receive a packet and it is not corrupt and it is an ack with proper sequence number we stop timer and continue
        while not clock.timeout():
            pktR, addrR = udt.recv()
        continue
        # wait to see if we receive another packet of data, if not repeat these steps starting from read packet


    #     data = generate_payload(40).encode()
    #     pkt = packet.make(seq, data)
    #     print("Sending seq# ", seq, "\n")
    #     udt.send(pkt, sock, RECEIVER_ADDR)
    #     seq = seq+1
    #     time.sleep(TIMEOUT_INTERVAL)
    # pkt = packet.make(seq, "END".encode())
    # udt.send(pkt, sock, RECEIVER_ADDR)

# Send using GBN protocol
def send_gbn(sock):

    return

# Receive thread for stop-n-wait
def receive_snw(sock, pkt):
    # Fill here to handle acks
    return

# Receive thread for GBN
def receive_gbn(sock):
    # Fill here to handle acks
    return


# Main function
if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print('Expected filename as command line argument')
    #     exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)

    # filename = sys.argv[1]

    send_snw(sock)
    sock.close()


