import threading
import wiringpi # PWM
import time

def getPWM(velocity):

    return int(velocity)

class MotorsController(threading.Thread):

    def __init__(self, threadID, name, jr):
        """

        :param threadID: Id of the thread
        :param name: name of the thread
        :param jr: Jonny Robot class
        """
        threading.Thread.__init__(self)

        self.threadID = threadID
        self.name =  name
        self.jr = jr

    def run(self):

        while 1:
            left_pwm = getPWM(self.jr.velocity_left_weel)
            if left_pwm > 0:
                if left_pwm < self.jr.MIN_SPEED:
                    left_pwm = 0
                elif left_pwm > 70:
	                left_pwm = 70
                wiringpi.softPwmWrite(self.jr.MOTOR_LEFT_F, left_pwm)
                wiringpi.softPwmWrite(self.jr.MOTOR_LEFT_B, 0)
            elif left_pwm < 0:
                if left_pwm > - self.jr.MIN_SPEED:
                    left_pwm = 0
                elif left_pwm < - 70:
                    left_pwm = - 70
                wiringpi.softPwmWrite(self.jr.MOTOR_LEFT_F, 0)
                wiringpi.softPwmWrite(self.jr.MOTOR_LEFT_B, -left_pwm)
            else:
                wiringpi.softPwmWrite(self.jr.MOTOR_LEFT_F, 0)
                wiringpi.softPwmWrite(self.jr.MOTOR_LEFT_B, 0)

            right_pwm = getPWM(self.jr.velocity_right_weel)
            if right_pwm > 0:
                if right_pwm < self.jr.MIN_SPEED:
                    right_pwm = 0
                wiringpi.softPwmWrite(self.jr.MOTOR_RIGHT_F, right_pwm)
                wiringpi.softPwmWrite(self.jr.MOTOR_RIGHT_B, 0)
            elif right_pwm < 0:
                if right_pwm > - self.jr.MIN_SPEED:
                    right_pwm = 0
                wiringpi.softPwmWrite(self.jr.MOTOR_RIGHT_F, 0)
                wiringpi.softPwmWrite(self.jr.MOTOR_RIGHT_B, -right_pwm)
            else:
                wiringpi.softPwmWrite(self.jr.MOTOR_RIGHT_F, 0)
                wiringpi.softPwmWrite(self.jr.MOTOR_RIGHT_B, 0)

            wiringpi.delay(1) # 1 ms

            #print "self.jr.new_yaw_angle:,", self.jr.new_yaw_angle
            if self.jr.new_yaw_angle:
                if time.time() - self.jr.new_yaw_angle_arrived < self.jr.camera_motors_max_time:
                    self.jr.yaw_motor_pwm.ChangeDutyCycle(self.jr.yawDegreeToDutyCycle(self.jr.yaw_angle))
                else:
                    self.jr.new_yaw_angle = False
                    self.jr.yaw_motor_pwm.ChangeDutyCycle(0.0)
            if self.jr.new_pitch_angle:
                if time.time() - self.jr.new_pitch_angle_arrived < self.jr.camera_motors_max_time:
                    self.jr.pitch_motor_pwm.ChangeDutyCycle(self.jr.pitchDegreeToDutyCycle(self.jr.pitch_angle))
                else:
                    self.jr.pitch_motor_pwm.ChangeDutyCycle(0.0)
                    self.jr.new_pitch_angle = False
