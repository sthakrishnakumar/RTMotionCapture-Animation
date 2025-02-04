import cv2 as cv
import mediapipe as mp
import time
import json
import socket


class VideoPoseEstimator:
    def __init__(self, video_path):
        self.key_points = {
            0: "NOSE_TIP",  # 0
            11: "LEFT_SHOULDER",  # 1
            12: "RIGHT_SHOULDER",  # 2
            13: "LEFT_ELBOW",  # 3
            14: "RIGHT_ELBOW",  # 4
            15: "LEFT_WRIST",  # 5
            16: "RIGHT_WRIST",  # 6
            23: "LEFT_HIP",  # 7
            24: "RIGHT_HIP",  # 8
            25: "LEFT_KNEE",  # 9
            26: "RIGHT_KNEE",  # 10
            27: "LEFT_ANKLE",  # 11
            28: "RIGHT_ANKLE",  # 12
            31: "LEFT_FOOT",  # 13
            32: "RIGHT_FOOT"  # 14
        }
        self.keypoints = [
         {
                "name": "NOSE_TIP", 
                "x":1.0, "y":5.5
                },
                {
                "name": "LEFT_SHOULDER", 
                "x":1.1, "y":2.4
                },
                {
                "name": "RIGHT_SHOULDER", 
                "x":1.0, "y":5.5
                },
                {
                "name": "LEFT_ELBOW", 
                "x":1.1, "y":2.4
                },
                {
                "name": "RIGHT_ELBOW", 
                "x":1.0, "y":5.5
                },
                {
                "name": "LEFT_WRIST", 
                "x":1.1, "y":2.4
                },
                {
                "name": "RIGHT_WRIST", 
                "x":1.0, "y":5.5
                },
                {
                "name": "LEFT_HIP", 
                "x":1.1, "y":2.4
                },
                {
                "name": "RIGHT_HIP", 
                "x":1.1, "y":2.4
                },
                {
                "name": "LEFT_KNEE", 
                "x":1.0, "y":5.5
                },
                {
                "name": "RIGHT_KNEE", 
                "x":1.1, "y":2.4
                },
                {
                "name": "LEFT_ANKLE", 
                "x":1.0, "y":5.5
                },
                {
                "name": "RIGHT_ANKLE", 
                "x":1.1, "y":2.4
                },
                {
                "name": "LEFT_FOOT", 
                "x":1.0, "y":5.5
                },
                {
                "name": "RIGHT_FOOT", 
                "x":1.1, "y":2.4
                },
            ]
        self.s = socket.socket()         # Create a socket object
        host = socket.gethostname()       # Get local machine name
        port = 9000                         # Reserve a port for your service.
        self.s.connect((host, port))
        self.connection = True

        self.path = video_path

        self.mPose = mp.solutions.pose
        self.mp_holistic = mp.solutions.holistic
        self.pose = self.mPose.Pose()
        self.joint = {}
        try:
            self.cap = cv.VideoCapture(video_path)
            self.ptime = 0
            print("Camera SetUp Success")
        except:
            print("File not found")

        while self.connection:
            time.sleep = 0.5
            success, self.frame = self.cap.read()

            self.frame = self.resizeImage(self.frame, 40)
            results = self.pose.process(self.frame)

            ctime = time.time()
            fps = 1 / (ctime - self.ptime)
            self.ptime = ctime

            cv.putText(self.frame, f"FPS:{int(fps)}", (30, 30), cv.FONT_HERSHEY_PLAIN, 2, (255, 0, 0), 3)
            self.determinePose(results)
            self.display('frame', self.frame)

            jsonObj = json.dumps(self.keypoints)
            self.s.sendall(bytes(jsonObj, encoding="utf-8"))
            print(f"{self.s.recv(1024)}")

            key = cv.waitKey(1) & 0xFF
            if key == 27:
                self.s.send("exit".encode("UTF-8"))
                connection = False
                self.s.close()
                self.close()

    def determinePose(self, results):
        if results.pose_landmarks:
            for index, lm in enumerate(results.pose_landmarks.landmark):
                if self.key_points.__contains__(index):
                    h, w, c = self.frame.shape
                    cx, cy = int(lm.x * w), int(lm.y * h)
                    value = self.key_points[index]

                    width = int(self.frame.shape[1] * 50 / 100)
                    height = int(self.frame.shape[0] * 50 / 100)
                    
                    cv.putText(self.frame, 
                                f'({round(lm.x, 2)},{round(lm.y, 2)},{round(lm.z, 2)})',
                               (cx - 50, cy + 10), cv.FONT_HERSHEY_PLAIN, 0.8, (0, 255, 55), 1)
                    cv.putText(self.frame, f'({value})', (cx - 50, cy - 10),
                               cv.FONT_HERSHEY_PLAIN, 0.8, (0, 25, 255), 1)

                    if len(self.joint) == len(self.key_points):
                        xdiff = round(abs(lm.x - self.joint[value]['x']), 5)
                        ydiff = round(abs(lm.y - self.joint[value]['y']), 5)
                        zdiff = round(abs(lm.z - self.joint[value]['z']), 5)

                        if xdiff > 0.09 or ydiff > 0.09 or zdiff > 0.09:
                            if lm.visibility > 0.8:
                                print(f'Push Value::{value}--diff::{xdiff},{ydiff},{zdiff}')
                                #self.firebaseAccess.SendData(value, lm.x, lm.y, lm.z)

                    for i in range(0, len(self.key_points)):
                        if(self.keypoints[i]["name"] == value):
                            self.keypoints[i]["x"]=lm.x
                            self.keypoints[i]["y"]=lm.y
                            self.keypoints[i]["z"]=lm.z
                            print(f"{value} (x:{lm.x}, y:{lm.y}, z:{lm.z})")

    def resizeImage(self, image, scalefactor = 50):
        width = int(image.shape[1] * scalefactor / 100)
        height = int(image.shape[0] * scalefactor / 100)
        dim = (width, height)
        image = cv.resize(image, dim, interpolation=cv.INTER_AREA)
        return image

    def display(self, name, image):
        cv.imshow(name, image)

    def close(self):
        self.cap.release()
        cv.destroyAllWindows()
        self.close()
        print('Closed!')


if __name__ == "__main__":
    video = VideoPoseEstimator("Videos/Video01.mp4")
