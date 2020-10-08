# receiver.py - The receiver in the reliable data transfer protocol
import packet
import socket
import sys
import udt

RECEIVER_ADDR = ('localhost', 8080)


# Receive packets from the sender w/ GBN protocol
def receive_gbn(sock):
    seq = 0
    bio = ""
    rseq = 0
    while rseq != -1:     # how to end while loop?
        pkt, sender = udt.recv(sock)
        try:
            rseq, data = packet.extract(pkt)
            print("rseq: %s\nseq: %s\n" % (rseq, seq))
            if int(rseq) == int(seq):
                print("hello")
                bio += data.decode()
                seq += 512
                ack = packet.make(seq)
                udt.send(ack, sock, RECEIVER_ADDR)
                print("From: ", sender, ", Seq# ", seq)
            elif int(rseq) > int(seq):
                ack = packet.make(seq)
                udt.send(ack, sock, RECEIVER_ADDR)
                print("resent ack")
        except:
            print("Corrupted packet")
    return data

    # wait for frame to arrive
    # check if corrupted, do nothing if so
    # if received packet is expected seq number then read data, compile, send ack
    return


# Receive packets from the sender w/ SR protocol
def receive_sr(sock, windowsize):
    # Fill here
    return


# Receive packets from the sender w/ Stop-n-wait protocol
def receive_snw(sock):
   endStr = ''
   while endStr != 'END':
       pkt, senderaddr = udt.recv(sock)
       seq, data = packet.extract(pkt)
       endStr = data.decode()
       print("From: ", senderaddr, ", Seq# ", seq, endStr)


# Main function
if __name__ == '__main__':
    # if len(sys.argv) != 2:
    #     print('Expected filename as command line argument')
    #     exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR)
    # filename = sys.argv[1]
    print("starting gbn receive")
    data = receive_gbn(sock)
    print(type(data))
    print(data)
    # Close the socket
    sock.close()
