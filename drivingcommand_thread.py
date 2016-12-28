import threading
import math
import sys
import bluetooth

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
        self.jr = jr
        self.increasing_factor = 5

    def saturation(self,vel):
        if vel > self.jr.MAX_SPEED:
            vel = self.jr.MAX_SPEED
        elif vel < - self.jr.MAX_SPEED:
            vel = - self.jr.MAX_SPEED
        return vel


    def run(self):

        if self.jr.communication_style == "WIFI":

            while 1:
                success, d = self.jr.driving_socket.receiveData()
                self.updateCommands(success,d)


        else:

            bluetooth.advertise_service(self.jr.driving_socket, "jr_driving_service",
                              service_id=self.jr.DRIVING_SERVICE_UUID,
                              service_classes=[self.jr.DRIVING_SERVICE_UUID, bluetooth.SERIAL_PORT_CLASS],
                              profiles=[bluetooth.SERIAL_PORT_PROFILE],
                              #                   protocols = [ OBEX_UUID ]
                              )

            try:
                self.jr.driving_socket_client_sock, self.jr.driving_socket_client_sock_info = self.jr.driving_socket.accept()
                print "Connection established for DRIVING service, acceptd from", self.jr.driving_socket_client_sock_info
            except IOError:
                print "IOError in driving accepting connection"

            timeout = 0.05
            self.jr.driving_socket_client_sock.settimeout(timeout)
            while True:
                try:
                    d = self.jr.driving_socket_client_sock.recv(1024)
                    if len(d) > 0:
                        self.updateCommands(True, d)
                    else:
                        print "wrong command sent to DRIVING service"
                except IOError, e:
                    self.updateCommands(False, None)
                    # TODO
                    # handle exceptions accordingly ot timeout or connection reset by peer
                    # if e[0] == 11 or e == "timed out":
                    #     self.updateCommands(False, d)
                    # else:
                    #     print "connection lost with: ", self.jr.driving_socket_client_sock_info
                    #     print "Error number:", e.errno
                    #     print "Error:", e

    def updateCommands(self,success,d):
        if success:
            # parsing the input
            # The command should be defined by a string as:
            # COMMAND-VELOCITY
            if self.jr.communication_style == "WIFI":
                data = d[0].split('-')
            else:
                data = d.split('-') # this because the bluetooth socket receives directly the string, while the udp
                                    # receives (string, adrress)

            # check they are three
            if not data.__len__() == 2:
                print
                "Error receiving the DRIVING command. Not correct number of arguments in the string"

            # print "command: ", data[0]
            if data[0] == 'forward':
                self.jr.state = 'FORWARD'
                self.jr.velocity_right_weel = self.jr.velocity_right_weel + self.increasing_factor
                self.jr.velocity_left_weel = self.jr.velocity_left_weel + self.increasing_factor


            elif data[0] == 'backward':
                self.jr.state = 'BACKWARD'
                self.jr.velocity_right_weel = self.jr.velocity_right_weel - self.increasing_factor

                self.jr.velocity_left_weel = self.jr.velocity_left_weel - self.increasing_factor

            elif data[0] == 'left':

                # self.jr.velocity_left_weel = self.jr.velocity_left_weel - self.increasing_factor
                if self.jr.state == 'FORWARD':
                    self.jr.velocity_left_weel = self.jr.velocity_left_weel - (
                    self.jr.velocity_left_weel - 50) - self.increasing_factor
                    self.jr.velocity_right_weel = self.jr.velocity_right_weel + self.increasing_factor
                elif self.jr.state == 'BACKWARD':
                    self.jr.velocity_left_weel = self.jr.velocity_left_weel - (
                    - self.jr.velocity_left_weel - (- 50)) - self.increasing_factor
                    self.jr.velocity_right_weel = self.jr.velocity_right_weel - self.jr.velocity_right_weel
                else:
                    self.jr.velocity_left_weel = self.jr.velocity_left_weel - self.increasing_factor
                    self.jr.velocity_right_weel = self.jr.velocity_right_weel + self.increasing_factor

                self.jr.state = 'TURNING_LEFT'

            elif data[0] == 'right':

                if self.jr.state == 'FORWARD':
                    self.jr.velocity_right_weel = self.jr.velocity_right_weel - (
                    self.jr.velocity_right_weel - 50) - self.increasing_factor
                    self.jr.velocity_left_weel = self.jr.velocity_left_weel + self.increasing_factor
                elif self.jr.state == 'BACKWARD':
                    self.jr.velocity_right_weel = self.jr.velocity_right_weel - (
                    - self.jr.velocity_right_weel - (- 50)) - self.increasing_factor
                    self.jr.velocity_left_weel = self.jr.velocity_left_weel - self.jr.velocity_left_weel
                else:
                    self.jr.velocity_right_weel = self.jr.velocity_right_weel - self.increasing_factor
                    self.jr.velocity_left_weel = self.jr.velocity_left_weel + self.increasing_factor

                self.jr.state = 'TURNING_RIGHT'

        else:  # no data received, state IDLE
            self.jr.state = 'IDLE'

            if self.jr.velocity_right_weel > 0:
                self.jr.velocity_right_weel = self.jr.velocity_right_weel - 30
            if self.jr.velocity_right_weel < 0:
                self.jr.velocity_right_weel = self.jr.velocity_right_weel + 30

            if self.jr.velocity_left_weel > 0:
                self.jr.velocity_left_weel = self.jr.velocity_left_weel - 30
            if self.jr.velocity_left_weel < 0:
                self.jr.velocity_left_weel = self.jr.velocity_left_weel + 30

        # self.saturation(self.jr.velocity_right_weel)
        # self.saturation(self.jr.velocity_left_weel)
        self.jr.velocity_right_weel = self.saturation(self.jr.velocity_right_weel)
        self.jr.velocity_left_weel = self.saturation(self.jr.velocity_left_weel)

        # data updating


        print
        'RW:', self.jr.velocity_right_weel, "LW:", self.jr.velocity_left_weel, "YAW:", self.jr.yaw_angle, "PITCH", self.jr.pitch_angle, "           "
        sys.stdout.write("\033[F")  # cursor up one line