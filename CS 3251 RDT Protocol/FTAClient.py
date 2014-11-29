import sys
import getopt
from BasicSocket import RDTSocket

DEBUG = False;

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
        self.emuIPAddr = emuIPAddr
        self.emuPort = emuPort
        self.serverIPAddr = "127.0.0.1"            #Will be defined by connect() method
        self.serverPort = port + 1
        self.CONNECTED = False              #Indicates whether the client is connected to the server at this time

        self.commands = ["connect", "get", "post", "window", "disconnect", "connect-get"]       #must contain all available commands

        self.clientRDTSocket = RDTSocket(self.IPAddr, self.port, emuIPAddr, emuPort)


    """
    Should be called to start the FTA Client. Loops listen until listen returns -1
    """
    def start(self):
        not_terminate = True

        while not_terminate:
            self.showCommands()
            not_terminate = self.__listen()



    """
    Listens for commands from the user once the client has been setup. Should be called continuously until
    the disconnect command has been given.
    @return     False if disconnect command was given; True otherwise
    """
    def __listen(self):
        input = raw_input("Enter command to perform: ")
        cmd = input.split(" ")[0].lower()

        if not cmd or cmd not in self.commands:
            print "Invalid command"
            return True

        if cmd == "disconnect":
            self.terminate()
            return False

        #The following commands take arguments
        arg = input.split(" ")[1]

        if cmd == "connect":
            addr, port = arg.split(":")
            self.connect(addr, int(port))
            
        if cmd == "connect-get":
            self.connect_get(arg)
            
        if cmd == "get":
            self.get(arg)

        if cmd == "post":
            self.post(arg)

        if cmd == "window":   #window was called
            self.window(int(arg))

        return True




    """
    Shows available client commands once the client has been started. Does not implement extra credit functions
    """
    def showCommands(self):
        print """
        Commands:
        -----------------------------
        connect-get f    Connects to server and downloads file {f} to client
        disconnect     - Disconnect from the FTA Server and exit application

        """
        
        
        
    """
    Shows available client commands once the client has been started. This implements extra credit 
    functions.
    """
    def showCommandsx(self):
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
    def connect(self, serverIP, port):
        d_print("Called connect with IP: " + serverIP + " and port: " + str(port))
        if self.CONNECTED:
            print "Already connected to a server!"
            return
        
        self.serverIPAddr, self.serverPort = serverIP, port
        self.clientRDTSocket.connect(self.serverIPAddr, self.serverPort)
        self.CONNECTED = True



    """
    Downloads a file from the server
    @param file - The full file name to download to the client
    @return    1 if successful;    -1 if not successful
    """
    def get(self, file):
        d_print("Called get with file name: " + file)
        self.clientRDTSocket.send("Download:" + file)




    def connect_get(self, file):
        d_print("Called connect-get with file name: " + file)
        
        self.connect(self.serverIPAddr, self.serverPort)
        self.get(file)
        
        
    """
    Uploads a file to the server
    @param file - The full file name to upload to the server
    @return    1 if successful; -1 if not successful
    """
    def post(self, file):
        d_print("Called post with file name: " + file)
        
        pass




    """
    Sets the maximum client receiving window to the specified size
    @param size - The size of the client's receiving window (in segments)
    """
    def window(self, size):
        d_print("Called window with size: " + str(size))
        
        pass



    """
    Closes the connection with the server and exits the client application
    """
    def terminate(self):
        d_print("Called terminate")
        
        pass


#############################################################################################################
##################################    END    FTACLIENT    CLASS    ##########################################
#############################################################################################################

def usage():
    print """
    Usage: FTAClient X A P [flags]

    X:    The port number at which the FTA Client should bind to (even number) between 0 and 65535. Should be server port # + 1.
    A:    IP Address of the Network Emulator in form xxx.xxx.xxx.xxx
    P:    UDP Port Number of the Network Emulator (between 0 and 65535)

    Optional Flags
    ----------------------

    -d, --debug:    Set this flag to view debug print statements

    """





"""
Checks command line arguments for proper form
@var argsv - The command line arguments to check for FTA Client
@return    1 if no errors; -1 if error found
"""
def checkArgs(argsv):
    if len(argsv) < 3 or len(argsv) > 4:
        d_print("Incorrect number of args")
        return -1

    try:
        client_port = int(argsv[0])
        emu_addr = argsv[1]
        emu_port = int(argsv[2])

    except:
        print "Incorrect formatting on arguments"
        return -1

    #check to make sure all args are in correct format
    import re
    addr_regex = re.compile("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$") #checks for valid IP address

    if ( client_port % 2 != 0 or client_port < 0 or client_port >65535
          or addr_regex.match(emu_addr) == None
          or emu_port < 0 or emu_port > 65535):
        print "Invalid arguments received"
        return -1

    return 1






"""
Main method that handles parsing the command line arguments and receiving commands such as
download, upload, etc.
"""
def main(argv):
    if checkArgs(argv) < 0:     #something was wrong with the arguments given
        usage()
        sys.exit(2)

    client_port = int(argv[0])
    emu_addr = argv[1]
    emu_port = int(argv[2])


    global DEBUG        #starts out as False initially
    if len(argv) == 4:
        flag = argv[3]
        DEBUG = flag in ("-d", "--debug")
        d_print("Debugging enabled")

    client = FTAClient(client_port, emu_addr, emu_port)
    client.start()







if __name__ == "__main__":
    main(sys.argv[1:])