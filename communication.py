#!/usr/bin/python
# coding=utf-8
"""
This module allows the communications between the pc and raspberry through UDP sockets.
To use the communications just initialize the class and close the sentData method. Reading from the
raspberry is still not implemented.
"""



__author__ = "Nicola Covallero"



import socket               # Import socket module
import sys
import bluetooth



class Socket:
    """
    This class allows define easily the UDP sockets communications or Bluetooth sockets.

    Basic usage:
    1) Create a connection(server) by binding the socket to a IP and PORT
            server = UDPSocket()
            server.bind(1234,'')
    Here the client ìs a new instance of the UDPSocket class.
    3) Now we can use the server to send data as well

    4) To create a UDPSocket as a simple client:
            client = UDPSocket(IP)
            client.sendData(2,IP)
    You need to know the IP.
    """
    def __init__(self, IP="", socket_=None, print_errors=False):

        self.print_errors = print_errors

        self.IP = IP
        #self.client = socket.socket()  # Create a socket object
        self.port = 2525  # Reserve a port for your service.

        # refence: http://www.binarytides.com/programming-udp-sockets-in-python/
        # create dgram udp socket
        if socket_ is None:
            try:
                self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            except socket.error:
                print 'Failed to create socket'
                sys.exit()

        else:
            self.socket = socket_

        self.type = "client"
        self.binded = False

    def bind(self,port = None, IP = None):
        """
        Bind the socket
        :param port:
        :param IP:
        :return:
        """
        if IP is None:
            IP = self.IP
        if port is None:
            port = self.port

        self.type = "server"
        #print 'bind: ', port, IP
        try:
            self.socket.bind((IP, port))
            self.binded = True
            return True
        except socket.error, msg:
            print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            self.binded = True
            return False

    # def accept(self, listen = 5):
    #     """
    #     Accept a connection. The socket must be bound to an address and listening for connections.
    #
    #     :return: The return value is a pair (conn, address) where conn is a new socket object usable
    #     to send and receive data on the connection, and address is the address bound to the socket on
    #     the other end of the connection.
    #     """
    #     if self.type == 'server' and self.binded:
    #         self.socket.listen(5)
    #         #[client_socket, address] = self.socket.accept()
    #         #return [Communication(client_socket) , address]
    #         a = 2
    #         return UDPSocket(), a
    #     elif self.binded:
    #         print "Exit - Trying to accept a connection when the socket was not binded. Call the bind() method before."


    def connect(self,port = None, IP = None):
        if IP is None:
            IP = self.IP
        if port is None:
            port = self.port

        try:
            self.socket.connect((IP, port))
            return True
        except socket.error, msg:
            print 'Connection failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            return False

    def sendData(self, *args, **kwds):
        """
        Sent data to a specific address.
        There are three admissible ways to call this funciton:
        socket.sendData(data, IP = addr[0], PORT = addr[1]) # full address specification
        socket.sendData(data, IP = addr[0]) # the port used will be the default saved in the socket
        socket.sendData(data, ADDR = addr) # full address specification (here it is defined as a tuple(IP,PORT) )

        :param args: Only one element which is the data to send
        :param kwds: keywords
        :return: True if no exceptions appeared.
        """

        try:
            if kwds.has_key('IP'):
                IP = kwds['IP']
                if kwds.has_key('PORT'):
                    self.socket.sendto(str(args[0]), (kwds['IP'], kwds['PORT']))
                else:
                    self.socket.sendto(str(args[0]), (kwds['IP'], self.port))
            elif kwds.has_key('ADDR'):
                self.socket.sendto(str(args[0]), (kwds['ADDR']))
            return True

        except socket.error, msg:
            if self.print_errors:
                print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            return False

    def receiveData(self, timeout = 0.1, bufferSize = 1024):
        self.socket.settimeout(timeout)
        d = []
        try:
            d = self.socket.recvfrom(bufferSize)
            return [True,d]
        except socket.error, msg:
            if self.print_errors:
                if msg[0] == "timed out":
                        print 'Error Code : ' + str(msg[0])
                else:
                        print 'Error Code : ' + str(msg[0])   + ' Message ' + msg[1]
            return [False,d]


    def closeSocket(self):
        self.socket.close  # Close the socket when done

    def setPrintErrors(self,val):
        self.print_errors = val

