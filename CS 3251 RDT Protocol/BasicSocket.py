try:
    import cPickle as pickle
except:
    import pickle

from RDTPacket import RDTPacket
import socket
import zlib

"""
Non Extra credit socket class that just does stop and wait, checksum, and timeouts.
"""
class RDTSocket:

    def __init__(self, IPAddr, port):
        self.srcPort = port
        self.srcIP = IPAddr
        self.destPort = None        #determined upon successful connection (either in connect or listen)
        self.destIP = None          #determined upon successful connection (either in connect or listen)
        self.CONNECTED = False      #only set to true upon successful connection with server/client
        self.TERMINATED = False     #this indicates whether the CURRENT SOCKET is terminated. The other socket must also 
                                    #be terminated in order to have a successful termination

        self.timeout = 10            #default, will change according to max timeout received
        self.MSS = 1024             #max number of bytes an RDT packet payload can have
        self.BUFFER_SIZE = self.MSS + 28    #there are 28 bytes in UDP datagram header
        self.UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)      #UDP socket for communicating with network emulator
        self.UDP_socket.bind((self.srcIP, self.srcPort))
        self.send_seq_number = 0
        self.expected_seq_number = 0
        self.ACK_number = 0


    """
    Connects to the remote server by sending a SYN packet, waiting for an ACK, and then sending one more packet.

    @param IPAddr:    The IP address of the server
    @param    port:    The port number of the server
    """
    def connect(self, IPAddr , port):
        port = self.srcPort + 1
        IPAddr = self.srcIP
        self.destIP = IPAddr
        self.destPort = port

        #send SYN packet to server
        SYN_packet = self.__makeSYNPacket()
        self.__send_packet(SYN_packet)   #send the SYN packet
        print "Sent SYN Packet"
        #wait for uncorrupted ACK
        ACK_packet  = self.__receive_packet()
        print "Received SYN-ACK"
        #send last packet to acknowledge ACK packet received.
        client_ACK_packet = self.__makeACKPacket()
        self.UDP_socket.sendto(pickle.dumps(client_ACK_packet), (self.destIP, self.destPort))
        print "Sent SYN-ACK response. Connection established"
        #we are done, begin transmission










    """
    Disconnects the client from the server
    """
    def disconnect(self):
        if not self.CONNECTED:      #we are already disconnected so just return
            return  
        
        if not self.TERMINATED:     #if we haven't already sent our intention to quit
            TRM_packet = self.__makeTRMPacket()
            self.__send_packet(TRM_packet)
            print "Sent TRM packet"
            
        


        self.UDP_socket.close()
        self.CONNECTED = False






    """
    SERVER METHOD ONLY!!!!!!!!
    Server call to block until a SYN packet is received, thus indicating intention to establish a connection.
    When this method returns, it means the server has successfully connected with a client
    """
    def listen(self):
        print "Listening for client to connect"
        if self.CONNECTED:      #can only establish connection once
            print "Already connected to a client"
            return -1

        while True:
            self.UDP_socket.settimeout(self.timeout)
            try:
                packet = self.__receive_packet()
                if packet.SYN:
                    print "Received SYN packet"
                    self.destIP = packet.destIP
                    self.destPort = packet.destPort     #after server receives a packet, it now knows where to send all other packets
                    
                    ACK_packet = self.__makeACKPacket(packet)
                    ACK_packet.ack_num = packet.seq_num
                    self.__send_packet(ACK_packet)
                    print "Sent SYN-ACK packet. Connection established"
            except socket.timeout:
                print "Socket timed out. Listening again"
                continue

        self.CONNECTED = True
        return True










    """
    Send method. Takes in data and sends it as a byte stream. The amount of packets used will be
                        (# bytes in data / MSS)  + 1
    The last packet sent will contain no data and indicates the end of the sending stream
    @param data:    The data that will be sent (as a byte string)
    """
    def send(self, data):
        #Loop through creating a packet with MSS bytes of data and sending it
        byte_pointer = 0      #points to the first byte in the next packet to be sent

        while byte_pointer + self.MSS < len(data):
            bytes_to_send = data[byte_pointer: byte_pointer+self.MSS]
            packet = self.__makePacket(bytes_to_send)
            self.__send_packet(packet)      #packet is ensured to be successfully sent and ACK'd
            byte_pointer += self.MSS

        #send last packet with data
        last_bytes = data[byte_pointer:]
        packet = self.__makePacket(last_bytes)
        self.__send_packet(packet)

        #send empty packet to indicate end of data (we have successfully transmitted the entire file)
        packet = self.__makePacket(None)
        self.__send_packet(packet)




    """
    Receives packets that are sent by the sender
    @return: The entire data byte stream that was received
    """
    def receive(self):
        data_bytes = ""

        while True:
            try:
                packet = self.__receive_packet()
                print "Received packet: ", packet.data
            except socket.timeout:
                continue

            if packet.data == None:     #we have received the last packet of the message
                print "Received entire message"
                break

            data_bytes += packet.data   #add data to "disk"
            self.__send_ACK_packet(packet)

        print "Received entire message: ", data_bytes
        return  data_bytes




    """
    Private helper method
    Continues sending the packet in intervals of {self.timeout} seconds until a valid ACK is received
    """
    def __send_packet(self, packet):

        ACK_packet = None
        packet_string = pickle.dumps(packet)

        while ACK_packet == None:
            self.UDP_socket.sendto(packet_string, (self.destIP, self.destPort))

            try:
                recv_packet = self.__receive_packet()

                if recv_packet.ACK and recv_packet.ack_num == packet.ack_num:
                    self.send_seq_number = (self.send_seq_number + 1) % 2
                    break
            except socket.timeout:
                continue



    """
    Sends an ACK packet without waiting for a timeout (implemented by receiving side only)
    """
    def __send_ACK_packet(self, packet_to_ACK):
        ACK = self.__makeACKPacket(packet_to_ACK)
        packet_string = pickle.dumps(ACK)
        print type(self.destIP)
        self.UDP_socket.sendto(packet_string, (self.destIP, self.destPort))



    """
    Receive packets. Ensures correct reception of a packet
    Returns the packet if it is ok, or None if there was an error with the packet.
    Throws a timeout exception if nothing is received within the timeout period
    @return: The packet object if it is not corrupted or a duplicate; None otherwise
    @raise socket.timeout: If the socket times out while receiving a packet
    """
    def __receive_packet(self):
        self.UDP_socket.settimeout(self.timeout)
        packet_string, addr = self.UDP_socket.recvfrom(self.BUFFER_SIZE)
        packet = pickle.loads(packet_string)

        if self.__uncorrupt(packet):
            if not self.__duplicate(packet):
                return packet
            else:
                print "Duplicate packet detected"
        else:
            print "Corrupted packet"

        return None

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
        packet.seq_num = self.send_seq_number
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



    def __makeACKPacket(self, packet_to_ACK):
        packet = self.__makePacket(None)
        packet.ACK = True
        packet.ack_num = packet_to_ACK.seq_num
        return packet



    def __checksum(self, packet):

        values = [packet.data, packet.srcIP, packet.srcPort, packet.destIP, packet.destPort, packet.seq_num, packet.ack_num,
                  packet.SYN, packet.ACK, packet.TRM]
        checksum = ""
        for val in values:
            checksum += str(zlib.crc32(pickle.dumps(val)))
        
        #trivial checksum for now - remove to implement another one
        checksum = packet.srcPort + packet.destPort
        return checksum


    def __uncorrupt(self, packet):
        if self.__checksum(packet) == packet.checksum:
            return True

        print "Packet corrupted"
        return False


    """
    Checks if a duplicate packet was received.
    """
    def __duplicate(self, packet):
        if packet.seq_num != self.send_seq_number:
            print "Duplicate packet detected"
            return True

        return False



if __name__ == "__main__":
    pass