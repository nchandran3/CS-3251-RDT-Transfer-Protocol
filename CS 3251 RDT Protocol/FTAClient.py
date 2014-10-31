import sys

DEBUG = FALSE;

def d_print(string):
    if DEBUG:
        print "###DEBUG###: " + string
        
"""
Outlines the functionality of the File Transfer Application client
"""
class FTAClient():
    
    def __init__(self, port, emuIPAddr, emuPort):
        self.IPAddr = "127.0.0.1"
        self.port = port
        self.emuIPAddr = emuAddr
        self.emuPort = emuport
        self.serverIPAddr = None            #Will be defined by connect() method
        self.serverPort = None
        self.connected = False              #Indicates whether the client is connected to the server at this time
    
    """
    Should be called to start the FTA Client. Loops listen until listen returns -1
    """
    def start(self):
        not_terminate = True
        
        while not_terminate:   
            self.showCommands()
            not_terminate = self.listen()
            
            
            
    """
    Listens for commands from the user once the client has been setup. Should be called continuously until
    the disconnect command has been given.
    @return     False if disconnect command was given; True otherwise
    """
    def listen():
        input = raw_input("Enter command to perform ")
        cmd = self.__checkCmd(input)
        
        try:
            eval(cmd)
        except:
            print "Something went wrong"
            return False
        
        if cmd == "self.disconnect()":
            return False
        
        return True

        
    
    """
    Private method to parse commands given from user input. Calls showCommands() if invalid input given
    @param input - The user input 
    @return string calling the correct command. 
    """
    def __checkCmd(self, input):
        cmd = input.split(" ")[0].lower()
        commands = ["connect", "get", "post", "window", "disconnect"]
        
        if not cmd or cmd not in commands:
            print "Invalid command"
            return "self.showCommands()"
        
        if cmd == "disconnect":
            return "self.disconnect()"
        
        arg = input.split[" "][1]
        
        if cmd == "connect":
            addr, port = arg.split(":")
            return "self.%s(%d,%d)" % (cmd, addr, port)
        
        if cmd == "get" or cmd == "post":
            return "self.%s(%s)" % (cmd, arg)
            
        else:   #window was called
            return "self.%s(%d)" % (cmd, arg)   
    
            
        
    """
    Shows available client commands once the client has been started
    """
    def showCommands(self):
        print """
        Commands:
        -----------------------------
        connect x:y    - Connect to the FTA Server at IP Address {x} and port {y}
        get    f       - Download file with filename {f} to the client
        post   f       - Upload file with filename {f} to the server
        window w       - Set client maximum receiving window to {w} segments
        disconnect     - Disconnect from the FTA Server and exit application
        
        """ 
        
        
        
    """
    Connects to the server at serverIP:serverPort using the RDT Protocol.
    The server port as specified by the assignment will be one more than the client
    port number (as specified by the assignment)
    """
    def connect(serverIP, port):
        self.serverIPAddr, self.serverPort = serverIP, port
        d_print("Called connect")
        pass
    
    
    
    """
    Downloads a file from the server
    @param file - The full file name to download to the client
    @return    1 if successful;    -1 if not successful
    """
    def get(file):
        d_print("Called get with file name: " + file)
        pass
        
        
        
        
    """
    Uploads a file to the server
    @param file - The full file name to upload to the server
    @return    1 if successful; -1 if not successful
    """
    def post(file):
        d_print("Called post with file name: " + file)
        pass
    
    
    
    
    """
    Sets the maximum client receiving window to the specified size
    @param size - The size of the client's receiving window (in segments)
    """
    def window(size):
        d_print("Called window with size: " + size)
        pass
    
    
    
    """
    Closes the connection with the server and exits the client application
    """        
    def terminate():
        d_print("Called terminate")
        pass
    
    
#############################################################################################################
##################################    END    FTACLIENT    CLASS    ##########################################
#############################################################################################################

def usage():
    print """
    Usage: FTAClient X A P [flags]
    
    X:    The port number at which the FTA Client should bind to (even number) between 0 and 65535. This number should be equal to the server's port number + 1.
    A:    IP Address of the Network Emulator in form xxx.xxx.xxx.xxx
    P:    UDP Port Number of the Network Emulator (between 0 and 65535)
    
    Optional Flags
    ----------------------
    
    -d, --debug:    Set this flag to view debug print statements
    
    """   
    
"""
Main method that handles parsing the command line arguments and receiving commands such as 
download, upload, etc. 
"""
def main(argv):
    try:
        opts, args = getopt.getopt(argv, "d", ["debug"])
    
    except getopt.GetoptError:
        usage()
        sys.exit(2)
    
    for opt, args in opts:
        if opt in ("-d", "--debug"):
            DEBUG = True
    
    if checkArgs(argv) < 0:     #something was wrong with the arguments given
        usage()
        sys.exit(2)
    
    client_port = argv[0]
    emu_addr = argv[1]
    emu_port = argv[2]
    
    client = FTAClient(client_port, emu_addr, emu_port)
    

    
    
"""
Checks command line arguments for proper form
@var argsv - The command line arguments to check for FTA Client
@return    1 if no errors; -1 if error found
"""
def checkArgs(argsv):
    args = argsv.split(" ")

    if len(args) < 3 or len(args) > 4:
        return -1
    
    client_port = args[0]
    emu_addr = args[1]
    emu_port = args[2]
    
    #check to make sure all args are in correct format
    import re
    addr_regex = re.compile("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$") #checks for valid IP address
    
    if ( client_port % 2 != 0 or client_port < 0 or client_port >65535
          or addr_regex.match(emu_addr) == None
          or emu_port < 0 or emu_port > 65535):
        return -1
    
    return 1
                
    
        











if __name__ == "__main__":
    main(sys.argv[1:])