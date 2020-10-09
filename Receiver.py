# receiver.py - The receiver in the reliable data transfer protocol
import packet
import socket
import sys
import udt

RECEIVER_ADDR = ('localhost', 8080)


# Receive packets from the sender w/ GBN protocol
def receive_gbn(sock, filename):
    # Open the file for writing
    try:
        file = open(filename, 'wb')
    except IOError:
        print("Cannot open %s" % filename)
        return

    expected_seq = 0
    while True:
        pkt, addr = udt.recv(sock)
        if not pkt:
            break
        seq, data = packet.extract(pkt)
        print("Received packet: %s" % seq)

        if seq == expected_seq:
            print("Received expected packet\nSending ACK: %s" % seq)
            pkt = packet.make(seq)
            udt.send(pkt, sock, addr)
            expected_seq += 1
            print("Writing data to file")
            file.write(data)
        else:
            print("Sending ACK for latest packet: %s" % (expected_seq - 1))
            pkt = packet.make(expected_seq - 1)
            udt.send(pkt, sock, addr)

    file.close()


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
    if len(sys.argv) != 3:
        print("Expected filename and send protocol as command line argument")
        exit()

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    sock.bind(RECEIVER_ADDR)

    filename = sys.argv[1]
    protocol = sys.argv[2]
    if protocol == "gbn":
        print("starting receive gbn")
        receive_gbn(sock, filename)
    elif protocol == "snw":
        print("starting receive gbn")
        receive_snw(sock, filename)
    sock.close()
