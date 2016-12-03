import threading
import time
import math

class CameraDrivingCommand(threading.Thread):

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

    def yawSaturation(self,yaw_angle):
        if yaw_angle > self.jr.yaw_max_angle:
            yaw_angle = self.jr.yaw_max_angle
        elif yaw_angle  < self.jr.yaw_min_angle:
            yaw_angle = self.jr.yaw_min_angle
        return yaw_angle

    def pitchSaturation(self,pitch_angle):
        if pitch_angle > self.jr.pitch_max_angle:
            pitch_angle = self.jr.pitch_max_angle
        elif pitch_angle  < self.jr.pitch_min_angle:
            pitch_angle = self.jr.pitch_min_angle
        return pitch_angle

    def run(self):

        while 1:
            yaw_angle = self.jr.yaw_angle
            pitch_angle = self.jr.pitch_angle
            success, d = self.jr.camera_driving_socket.receiveData()

            if success:
                # parsing the input
                # The command should be defined by a string as:
                # COMMAND/ANGLE (e.g.: pitch/57.3)
                data = d[0].split('/')
                #print "command: ", data
                if not data.__len__() == 2:
                    print "Error receiving the DRIVING command. Not correct number of arguments in the string"
                else:
                    self.jr.yaw_angle_old = self.jr.yaw_angle
                    self.jr.pitch_angle_old = self.jr.pitch_angle
                    if data[0] == 'pitch':
                        pitch_angle = float(data[1])
                        self.jr.new_pitch_angle = True
                        self.jr.new_pitch_angle_arrived = time.time()
                    elif data[0] == 'yaw':
                        self.jr.new_yaw_angle = True
                        self.jr.new_yaw_angle_arrived = time.time()
                        yaw_angle = float(data[1])

            self.jr.yaw_angle = self.yawSaturation(yaw_angle)
            self.jr.pitch_angle = self.pitchSaturation(pitch_angle)
