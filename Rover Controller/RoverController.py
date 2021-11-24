from flask import Flask, render_template, request, Response
import RPi.GPIO as GPIO
import cv2
import socket
import io

app = Flask(__name__, template_folder='template', static_folder='static')
realUsername = "Bob1234"
realPassword = "NetworksRock"

# Set camera capture to vc
vc = cv2.VideoCapture(0)

# Motor Driver/ GPIO Values:Variables
m11=17 # Orange
m12=27 # Yellow
m21=23 # Green
m22=24 # Grey

# ---GPIO Set up---
GPIO.setwarnings(False) # Avoid Error
GPIO.setmode(GPIO.BCM)  # SOC channel set
GPIO.setup(m11, GPIO.OUT) # Setting m11 as OUTPUT
GPIO.setup(m12, GPIO.OUT)
GPIO.setup(m21, GPIO.OUT)
GPIO.setup(m22, GPIO.OUT)

# Preset to ensure rover in not moving on start
GPIO.output(m11 , 0)
GPIO.output(m12 , 0)
GPIO.output(m21, 0)
GPIO.output(m22, 0)

# Renders html file (Loads Website)
@app.route("/")
def index():
    return render_template('/login.html')

@app.route('/login', methods = ['POST', 'GET'])
def login():
    if(request.method == 'POST'):
        username = request.form.get('username')
        password = request.form.get('password')
        if username == realUsername and password == realPassword:
            return render_template("index.html")
        else:
            return render_template("/wronglogin.html")

# Generate streaming function
def gen():
    while True:
        rval, frame = vc.read()
        cv2.imwrite('stream.jpg', frame)
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + open('stream.jpg', 'rb').read() + b'\r\n')


# Returns the video feed to html file
@app.route('/video_feed')
def video_feed():
    return Response(gen(),
                    mimetype='multipart/x-mixed-replace; boundary=frame')

# Sets GPIO's to left movement
@app.route('/left_side')
def left_side():
    data1="LEFT"
    GPIO.output(m11 , True)
    GPIO.output(m12 , True)
    GPIO.output(m21 , True)
    GPIO.output(m22 , False)
    return 'true'

# Sets GPIO's to right movement
@app.route('/right_side')
def right_side():
   data1="RIGHT"
   GPIO.output(m11 , False)
   GPIO.output(m12 , True)
   GPIO.output(m21 , True)
   GPIO.output(m22 , True)
   return 'true'

# Sets GPIO's to forward movement
@app.route('/up_side')
def up_side():
   data1="FORWARD"
   GPIO.output(m11 , False)
   GPIO.output(m12 , True)
   GPIO.output(m21 , True)
   GPIO.output(m22 , False)
   return 'true'

# Sets GPIO's to reverse movement
@app.route('/down_side')
def down_side():
   data1="BACK"
   GPIO.output(m11 , True)
   GPIO.output(m12 , False)
   GPIO.output(m21 , False)
   GPIO.output(m22 , True)
   return 'true'

# Sets GPIO's to stop
@app.route('/stop')
def stop():
   data1="STOP"
   GPIO.output(m11 , False)
   GPIO.output(m12 , False)
   GPIO.output(m21 , False)
   GPIO.output(m22 , False)
   return 'true'

# Host website
if __name__ == "__main__":
 app.run(host='0.0.0.0',port=5000)

# Releasing the VideoCapture to avoid Out of resources error.
vc.release()
