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

        if self.jr.communication_style == "WIFI":
            while 1:
                success, d = self.jr.connection_socket.receiveData()
                if success and d[0] == "connected":

                    data = d[0]
                    addr = d[1]
                    print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()
                    # To confirm the establishment of the connection some data are sent to the pc:
                    data_str = "jr_data/" + "yaw_range/" + str(self.jr.yaw_range_degree) + "/" + "pitch/" + str(self.jr.pitch_range_degree)
                    self.jr.connection_socket.sentData(data_str, ADDR=addr)  # send the data back
                    self.jr.IP = addr[0]
                    print "Connected to device with IP address: ", self.jr.IP
        else:
            pass

