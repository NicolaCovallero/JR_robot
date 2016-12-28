import threading
import time
import math
import bluetooth


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

        if self.jr.communication_style == "WIFI":

            while 1:

                success, d = self.jr.camera_driving_socket.receiveData()
                self.updateValues(success,d[0].split('/'))

        else:

            bluetooth.advertise_service(self.jr.camera_driving_socket, "jr_camera_driving_service",
                                        service_id=self.jr.CAMERA_DRIVING_SERVICE_UUID,
                                        service_classes=[self.jr.CAMERA_DRIVING_SERVICE_UUID, bluetooth.SERIAL_PORT_CLASS],
                                        profiles=[bluetooth.SERIAL_PORT_PROFILE],
                                        #                   protocols = [ OBEX_UUID ]
                                        )

            try:
                self.jr.camera_driving_socket_client_sock, self.jr.camera_driving_socket_client_sock_info = self.jr.camera_driving_socket.accept()
                print
                "Connection established for CAMERA DRIVING service, acceptd from", self.jr.camera_driving_socket_client_sock_info
            except IOError:
                print
                "IOError in driving accepting connection"

            timeout = 0.05
            self.jr.camera_driving_socket_client_sock.settimeout(timeout)
            while True:
                try:
                    d = self.jr.camera_driving_socket_client_sock.recv(1024)
                    if len(d) > 0:
                        self.updateValues(True, d.split('/'))
                    else:
                        print
                        "wrong command sent to DRIVING service"
                except IOError, e:
                    self.updateValues(False, None)


    def updateValues(self,success,data):
        yaw_angle = self.jr.yaw_angle
        pitch_angle = self.jr.pitch_angle
        if success:
            # parsing the input
            # The command should be defined by a string as:
            # COMMAND/ANGLE (e.g.: pitch/57.3)

            #print "command: ", data
            if not data.__len__() == 4:
                print "Error receiving the CAMERA DRIVING command. Not correct number of arguments in the string"
                print "received: ", data.join()
            else:
                self.jr.yaw_angle_old = self.jr.yaw_angle
                self.jr.pitch_angle_old = self.jr.pitch_angle
                if data[2] == 'pitch':
                    pitch_angle = float(data[3])
                    self.jr.new_pitch_angle = True
                    self.jr.new_pitch_angle_arrived = time.time()
                if data[0] == 'yaw':
                    self.jr.new_yaw_angle = True
                    self.jr.new_yaw_angle_arrived = time.time()
                    yaw_angle = float(data[1])

        self.jr.yaw_angle = self.yawSaturation(yaw_angle)
        self.jr.pitch_angle = self.pitchSaturation(pitch_angle)
