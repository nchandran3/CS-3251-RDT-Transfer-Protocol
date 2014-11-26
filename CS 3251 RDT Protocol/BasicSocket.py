try:
    import cPickle as pickle
except:
    import pickle
    
import RDTPacket
import socket
import zlib

"""
Non Extra credit socket class that just does stop and wait, checksum, and timeouts. 
"""
class RDTSocket:
    
    def __init__(self, IPAddr, port):
        self.srcPort = port
        self.srcIP = IPAddr
        self.destPort = None        #determined upon successful connection
        self.destIP = None          #determined upon successful connection
        self.CONNECTED = False      #only set to true upon successful connection with server/client
        
        self.timeout = 1            #default, will change according to max timeout received
        self.MSS = 1024             #max number of bytes an RDT packet payload can have 
        self.BUFFER_SIZE = self.MSS + 28    #there are 28 bytes in UDP datagram header
        self.UDP_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)      #UDP socket for communicating with network emulator
        self.UDP_socket.bind((self.srcIP, self.srcPort))
        
    
    """
    Connects to the remote server by sending a SYN packet, waiting for an ACK, and then sending one more packet. 
    
    @param IPAddr:    The IP address of the server
    @param    port:    The port number of the server
    """
    def connect(self, IPAddr, port):
        self.destIP = IPAddr
        self.destPort = port
        
        #send SYN packet to server
        SYN_packet = self.__makeSYNPacket()
        self.send_packet(SYN_packet)   #send the SYN packet 
        
        #wait for uncorrupted ACK
        ACK_packet  = self.receive_packet()
        
        packet = self.__makePacket(None)
        self.send_packet(packet)
        
        
    def listen(self):
        while True:
            self.UDP_socket.settimeout(self.timeout)
            try:
                packet = self.receive_packet()
                if packet.SYN:
                    ACK_packet = self.__makeACKPacket()
                    self.send_packet(ACK_packet)
            except socket.timeout:
                continue
        
        self.CONNECTED = True

    """
    Continues sending the packet in intervals of {self.timeout} seconds until a valid ACK is received
    """
    def __send_packet(self, packet):
        ACK_packet = None
        packet_string = pickle.dumps(packet)
        
        while ACK_packet == None:
            self.UDP_socket.sendtto(packet_string, (self.destIP, self.destPort))
            
            try:
                ACK_packet = self.receive_packet()
            except socket.timeout:
                continue
    
    """
    Receive packets. Returns the packet if it is ok, or None if there was an error with the packet.
    Throws a timeout exception if nothing is received within the timeout period
    """
    def __receive_packet(self):
        self.UDP_socket.settimeout(self.timeout)
        packet_string = self.UDP_socket.recv(self.BUFFER_SIZE)
        packet = pickle.loads(packet_string)
        
        if self.__uncorrupt(packet):
            return packet
        
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
        
    def __makeACKPacket(self):
        packet = self.__makePacket(None)
        packet.ACK = True
        return packet
    
    def __checksum(self,packet):
        return zlib.crc32(pickle.dumps(packet))

    def __uncorrupt(self, packet):
        if self.__checksum(packet) == packet.checksum:
            return True
        
        return False

if __name__ == "__main__":
    pass