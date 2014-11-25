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
        packet_string = pickle.dumps(SYN_packet)
        self.UDP_socket.sendto(packet_string, (IPAddr, port))   #send the SYN packet 
        
        #wait for uncorrupted ACK
        ACK_packet_serialized = self.UDP_socket.recv(self.BUFFER_SIZE)
        ACK_packet = pickle.loads(RDT_packet_serialized)
        
        
    def listen(self):
        while True:
            self.UDP_socket.settimeout(self.timeout)
            try:
                SYN_packet_serialized = self.UDP_socket.recv(self.MSS+28)       #UDP + IP header = 28 bytes
                SYN_packet = pickle.loads(SYN_packet_serialized)
                break
            except socket.timeout:
                continue
        
        
        if self.__uncorrupt(SYN_packet):
            pass
        
        self.CONNECTED = True

    def send(self, packet):
        ACK_packet = None
        packet_string = pickle.dumps(packet)
        
        while ACK_packet == None:
            self.UDP_socket.sendtto(packet_string, (self.IPAddr, self.port))
            
            self.UDP_socket.settimeout(self.timeout)
            try:
                ACK_packet = self.UDP_socket.recv(self.BUFFER_SIZE)
            except socket.timeout:
                continue
    """
    Receive packets
    """
    def receive(self):
        pass
    
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