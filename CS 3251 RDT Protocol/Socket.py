try:
    import cPickle as pickle
except:
    import pickle

import socket
import sys
import random
import RDTPacket
import zlib

"""
This class implements the RDT protocol and allows the File Transfer Application to perform the following
functions:

send(msg)
receive(buffer size)

Internally, it handles all connection setup and teardown as per the specifications on the Implementation Design Report
"""




class Socket:

    """
    Upon creation, the socket is given its source IP and source port
    @param IPAddr:    The source IP address that the socket will listen on
    @param port:    The source port that the socket will listen on
    """
    def __init__(self, IPAddr, port):
        self.srcPort = port
        self.srcIP = IPAddr
        self.destPort = None        #determined upon successful connection
        self.destIP = None          #determined upon successful connection
        self.CONNECTED = False      #only set to true upon successful connection with server/client
        self.UPLOADING = False      #if the socket is sending data in its packets
        self.DOWNLOADING = False    #if the socket is receiving data and sending ACKs
        self.window = 1024          #default, can be changed by calling window(int) in bits
        self.timeout = 1            #default, will change according to max timeout received

        self.send_buffer = []       #holds all packets currently awaiting ACKs
        self.recv_buffer = []       #holds all packets received which haven't been flushed to disk yet

        self.initial_seq_number = None      #set upon connection
        self.curr_send_seq_number = None        #The next sent packet will be given this sequence number
        self.RTT = 1                #equal to the max received RTT so far (1 default)
        self.MSS = 1024             #max number of bytes a RDT packet payload can have

        self.UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)      #UDP socket for communicating with network emulator
        self.UDP_socket.bind((self.srcIP, self.srcPort))
    """
    The server socket will connect to a given IPAddr and port number if a SYN packet is received
    by implementing the following steps:
    1.  The checksum from the packet is validated. If SYN packet, extract the sequence number(called A), IP Address, port number and checksum.
    2.  Randomly generate an initial sequence number for the server.
    3.  Send SYN-ACK packet back to client with the ack number equal to one plus the sequence number(A) received.
        Also send the server's initial sequence number. Increment sequence number.

            Server is connected to Client...
    """
    def serverConnect(self):
        while self.CONNECTED == False:
            #1
            recvPacket = pickle.loads(self.UDP_socket.recvfrom(self.recv_buffer))

            if recvPacket.SYN == True and self.__uncorrupt(recvPacket):
                self.destIP = recvPacket.destIP
                self.destPort = recvPacket.destPort

                #2
                #Initial sequence number is a random long integer
                self.initial_seq_number = (long) (random.uniform(1, (2**(32)- 1)))

                #3
                saPacket = self.__makeSYNACKPacket()
                saPacket.checksum = self.__checksum(saPacket)

                self.UDP_socket.sendto(pickle.dumps(saPacket), (self.srcIP, self.srcPort))

                self.CONNECTED = True



    """
    The client socket will connect to the given IPAddr and port by implementing the following steps:
    1. Send SYN packet - this includes the client's initial sequence number, clients's
       receiving window size and checksum.
    2. Receive SYN packet Acknowledgement from the server - this includes the server's initial
       sequence number and the server's maximum receiving window size. Must also validate checksum.
    3. The client will send an Acknowledgement to the server with correct sequence and ack numbers.
        Again checksum must be computed and sent.

           Client is connected to Server...

    @param IPAddr:    The destination IP address that the socket should connect to
    @param port:     The destination port that the socket should connect to
    """
    def clientConnect(self, IPAddr, port):
        self.destIP = IPAddr
        self.destPort = port

        #1 send syn packet
        synPack = self.__makeSYNPacket()
        #Initial sequence number is a random long integer
        self.initial_seq_number = (long) (random.uniform(1, (2**(32)- 1)))
        synPack.seq_num = self.initial_seq_number
        self.curr_send_seq_number = self.initial_seq_number + 1

        synPack.checksum = self.__checksum(synPack)

        #send and serialize the packet for the UDP packet data field
        self.UDP_socket.sendto(pickle.dumps(synPack), (IPAddr, port))

        #2 receive syn-ack
        recvRDTPacket = pickle.loads(self.UDP_socket.recvfrom(self.recv_buffer))

        while self.CONNECTED == False:
            #True if the packet received is a SYN-ACK with ack num == seq number +1
            if (recvRDTPacket.SYN and recvRDTPacket.ACK and recvRDTPacket.ack_num == self.curr_send_seq_number
                and self.__isValidChecksum(recvRDTPacket)):
                connACKPacket = self.__makePacket()
                connACKPacket.ACK = True
                connACKPacket.seq_num = self.curr_send_seq_number
                self.curr_send_seq_number += 1
                self.checksum = self.__checksum(connACKPacket)

                #3 send ack
                self.UDP_socket.sendto(pickle.dumps((connACKPacket), (IPAddr, port)))

                self.CONNECTED = True

            else:
                print("Wrong or Corrupted Packet received...")
                self.CONNECTED = False

    """
    This method is only to be called on the server file transfer application. Blocks until it receives a SYN packet. It will
    then perform the connect process as detailed in the design report.
    """
    def listen(self):
        ##assign received packet to variable
        rcvPack = self.receive()

        ##if packet is SYN -> call connect


    """
    Changes the window size of the client or server.
    @param size:    The new size of the window
    """
    def set_window(self, size):
        self.window = size



    """
    Disconnects the client from the server. The process is as following:
    1. Client sends a TRM packet
    2. Server acknowledges the packet
    3. Server sends a TRM packet
    4. Client sends an ACK packet
    Connection terminated
    """
    def disconnect(self):
        self.__makeTRMPacket()

        self.CONNECTED = False



    """
    Sends data (in windows) to the other end of the socket. If there is no ACK within the timeout period, resends that
    single packet (selective repeat).

    @param data:    The data to be sent to the other end of the socket
    """
    def send(self, data):
        packet = self.__makePacket(data)
        packet_string = pickle.dumps(packet)
        self.UDP_socket.sendto(packet_string, (self.destIP, self.destPort))

    """
    Receives data from the other end of the connection.

    @return    The data received from the other end of the connection
    """
    def receive(self):
        disk = ""     #represents the "disk". Keeps concatenating bits read from packets once the buffer is flushed

        pass

    """
    Calculates the checksum of the entire packet by implementing the CRC32 algorithm
    """
    def __checksum(self, packet):
        values = [packet.data, packet.srcIP, packet.srcPort, packet.destIP, packet.destPort, packet.seq_num, packet.ack_num,
                  packet.SYN, packet.ACK, packet.TRM]
        checksum = ""
        for val in values:
            checksum += zlib.crc32(pickle.dumps(val))

        return checksum

    """
    Creates a RDT Packet with the given data
    @param data:    The data to be sent in the packet
    @return:     The RDT Packet
    """
    def __makePacket(self, data):
        packet = RDTPacket()
        packet.data = data

        packet.srcIP = self.srcIP
        packet.srcPort = self.srcPort
        packet.destIP = self.destIP
        packet.destPort = self.destPort
        packet.seq_num = None
        packet.ack_num = None
        packet.window = self.window
        packet.SYN = False
        packet.ACK = False
        packet.TRM = False
        packet.checksum = self.__checksum(packet) #must be calculated last because it considers all header fields as well

        return packet

    def __makeSYNPacket(self):
        packet = self.__makePacket(None)
        packet.SYN = True
        return packet

    def __makeSYNACKPacket(self):
        packet = self.__makePacket(None)
        packet.SYN = True
        packet.ACK = True
        return packet

    def __makeTRMPacket(self):
        packet = self.__makePacket(None)
        packet.TRM = True
        return packet

    def uncorrupt(self, recvRDTPacket):
        recChecksum = self.__checksum(recvRDTPacket)
        return (recChecksum == recvRDTPacket.checksum)

    """
    Breaks up a message into message size/MSS packets

    @param msg:    The entire message or data to turn into RDT packets
    @return:    The entire string of packets for the message
    """
    def __packetize(self, msg_string):
        num_packets = len(msg_string)/self.MSS




def main():
    pass













if __name__ == '__main__':
    main()