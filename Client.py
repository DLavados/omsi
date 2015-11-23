__author__ = 'fdemoullin'

import sys
import Checksum
import select

try:
    import socket
except ImportError:
    print 'Cannot import socket. Exiting...'
    sys.exit()


# module that provides an interface for all server related requests
# sets up connection with the running server on localhost and port 20500
# all methods are static and should be called statically

# global variable to keep track of the socket
gPORT = 20500 # hardcoding the port number TODO: make based on user input
gHOST = socket.gethostname()

# setter
# pHost = IP address provided by prof
# pPort = Port provided by prof
def setUpServer(pHost, pPort):
    global gPORT, gHOST

    # deactivated during testing phase! The connection is set up on localhost

    # gPORT = pPort
    # gHOST = pHost

# executes a function on the server
# input function name to be executed
# return value True or False depending on success on server
def callFunctionOnServer(functionName):

    #create and configure the socket
    lSocket = createAndSetUpSocket()

    # execute the function
    lSocket.send(functionName)

    # see what the server has to say and return it
    lServerResponse = getResponseFromServer(lSocket)

    if lServerResponse == "s" or lServerResponse == "f":
        return lServerResponse
    else:
        # the server is trying to send a file
        return "A file"


def sendFileToServer(pFileName):

    #create and configure the socket
    lSocket = createAndSetUpSocket()

    #open the file
    lOpenFile = openFile(pFileName)

    if (lOpenFile):
        # first tell the server that we are sending a file
        lSocket.send("File")

        # block client until server is ready to accept the file
        lResponse = lSocket.recv(1024) #server will send "ready" or "abort"

        # check if something went wrong server side
        if lResponse != "ready":
            print "The server aborted prior to transmission of file, check server logs for more details"
            return

        # send the file
        lFileChunk = lOpenFile.read()
        while (lFileChunk):
            print 'Sending File'
            lSocket.send(lFileChunk)
            lFileChunk = lOpenFile.read(1024)
    else:
        print "This should not be reached"

    return getResponseFromServer(lSocket)

def openFile(pFileName):
    try:
      lOpenFile = open(pFileName, "r")
      return lOpenFile
    except IOError:
      print "Error: File does not appear to exist."
      return 0

# close the connection
def getResponseFromServer(pSocket):

    # block until server response received
    lServerResponse = pSocket.recv(1024)
    pSocket.close()

    if lServerResponse == "s":
        return True
    else:
        print lServerResponse
        return False

def createAndSetUpSocket():
     # connection on localhost for now
    global gPORT, gHOST
    try:
        # create local Internet TCP socket (domain, type)
        pSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        # initiate server connection to global
        pSocket.connect( (gHOST, gPORT) )
        return pSocket

    #connection problem
    except socket.error, (value,message):
        if pSocket:
            # close socket
            pSocket.close()
        raise RuntimeError("Could not open socket on Client: " + message)
        return False

def computeChecksum(filename):

    h = Checksum.checksum(filename)

    print 'Please hand copy the following value and turn it into the professor: ' + h

def receiveFile(pClientSocket):

    lQuestionsFile = createQuestionsFile()

    # something went wrong when creating the file, let the client know
    if (lQuestionsFile == False):
        pClientSocket.send("abort")

    lSuccess = "f"
    try:
        # let the client know the server is ready
        pClientSocket.send("ready")

        # receive the file
        while 1:
            # set a timeout for this
            ready = select.select([pClientSocket], [], [], 2)
            if ready[0]:
                lChunkOfFile = pClientSocket.recv(1024)
                lQuestionsFile.write(lChunkOfFile)
            else:
                break

        print("Finished accepting file")
        lSuccess = "s"

    finally:
        if lSuccess == "f":
            # something went wrong
            print "File transfer was not successful"
        # close file, regardless of success
        lQuestionsFile.close()

        # return success information
        return lSuccess

def createQuestionsFile():
# create new or trunctate old file - hence the w flag
    try:
        lNewFile = open("QuestionsStudent.txt", 'w')
        return lNewFile
    except IOError:
        print "Questions file could not be created on the Client's machine"
        return False