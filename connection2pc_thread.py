import threading

class ConnectionToPc(threading.Thread):

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
        tmp_data = "no_connected"
        tmp_addr = ""
        while 1:
            success, d = self.jr.connection_socket.receiveData()
            if success:
                data = d[0]
                addr = d[1]
                print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
                self.jr.connection_socket.sentData(data, ADDR=addr)  # send the data back
                if tmp_data == data and tmp_addr == addr:
                    self.jr.connected = True
                    self.jr.IP = addr[0]
                    print "Connected to device with IP address: ", self.jr.IP
                tmp_data = data
                tmp_addr = addr
