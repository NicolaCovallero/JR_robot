import threading

class DrivingCommand(threading.Thread):

    def __init__(self, threadID, name, jr):
        """

        :param threadID: Id of the thread
        :param name: name of the thread
        :param jr: Jonny Robot class
        """
        threading.Thread.__init__(self)

        self.threadID = threadID
        self.name = name
        self.connected = False
        self.jr = jr

    def run(self):

        while 1:
            success, d = self.jr.driving_socket.receiveData()

            if success:
                # parsing the input
                # The command should be defined by a string as:
                # COMMAND-VELOCITY_LEFT_WEEL-VELOCITY_RIGHT_WEEL
                data = d[0].split('-')
                # check they are three
                if not data.__len__() == 3:
                    print "Error receiving the DRIVING command. Not correct number of arguments in the string"

                # TODO: add the parsing and checking


                # addr = d[1]
                # print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()

