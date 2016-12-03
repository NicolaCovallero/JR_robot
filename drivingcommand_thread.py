import threading
import math
import sys

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

        while 1:
            success, d = self.jr.driving_socket.receiveData()

            if success:
                # parsing the input
                # The command should be defined by a string as:
                # COMMAND-VELOCITY
                data = d[0].split('-')
                # check they are three
                if not data.__len__() == 2:
                    print "Error receiving the DRIVING command. Not correct number of arguments in the string"

                #print "command: ", data[0]
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
                        self.jr.velocity_left_weel = self.jr.velocity_left_weel - (self.jr.velocity_left_weel - 50) - self.increasing_factor
                        self.jr.velocity_right_weel = self.jr.velocity_right_weel + self.increasing_factor
                    elif self.jr.state == 'BACKWARD':
                        self.jr.velocity_left_weel = self.jr.velocity_left_weel - (- self.jr.velocity_left_weel - (- 50)) - self.increasing_factor
                        self.jr.velocity_right_weel = self.jr.velocity_right_weel - self.jr.velocity_right_weel
                    else:
                        self.jr.velocity_left_weel = self.jr.velocity_left_weel  - self.increasing_factor
                        self.jr.velocity_right_weel = self.jr.velocity_right_weel + self.increasing_factor

                    self.jr.state = 'TURNING_LEFT'

                elif data[0] == 'right':

                    if self.jr.state == 'FORWARD':
                        self.jr.velocity_right_weel = self.jr.velocity_right_weel - (self.jr.velocity_right_weel - 50) - self.increasing_factor
                        self.jr.velocity_left_weel = self.jr.velocity_left_weel + self.increasing_factor
                    elif self.jr.state == 'BACKWARD':
                        self.jr.velocity_right_weel = self.jr.velocity_right_weel - (- self.jr.velocity_right_weel - (- 50)) - self.increasing_factor
                        self.jr.velocity_left_weel = self.jr.velocity_left_weel - self.jr.velocity_left_weel
                    else:
                        self.jr.velocity_right_weel = self.jr.velocity_right_weel - self.increasing_factor
                        self.jr.velocity_left_weel = self.jr.velocity_left_weel + self.increasing_factor

                    self.jr.state = 'TURNING_RIGHT'

            else: # no data received, state IDLE
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


            print 'RW:', self.jr.velocity_right_weel , "LW:", self.jr.velocity_left_weel, "YAW:", self.jr.yaw_angle, "PITCH", self.jr.pitch_angle , "           "
            sys.stdout.write("\033[F")  # cursor up one line


                # addr = d[1]
                # print 'Message[' + addr[0] + ':' + str(addr[1]) + '] - ' + data.strip()

