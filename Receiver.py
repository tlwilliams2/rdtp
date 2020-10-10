# receiver.py - The receiver in the reliable data transfer protocol
import packet
import socket
import sys
import udt

RECEIVER_ADDR = ('localhost', 8080)


# Receive packets from the sender w/ GBN protocol
def receive_gbn(sock, filename):
    # try to pen file for writing else throw error
    try:
        file = open(filename, 'wb')
    except IOError:
        print("Cannot open %s" % filename)
        return

    expected_seq = 0
    while True:
        pkt, addr = udt.recv(sock)                  # receive packet and check if it's valid
        if not pkt:                                 # if we receive a sentinel packet break receive
            break
        seq, data = packet.extract(pkt)             # extract packet sequence number
        print("Received packet: %s" % seq)

        if seq == expected_seq:                     # if received sequence # is the expected sequence # send ACKs
            print("Received expected packet\nSending ACK: %s" % seq)
            pkt = packet.make(seq)
            udt.send(pkt, sock, addr)
            expected_seq += 1                       # increment next expected sequence # and write data to file
            print("Writing data to file")
            file.write(data)
        else:                                       # if not expected sequence # then send ACK for most recent ingested packet
            print("Sending ACK for latest packet: %s" % (expected_seq - 1))
            pkt = packet.make(expected_seq - 1)
            udt.send(pkt, sock, addr)

    file.close()


# Receive packets from the sender w/ SR protocol
def receive_sr(sock, windowsize):
    # Fill here
    return


# Receive packets from the sender w/ Stop-n-wait protocol

ack = 0

def receive_snw(sock):
    global ack
    endStr = ''
    prevData = '' #Holds previous data incase of packet drop from Receiver to Sender
    #If data from packet contains 'END', receive stream has ended.
    while endStr!='END':
        #Extracts packet and sender address from socket.
        pkt, senderaddr = udt.recv(sock)
        #Extracts sequence number and data from packet.
        seq, data = packet.extract(pkt)
        #If data equals the previous data sent then packet was dropped from Receiver
        #to sender. Resend previous ack number with data.
        if data == prevData:
            print("Data received is previous data received. Resending previous ack.")
            if(ack == 0):
                pkt = packet.make(ack+1, data)
                udt.send(pkt,sock,senderaddr)
            else:
                pkt = packet.make(ack-1, data)
                udt.send(pkt, sock, senderaddr)
        
        #If sequence does not equal ack from Sender then packet dropped causing 
        #misorder. Send the correct sequence from Receiver back to Sender.
        elif (seq!=ack):
            print("Seq ", seq, " and ack ", ack, " do not match. Waiting for resend.")
            pkt = packet.make(ack, data)
            udt.send(pkt,sock,senderaddr)
        
        #Sequence matches ack from Sender.
        #Write data to new file, incrememnt Receiver ack, send back the Sender ack
        #to acknowledge receieved proper sequenced number.
        else:
            print("Seq ", seq, " and ack ", ack, " match. Will write to file.")
            endStr = data.decode()
            file = open("receiver_bio.txt","a")
            file.write(endStr)
            pkt = packet.make(ack, data)
            prevData = data
            
            if(ack == 0):
                ack = 1
            else:
                ack = 0
            udt.send(pkt,sock,senderaddr)
#       print("From: ", senderaddr, ", Seq# ", seq, endStr)


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
