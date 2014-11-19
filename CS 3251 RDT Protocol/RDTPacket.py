"""
RDT Packet class defined as per the Design Implementation Report
"""

class RDTPacket():
    def __init__(self):
        self.srcIP = None
        self.srcPort = None
        self.destIP = None
        self.destPort = None
        self.seq_num = None
        self.ack_num = None
        self.checksum = None
        self.window = None
        self.SYN = False
        self.ACK = False
        self.TRM = False
        
        self.data = None
        
    def getLength(self):
        #initial number of bytes the packet should be without flags
        num_bits = 208
        
        if self.SYN:
            num_bits += 1
        if self.ACK:
            num_bits += 1
        if self.TRM:
            num_bits += 1
        
        return num_bits
        

        
    
    
    