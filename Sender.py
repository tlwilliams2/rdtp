import socket
import _thread
import sys
import time
import packet
import udt
from timer import Timer
from threading import Thread, Event

# Some already defined parameters
PACKET_SIZE = 512
RECEIVER_ADDR = ('localhost', 8080)
SENDER_ADDR = ('localhost', 9090)
SLEEP_INTERVAL = 0.05               # (In seconds)
TIMEOUT_INTERVAL = 0.5
WINDOW_SIZE = 4

# You can use some shared resources over the two threads
base = 0
mutex = _thread.allocate_lock()
timer = Timer(TIMEOUT_INTERVAL)

# Need to have two threads: one for sending and another for receiving ACKs


def read_payload(file):
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

seq = 0
#To stop snw_receiver thread after timeout.
stop_event = Event()
def send_snw(sock):
    # open file to be read.
    file = open("bio.txt","r",encoding="utf-8")
    #The end of file, nothing else to read.
    while(file.tell()!=3460):
        ack = seq
        #Read bytes from file as determines by PACKET_SIZE
        data = file.read(PACKET_SIZE) 
        
        data = data.encode()
        pkt = packet.make(seq, data)
        print("Sending seq# ", seq, "\n")
        
        #Loop through sending attempts until sequence as been updated
        #signaling packet has been properly sent and ack received.
        while(ack==seq):
        
            udt.send(pkt, sock, RECEIVER_ADDR)
            #Start thread for receiver_snw.
            snwThread = Thread(target = receive_snw, args=(sock, pkt))
            snwThread.start()
            #Timeout for receiver_snw thread to complete then continue down path.
            snwThread.join(timeout = .5)
            #Set stop event so receive_snw stops after timeout.
            stop_event.set()
    
    #Sends end of file flag to Receiver socket signaling file has been fully read.
    pkt = packet.make(seq, "END".encode())
    udt.send(pkt, sock, RECEIVER_ADDR)


def get_window_size(num_packets):
    global base
    return min(WINDOW_SIZE, num_packets - base)


# Send using GBN protocol
def send_gbn(sock, packets):
    global mutex
    global base
    global timer

    # get packets from file and set all necessary values
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
            print("Waiting for ACKs")
            time.sleep(SLEEP_INTERVAL)
            mutex.acquire()
        # if we time out or we have not received ACKs for all window packets
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

    # Send sentinel packets
    udt.send(packet.make_empty(), sock, RECEIVER_ADDR)
    print("All packets have been sent")



# Receive thread for stop-n-wait
def receive_snw(sock, pkt):

    endStr = ''
    
    global seq

    while endStr!='END':  
        pkt, senderaddr = udt.recv(sock)
        rSeq, data = packet.extract(pkt)
        
        #if received sequence from Receiver socket match sequence from this
        #Sender then alternate seq from 0 or 1 and break out while loop.        
        if(rSeq==seq):
            if(seq==0):
                seq = 1
            else:
                seq = 0
            break
        #Otherwise wrong sequence was received, resend correct sequence and data.
        else:
            print("Mismatched acks, resending")
            udt.send(pkt, sock, RECEIVER_ADDR)
            
        #Condition to check if timeout has been reach to end loop.
        if stop_event.is_set():
            break


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
        if ack >= base:                                  # check if ack is expected ack seq #
            mutex.acquire()                              # lock this thread
            base = ack + 1                               # increment base seq
            print("Updated next sequence #: %s" % base)  # update next base seq #
            timer.stop()
            mutex.release()


# Main function
if __name__ == '__main__':
    if len(sys.argv) != 3:
        print("Expected filename and send protocol as command line argument")
        exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(SENDER_ADDR)

    filename = sys.argv[1]
    protocol = sys.argv[2]
    if protocol == "gbn":
        print("starting sender gbn")
        print("Starting gbn send thread")
        _thread.start_new_thread(send_gbn, (sock, read_payload(filename), ))
        exit_program = input("Enter \"quit\" to exit program")
    elif protocol == "snw":
        print("starting sender snw")
        print("Starting snw send thread")
        _thread.start_new_thread(send_snw, (sock,))
        exit_program = input("Enter \"quit\" to exit program")
    sock.close()
