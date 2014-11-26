try:
    import cPickle as pickle
except:
    import pickle

import socket
import sys
import random
import RDTPacket
import binascii

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
    1. Extract the sequence number, IP Address and port number from the SYN packet (also validate checksum)
    2.
    """

    """
    The client socket will connect to the given IPAddr and port by implementing the following steps:
    1. Send SYN packet - this includes the client's initial sequence number and clients's
       receiving window size.
    2. Receive SYN packet Acknowledgement from the server - this includes the server's initial
       sequence number and the server's maximum receiving window size. Must also validate checksum
    3. The client will send an Acknowledgement to the server

           Client and server are now connected...

    @param IPAddr:    The destination IP address that the socket should connect to
    @param port:     The destination port that the socket should connect to
    """
    def clientConnect(self, IPAddr, port):
        self.destIP = IPAddr
        self.destPort = port
        recvRDTPacket = self.__makePacket()
        #1 send syn packet
        synPack = self.__makeSYNPacket()                                            # mark as SYN RDTPacket
        synPack.seq_num = (long) (random.uniform(1, (2**(32)- 1)))    #Initial sequence number is random long int
        self.initial_seq_number = synPack.seq_num
        self.curr_send_seq_number = self.initial_seq_number + 1

        synPack.checksum = self.__checksum(synPack)                   #compute/set checksum (must be last)
        pickle.dumps(synPack)                                         #serialize the packet for the UDP packet data field

        self.UDP_socket.sendto(pickle.dumps(synPack), (IPAddr, port))

        #2 receive syn-ack
        #       recDatagram = self.receive()
        recvRDTPacket = pickle.loads(self.UDP_socket.recvfrom(self.recv_buffer))

        #might need try catch to check for packet corruption and such
        #True if the packet received is a SYN-ACK with ack num == seq number +1
        if recvRDTPacket.SYN and recvRDTPacket.ACK and recvRDTPacket.ack_num == self.curr_send_seq_number:
            connACKPacket = self.__makePacket()
            connACKPacket.ACK = True
            connACKPacket.seq_num = self.curr_send_seq_number
            self.curr_send_seq_number += 1
            self.checksum = self.__checksum(connACKPacket)
            #3 send ack
            self.UDP_socket.sendto(pickle.dumps((connACKPacket), (IPAddr, port)))

        else:
            print("Wrong or Corrupted Packet received")

        self.CONNECTED = True

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
        sum = binascii.crc32(packet)
        return sum

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

    def __makeTRMPacket(self):
        packet = self.__makePacket(None)
        packet.TRM = True
        return packet

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