"""
This is the main file to control the robot
WORKIGN VERY WELL UNTIL NOW
"""

__autor__ = "Nicola Covallero"

import udpsocket # Sockets
import wiringpi # PWM
import RPi.GPIO as GPIO # GPIO
import sys
import threading

import connection2pc_thread
import drivingcommand_thread


class JonnyRobot:
    def __init__(self):
        # parameters
        self.HOST = ''
        self.CONNECTION_PORT = 2525
        self.DRIVING_PORT = 2526
        self.SONAR_PORT = 2527
        self.CAMERA_PORT = 2528
        # MOTORS' PINS ----> still to be set correctly
        # Nomenclature: _F : forward     _B : backward
        self.MOTOR_LEFT_F = 7
        self.MOTOR_LEFT_B = 11
        self.MOTOR_RIGHT_F = 15
        self.MOTOR_RIGHT_B = 13

        # STATE OF THE ROBOT
        # The possible states are:
        # IDLE : don't move
        # FORWARD : moving forward
        # BACKWARD : moving backward
        # TURNING_LEFT : turning left
        # TURNING_RIGHT : turning right
        self.command = 'IDLE'
        # Then these states are enriched by the velocity for each well
        self.velocity_left_weel = 0
        self.velocity_right_weel = 0

        # The "connection socket" is the one with the only aim to establish a connection to the computer
        self.connection_socket = udpsocket.UDPSocket()
        # We make all the sockets as servers here for the robot. Once they have binded they can be used for normal communication
        self.connection_socket.bind(self.CONNECTION_PORT, self.HOST)

        # The "driving socket" has the aim to receive data regarding the driving of the robot (direction and velocity)
        self.driving_socket = udpsocket.UDPSocket()
        self.driving_socket.bind(self.DRIVING_PORT, self.HOST)


        # The "sonar socket" send data regarding the measurement of the SONAR
        self.sonar_socket = udpsocket.UDPSocket()
        self.sonar_socket.bind(self.SONAR_PORT, self.HOST)

        # The "picamera socket" send data regarding the picamera
        self.picamera_socket = udpsocket.UDPSocket()
        self.picamera_socket.bind(self.CAMERA_PORT, self.HOST)

        # set up the wiringPi library
        wiringpi.wiringPiSetup()

    def run(self):
        connection_thread = connection2pc_thread.ConnectionToPc(0, 'Connection Thread', self)
        connection_thread.daemon = True
        connection_thread.start()

        driving_thread = drivingcommand_thread.DrivingCommand(1, 'Driving Thread', self)
        driving_thread.daemon = True
        driving_thread.start()










if __name__ == "__main__":

    try:
        jr = JonnyRobot()
        jr.run()
        print "done"

        while 1: pass # this is necessary in order to make the Keyboard interrupt detectable

    except KeyboardInterrupt:
        print 'CTRL-C pressed ... exiting...'
        exitFlag = True
        quit()