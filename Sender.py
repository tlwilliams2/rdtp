import socket
import _thread
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
base = 0
mutex = _thread.allocate_lock()
timer = Timer(TIMEOUT_INTERVAL)

# Need to have two threads: one for sending and another for receiving ACKs


# Generate random payload of any length
def generate_payload(length=10):
    letters = string.ascii_lowercase
    result_str = ''.join(random.choice(letters) for i in range(length))

    return result_str


def read_payload():
    file = "bio.txt"
    try:
        file = open(file, 'rb')
    except IOError:
        print("Cannot open %s" % file)
        return
    packets = []
    seq = 0
    while True:
        data = file.read(PACKET_SIZE)
        if not data:
            break
        packets.append(packet.make(seq, data))
        seq += 1
    return packets


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

def get_window_size(num_packets):
    global base
    return min(WINDOW_SIZE, num_packets - base)

# Send using GBN protocol
def send_gbn(sock):
    global mutex
    global base
    global timer

    # get packets from file and set all necessary values
    packets = read_payload()
    num_packets = len(packets)
    print("Packets to be sent: %s" % num_packets)
    window_size = get_window_size(num_packets)
    window_start = 0
    next_to_send = 0
    base = 0

    # Start the receiver thread
    print("Starting gbn receive thread")
    _thread.start_new_thread(receive_gbn, (sock,))

    while base < num_packets:
        # set mutex lock to this thread to execute send tasks
        # send all packets in given window
        mutex.acquire()
        while next_to_send < window_start + window_size:
            print("Sending sequence #: %s" % next_to_send)
            udt.send(packets[next_to_send], sock, RECEIVER_ADDR)
            next_to_send += 1

        # Start the timer
        if not timer.running():
            print("Starting window timer")
            timer.start()

        # Wait until a timer times out and pass mutex lock to receive thread
        while timer.running() and not timer.timeout():
            mutex.release()
            print("Waiting for acks")
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()
        # if we time out or we have not received acks for all window packets
        # then we reset window. Else we move the window
        if timer.timeout() or ((window_start + window_size) > base):
            print("Window timed out")
            timer.stop()
            next_to_send = window_start
        else:
            next_to_send = base
            window_start = base
            print("Moving window")
            window_size = get_window_size(num_packets)
        mutex.release()

    # Send sentinel packet
    udt.send(packet.make_empty(), sock, RECEIVER_ADDR)
    print("finished sending all packets")


# Receive thread for stop-n-wait
def receive_snw(sock, pkt):
    # Fill here to handle acks
    return

# Receive thread for GBN
def receive_gbn(sock):
    global mutex
    global base
    global timer

    while True:
        # receive ACKs then extract them
        pkt, addr = udt.recv(sock)
        ack, data = packet.extract(pkt)

        print("Received ack: %s" % ack)
        if ack >= base:                                 # check if ack is expected ack seq #
            mutex.acquire()                             # lock this thread
            base = ack + 1                              # increment base seq
            print("Updated next sequence #: %s" % base) # update next base seq #
            timer.stop()
            mutex.release()


# Main function
if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print('Expected filename as command line argument')
    #     exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)

    # filename = sys.argv[1]
    print("starting sender gbn")
    print("Starting gbn send thread")
    _thread.start_new_thread(send_gbn, (sock, ))
    exit_program = input("Enter \"quit\" to exit program")
    sock.close()