class BluetoothSocket:
    """
    This class allows define easily the UDP sockets communications or Bluetooth sockets.

    Basic usage:
    1) Create a connection(server) by binding the socket to a IP and PORT
            server = UDPSocket()
            server.bind(1234,'')
    Here the client ìs a new instance of the UDPSocket class.
    3) Now we can use the server to send data as well

    4) To create a UDPSocket as a simple client:
            client = UDPSocket(IP)
            client.sendData(2,IP)
    You need to know the IP.
    """
    def __init__(self, id=None, socket_=None, print_errors=False):

        self.uuid = id
        self.print_errors = print_errors

        #self.client = socket.socket()  # Create a socket object
        self.port = 2525  # Reserve a port for your service.

        # refence: http://www.binarytides.com/programming-udp-sockets-in-python/
        # create dgram udp socket
        if socket_ is None:
            try:
                self.socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            except socket.error:
                print 'Failed to create socket'
                sys.exit()

        else:
            self.socket = socket_

        self.type = "client"
        self.binded = False

    def bind(self,port = None):
        """
        Bind the socket
        :param port:
        :param IP:
        :return:
        """

        if port is None:
            port = bluetooth.PORT_ANY

        self.type = "server"
        try:
            self.socket.bind(("", port))
            self.binded = True
            return True
        except IOError:
            return False

    def sendData(self, *args, **kwds):
        """
        Sent data to a specific address.
        There are three admissible ways to call this funciton:
        socket.sendData(data, IP = addr[0], PORT = addr[1]) # full address specification
        socket.sendData(data, IP = addr[0]) # the port used will be the default saved in the socket
        socket.sendData(data, ADDR = addr) # full address specification (here it is defined as a tuple(IP,PORT) )

        :param args: Only one element which is the data to send
        :param kwds: keywords
        :return: True if no exceptions appeared.
        """

        try:
            if kwds.has_key('IP'):
                IP = kwds['IP']
                if kwds.has_key('PORT'):
                    self.socket.sendto(str(args[0]), (kwds['IP'], kwds['PORT']))
                else:
                    self.socket.sendto(str(args[0]), (kwds['IP'], self.port))
            elif kwds.has_key('ADDR'):
                self.socket.sendto(str(args[0]), (kwds['ADDR']))
            return True

        except socket.error, msg:
            if self.print_errors:
                print 'Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
            return False

    def receiveData(self, timeout = 0.1, bufferSize = 1024):
        self.socket.settimeout(timeout)
        d = []
        try:
            d = self.socket.recvfrom(bufferSize)
            return [True,d]
        except IOError:
            return [False,d]

    def closeSocket(self):
        self.socket.close()  # Close the socket when done

    def setPrintErrors(self,val):
        self.print_errors = val

    def find_service(self, uuid, addr=None):
        if addr == None: print 'Searching for all nearby devices'
        else: print "Searching for SampleServer on ", addr

        self.services_matches = bluetooth.find_service(uuid=uuid, address=addr)


    def advertise_service(self,name = 'bluetooth_server'):
        bluetooth.advertise_service(self.socket, name,
                          service_id=self.uuid,
                          service_classes=[uuid, bluetooth.SERIAL_PORT_CLASS],
                          profiles=[bluetooth.SERIAL_PORT_PROFILE],
                          #                   protocols = [ OBEX_UUID ]
                          )
    def accept(self):
        return self.socket.accept()

    def connect(self,name):

        # check in all the service the desire done and connect to it
        for match in self.services_matches:
            if match["name"] == name:
                port = match["port"]
                name = match["name"]
                host = match["host"]
                break
        self.socket.connect((host, port))

    def setServiceID(self,id):
        self.uuid = id

    def listen(self,val):
        self.socket.listen(val)

if __name__ == '__main__':
    # global IP
    # IP = '192.168.1.5'  # raspberyr's IP
    # server = UDPSocket()
    # server.bind(1234,'')
    # server.closeSocket()

    # to launch with sudo
    bl_server = BluetoothSocket()
    uuid = "94f39d29-7d6d-437d-973b-fba39e49d4ee"
    bl_server.setServiceID(uuid)
    bl_server.bind()
    bl_server.listen(1)
    bl_server.advertise_service()

    client_sock, client_info = bl_server.accept()
    print "Accepted connection from ", client_info
    while True:
        data = bl_server.socket.recv(1024)
        #success, data = bl_server.receiveData()
        if len(data) > 0:
            print "received ", data



    bl_server.closeSocket()
    client_sock.closeSocket()