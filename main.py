
"""
This is the main file to control the robot
WORKIGN VERY WELL UNTIL NOW
"""

from __future__ import division
__autor__ = "Nicola Covallero"


import udpsocket # Sockets
import bluetooth
import wiringpi # PWM
import RPi.GPIO as GPIO # GPIO
import time
import sys
import threading

import connection2pc_thread
import drivingcommand_thread
import cameradrivingcommand_thread
import motorscontroller_thread


class JonnyRobot:
    def __init__(self, communication_style = "WIFI"):
        # parameters
        self.communication_style = communication_style
        self.HOST = ''
        self.CONNECTION_PORT = 2525


        self.DRIVING_PORT = 2526
        self.DRIVING_SERVICE_UUID = "94f39d29-7d6d-437d-973b-fba39e49d4ee"

        self.SONAR_PORT = 2527

        self.CAMERA_PORT = 2528

        self.CAMERA_DRIVING_PORT = 2529
        self.CAMERA_DRIVING_SERVICE_UUID = "94f39d29-7d6d-437d-973b-fba39e49d4ea"


        # MOTORS' PINS ----> still to be set correctly
        # Nomenclature: _F : forward     _B : backward
        self.MOTOR_LEFT_F = 7
        self.MOTOR_LEFT_B = 11
        self.MOTOR_RIGHT_F = 15
        self.MOTOR_RIGHT_B = 13
        # we know map them to the wiringPi gpio map
        # http://wiringpi.com/pins/
        self.MOTOR_LEFT_F = mapGPIO2WIRINGPI(self.MOTOR_LEFT_F)
        self.MOTOR_LEFT_B = mapGPIO2WIRINGPI(self.MOTOR_LEFT_B)
        self.MOTOR_RIGHT_F = mapGPIO2WIRINGPI(self.MOTOR_RIGHT_F)
        self.MOTOR_RIGHT_B = mapGPIO2WIRINGPI(self.MOTOR_RIGHT_B)


        # STATE OF THE ROBOT
        # The possible states are:
        # IDLE : don't move
        # FORWARD : moving forward
        # BACKWARD : moving backward
        # TURNING_LEFT : turning left
        # TURNING_RIGHT : turning right
        self.state = 'IDLE'
        # Then these states are enriched by the velocity for each well
        self.MAX_SPEED = 100
        self.MIN_SPEED = 70
        self.velocity_left_weel = 0
        self.velocity_right_weel = 0

        # The "connection socket" is the one with the only aim to establish a connection to the computer
        if self.communication_style == "WIFI":
            self.connection_socket = udpsocket.UDPSocket()
            # We make all the sockets as servers here for the robot. Once they have binded they can be used for normal communication
            self.connection_socket.bind(self.CONNECTION_PORT, self.HOST)
        else:
            self.connection_socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            # bind the socket to an address, this format bounds the socket to any port and any address. You can bound the socket to a specific address and a specific port.
            self.connection_socket.bind(("", bluetooth.PORT_ANY))
            # Listen to connections made to the socket. The argument specified the maximum number of queded connections. It has to be at least 0 but in that case it does not listen anyone.
            self.connection_socket.listen(1)

        # The "driving socket" has the aim to receive data regarding the driving of the robot (direction and velocity)
        if self.communication_style == "WIFI":
            self.driving_socket = udpsocket.UDPSocket()
            self.driving_socket.bind(self.DRIVING_PORT, self.HOST)
        else:
            self.driving_socket = bluetooth.BluetoothSocket( bluetooth.RFCOMM )
            # bind the socket to an address, this format bounds the socket to any port and any address. You can bound the socket to a specific address and a specific port.
            self.driving_socket.bind(("", bluetooth.PORT_ANY))
            # Listen to connections made to the socket. The argument specified the maximum number of queded connections. It has to be at least 0 but in that case it does not listen anyone.
            self.driving_socket.listen(1)

        # The "driving socket" has the aim to receive data regarding the driving of the robot (direction and velocity)
        if self.communication_style == "WIFI":
            self.camera_driving_socket = udpsocket.UDPSocket()
            self.camera_driving_socket.bind(self.CAMERA_DRIVING_PORT, self.HOST)
        else:
            self.camera_driving_socket = bluetooth.BluetoothSocket(bluetooth.RFCOMM)
            # bind the socket to an address, this format bounds the socket to any port and any address. You can bound the socket to a specific address and a specific port.
            self.camera_driving_socket.bind(("", bluetooth.PORT_ANY))
            # Listen to connections made to the socket. The argument specified the maximum number of queded connections. It has to be at least 0 but in that case it does not listen anyone.
            self.camera_driving_socket.listen(1)




        # The "sonar socket" send data regarding the measurement of the SONAR
        self.sonar_socket = udpsocket.UDPSocket()
        self.sonar_socket.bind(self.SONAR_PORT, self.HOST)

        # The "picamera socket" send data regarding the picamera
        self.picamera_socket = udpsocket.UDPSocket()
        self.picamera_socket.bind(self.CAMERA_PORT, self.HOST)

        # set up the wiringPi library
        wiringpi.wiringPiSetup()
        wiringpi.pinMode(self.MOTOR_LEFT_F, 1)
        wiringpi.pinMode(self.MOTOR_LEFT_B, 1)
        wiringpi.pinMode(self.MOTOR_RIGHT_F, 1)
        wiringpi.pinMode(self.MOTOR_RIGHT_B, 1)
        wiringpi.softPwmCreate(self.MOTOR_LEFT_F, 0, 100)
        wiringpi.softPwmCreate(self.MOTOR_LEFT_B, 0, 100)
        wiringpi.softPwmCreate(self.MOTOR_RIGHT_F, 0, 100)
        wiringpi.softPwmCreate(self.MOTOR_RIGHT_B, 0, 100)

        # CAMERA SERVO MOTORS -----------------------------------
        # set pwm for servo motors (motor for the camera)
        self.yaw_motor_pin = 12
        self.pitch_motor_pin = 16
        self.PWM_FREQUENCY = 50 # Hz
        self.camera_motors_max_time = 0.3 #sec  - Maximum time to send a pwm (for noise reduction)
        GPIO.setmode(GPIO.BOARD)
        GPIO.setup(self.yaw_motor_pin, GPIO.OUT)
        GPIO.setup(self.pitch_motor_pin, GPIO.OUT)
        self.yaw_motor_pwm = GPIO.PWM(self.yaw_motor_pin,self.PWM_FREQUENCY )
        self.yaw_motor_pwm.start(0.0)
        self.pitch_motor_pwm = GPIO.PWM(self.pitch_motor_pin, self.PWM_FREQUENCY)
        self.pitch_motor_pwm.start(0.0)

        # initial angle
        self.yaw_angle = 0
        self.pitch_angle = 0
        self.PULSES2DEGREE = 180/200 # 180 degree/ 200 pulses
        self.yaw_angle_old = self.yaw_angle
        self.pitch_angle_old = self.pitch_angle
        self.new_yaw_angle = False # this is set to true when tehre is a new yaw angle
        self.new_yaw_angle_arrived = time.time() # time at which the new yaw angle arrived
        self.new_pitch_angle = False
        self.new_pitch_angle_arrived = time.time()


        # the servo motors are controlled with pulses, from 50 to 250
        # we use the term pulse because it refers to the pwm with (50=0.5ms,250=2.5ms)
        # we are going to set the zero value of the servo with the central pulse
        # ideally 50 is -90 degree and 250 is + 90 degree (- is on the rigth for the yaw, and down for the pitch)
        self.yaw_angle_zero_pulse = 140
        self.pitch_angle_zero_pulse = 145
        # iF the zero values are not perfectly calibrated to 150 we are going to center with saturation values
        self.yaw_range_pulse = min( self.yaw_angle_zero_pulse - 50, 250 - self.yaw_angle_zero_pulse)
        self.yaw_max_pulse = self.yaw_angle_zero_pulse + self.yaw_range_pulse + 50
        self.yaw_min_pulse = self.yaw_angle_zero_pulse - self.yaw_range_pulse
        self.pitch_range_pulse = min(self.pitch_angle_zero_pulse - 50, 250 - self.pitch_angle_zero_pulse)
        self.pitch_max_pulse = self.pitch_angle_zero_pulse + self.pitch_range_pulse + 50
        self.pitch_min_pulse = self.pitch_angle_zero_pulse - self.pitch_range_pulse

        # 180degree/200pulses = degree/pulses is the resolution
        self.yaw_range_degree = 180/200 * 2 * self.yaw_range_pulse
        self.pitch_range_degree = 180/200 * 2 * self.pitch_range_pulse
        self.yaw_max_angle = self.yaw_range_degree/2
        self.yaw_min_angle = - self.yaw_max_angle
        self.pitch_max_angle = self.pitch_range_degree / 2
        self.pitch_min_angle = - self.pitch_max_angle
        print "YAW/PITCH RANGES [+/-degree]: ", self.yaw_range_degree/2, "/",self.pitch_range_degree/2

        # let's give the motors 0.3s to set to the zero position
        # we have to give it some times to reach a certain position
        # but we have to stop after sometime the motors because of noise problem
        t_start = time.time()
        yaw_duty_cycle = (self.yaw_angle_zero_pulse / 1000) * self.PWM_FREQUENCY
        pitch_duty_cycle = (self.pitch_angle_zero_pulse / 1000) * self.PWM_FREQUENCY
        while time.time() - t_start <= 0.3:
            #self.yaw_motor_pwm.ChangeDutyCycle(yaw_duty_cycle)
            self.yaw_motor_pwm.ChangeDutyCycle(self.yawDegreeToDutyCycle(0.0))
            self.pitch_motor_pwm.ChangeDutyCycle(self.pitchDegreeToDutyCycle(0.0))
            #self.pitch_motor_pwm.ChangeDutyCycle(pitch_duty_cycle)
        self.yaw_motor_pwm.ChangeDutyCycle(0.0)
        self.pitch_motor_pwm.ChangeDutyCycle(0.0)
        # ----------------------------------------

    def yawDegreeToDutyCycle(self,degree):
        """
            This function converts the yaw degree in the correct PWM's duty cycle (frequenzy 50Hz) for the servo SG90.
            See the degrees_tf.png in "docs" folder.
            :param degree:
            :return: duty cycle
        """
        pulse = ((self.yaw_range_degree / 2 - (150 - self.yaw_angle_zero_pulse)*self.PULSES2DEGREE - degree)) /self.PULSES2DEGREE + self.yaw_min_pulse + (90 - self.yaw_range_degree / 2) /self.PULSES2DEGREE
        if pulse > self.yaw_max_pulse:
            pulse = self.yaw_max_pulse
        elif pulse < self.yaw_min_pulse:
            pulse = self.yaw_min_pulse

        duty = (pulse / 1000) * self.PWM_FREQUENCY

        return duty

    def pitchDegreeToDutyCycle(self, degree):
        """
            This function converts the pitch degree in the correct PWM's duty cycle (frequenzy 50Hz) for the servo SG90.
            See the degrees_tf.png in "docs" folder.
            :param degree:
            :return: duty cycle
        """
        pulse = ((self.pitch_range_degree / 2 - (150 - self.pitch_angle_zero_pulse) * 180 / 200 - degree)) /self.PULSES2DEGREE + self.pitch_min_pulse + (90 - self.pitch_range_degree / 2) /self.PULSES2DEGREE
        if pulse > self.pitch_max_pulse:
            pulse = self.pitch_max_pulse
        elif pulse < self.pitch_min_pulse:
            pulse = self.pitch_min_pulse

        duty = (pulse / 1000) * self.PWM_FREQUENCY

        return duty

    def run(self):
        connection_thread = connection2pc_thread.ConnectionToPc(0, 'Connection Thread', self)
        connection_thread.daemon = True
        connection_thread.start()

        driving_thread = drivingcommand_thread.DrivingCommand(1, 'Driving Thread', self)
        driving_thread.daemon = True
        driving_thread.start()

        cameradriving_thread = cameradrivingcommand_thread.CameraDrivingCommand(2, 'Camera Driving Thread', self)
        cameradriving_thread.daemon = True
        cameradriving_thread.start()

        motors_thread = motorscontroller_thread.MotorsController(3, 'Motors Thread', self)
        motors_thread.daemon = True
        motors_thread.start()

    def cleanMotorsPins(self):
        print 'Cleaning the motors\' pins up.'
        wiringpi.softPwmWrite(self.MOTOR_RIGHT_F, 0)
        wiringpi.softPwmWrite(self.MOTOR_RIGHT_B, 0)
        wiringpi.softPwmWrite(self.MOTOR_LEFT_F, 0)
        wiringpi.softPwmWrite(self.MOTOR_LEFT_B, 0)
        return True


