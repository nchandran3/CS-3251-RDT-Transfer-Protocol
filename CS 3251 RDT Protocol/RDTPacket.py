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
        
 
        

        
    
    
    