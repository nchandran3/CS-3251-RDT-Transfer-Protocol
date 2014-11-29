import sys
import socket
import errno
from BasicSocket import RDTSocket

DEBUG = False;

def d_print(string):
    if DEBUG:
        print "###DEBUG###: " + string

"""
Functionality of File Transfer Application Server
"""
class FTAServer():


    def __init__(self, serverPort, emuIPAddr, emuPort):
        self.IPAddr = "127.0.0.1"
        self.port = serverPort
        self.emuIPAddr = emuIPAddr
        self.emuPort = emuPort
        self.clientIPAddr = None            #Will be defined by connect() method
        self.clientPort = None
        self.connected = False              #Indicates server/client connection
        self.commands = ["window", "terminate"]
        self.rdtSocket = RDTSocket(self.IPAddr, self.port)

        ##testing code
#         self.rdtSocket.destIP, self.rdtSocket.destPort = '127.0.0.1', 49154

    def start(self):
        not_terminate = True
        self.rdtSocket.listen()
        print "Connected to server"
        
        while not_terminate:
            self.showCommands()
            not_terminate = self.__open()
            if not_terminate:
                print("Waiting for incoming packet")
                try:
                    rcvPacket = self.rdtSocket.receive()
                except socket.error, msg:
                    print 'Failed to create socket. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]


    """
    Waits for command from the server's user.
    @return     False if disconnect command was given; True otherwise
    """
    def __open(self):
        adminInput = raw_input("Enter command to perform: ")
        cmd = adminInput.split(" ")[0].lower()

        if not cmd or cmd not in self.commands:
            print "Invalid command"
            return True

        if cmd == "terminate":
            self.terminate()
            print "Terminate called. Shutting down server."
            return False

        #The following commands take arguments
        d_print("Admin input: " + adminInput)
        arg = adminInput.split(" ")[1]

        if cmd == "window":
            self.window(int(arg))

        return True




    """
    Shows available client commands once the client has been started. Does not implement extra credit commands
    """
    def showCommands(self):
        print """
        Commands:
        -----------------------------
        terminate      - Shuts down FTA-Server smoothly.

        """
        
        
        
        
    """
    Shows available client commands once the client has been started. Implements extra credit commands
    """
    def showCommandsx(self):
        print """
        Commands:
        -----------------------------
        window W       - Max receiver window-size at the FTA-Server = W segments.
        terminate      - Shuts down FTA-Server smoothly.

        """


    """
    Sets the maximum server/client receiving window to the specified size
    @param size - The size of the client/server's receiving window (in segments)
    """
    def window(self, size):
        d_print("Called window with size: " + str(size))
        pass



    """
    Terminates the connection with the clients and exits the client application
    with utmost grace.
    """
    def terminate(self):
        d_print("Connection terminated.")



#############################################################################################################
##################################    END    FTAServer   CLASS    ##########################################
#############################################################################################################

def usage():
    print """
    Usage: FTAServer X A P [flags]

    X:    The port number at which the FTA Server should bind to (odd number) between 0 and 65535. Should be client port # - 1.
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
        server_port = int(argsv[0])
        emu_addr = argsv[1]
        emu_port = int(argsv[2])

    except:
        print "Incorrect formatting on arguments"
        return -1

    #check to make sure all args are in correct format
    import re
    addr_regex = re.compile("^[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}\.[0-9]{1,3}$") #checks for valid IP address

    if ( server_port % 2 == 0 or server_port < 0 or server_port >65535
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

    server_port = int(argv[0])
    emu_addr = argv[1]
    emu_port = int(argv[2])

    global DEBUG        #starts out as False initially
    if len(argv) == 4:
        flag = argv[3]
        DEBUG = flag in ("-d", "--debug")
        d_print("Debugging enabled")

    server = FTAServer(server_port, emu_addr, emu_port)
    server.start()





if __name__ == "__main__":
    main(sys.argv[1:])