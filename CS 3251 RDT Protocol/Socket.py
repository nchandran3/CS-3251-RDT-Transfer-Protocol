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
        self.destPort = None        #determined upon connection
        self.destIP = None          #determined upon connection
        self.window = 1024          #default, can be changed by calling window()          
    
    """
    The socket will connect to the given IPAddr and port by implementing the following steps:
    1.
    2.
    3.
    4.
    
    @param IPAddr:    The destination IP address that the socket should connect to
    @param port:     The destination port that the socket should connect to
    """
    def connect(self, IPAddr, port):
        self.destIP = IPAddr
        self.destPort = port
        
    
    def window(self, size):
        self.window = size