def mapGPIO2WIRINGPI(pin):
    # revision 1:
    # reference: http: // wiringpi.com / pins /

    # the first pin is the GPIO the second one is the numbering of the WiringPi Library
    # bcm_dictionary_map = {1:8,1:9,4:7,17:0,21:2,22:3,10:12,9:13,11:14,14:15,15:16,18:1,23:4,24:5,25:6,8:10,7:11}
    board_dictionary_map = {3:8,5:9,7:7,11:0,13:2,15:3,19:12,21:13,23:14,8:15,10:16,12:1,16:4,18:5,22:6,24:10,26:11}
    return board_dictionary_map[pin]






if __name__ == "__main__":

    try:
        if len(sys.argv) < 2:
            jr = JonnyRobot()
            jr.run()
            print "done - communication style: WIFI"
        else:
            if sys.argv[1] == "-b":
                communication_style = "BLUETOOTH"
            elif sys.argv[1] == "-w":
                communication_style = "WIFI"
            else:
                communication_style = ""
            if communication_style == "WIFI" or communication_style == "BLUETOOTH":
                jr = JonnyRobot(communication_style)
                jr.run()
                print "done - communication style: ", communication_style
            else:
                jr = JonnyRobot()
                jr.run()
                print "done - uncorrect communication style given as input, the robot will communicate via WIFI "
                print "To tune the program: $ sudo python main.py -w/-b"


        while 1: pass # this is necessary in order to make the Keyboard interrupt detectable

    except KeyboardInterrupt:
        print '\nCTRL-C pressed ... exiting...'
        exitFlag = True

        # bring camera servo motors to the home pose
        jr.yaw_motor_pwm.ChangeDutyCycle(jr.yawDegreeToDutyCycle(0.0))
        jr.pitch_motor_pwm.ChangeDutyCycle(jr.pitchDegreeToDutyCycle(0.0))
        time.sleep(0.3)
        jr.yaw_motor_pwm.stop()
        jr.pitch_motor_pwm.stop()

        while not jr.cleanMotorsPins():
            pass
        GPIO.cleanup()
        quit()
