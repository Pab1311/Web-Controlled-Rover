# Web streaming example
# Source code from the official PiCamera package
# http://picamera.readthedocs.io/en/latest/recipes2.html#web-streaming

PAGE="""\
<html>
<head>
<script src="https://ajax.googleapis.com/ajax/libs/jquery/3.1.1/jquery.min.js"></script>
<title>Raspberry Pi - Surveillance Camera</title>
</head>
<body>
<center><h1>Raspberry Pi - Surveillance Camera</h1></center>
<img src="stream.mjpg" width="820" height="660" style = "position:absolute; left: 160px; top: 60px;">
<img src="http://73.28.42.31:8081" style = "position:absolute; left: 80px; top: 20px;"/> <!--Enter the IP Address of your Raspberry Pi-->
<div style="float:right">

</div>
<div style=" height:400px; width:300px; position: absolute; right: 100px; bottom: 220px;">
<center>
<h1><span style="color:#5C5C5C;">Circuit</span><span style="color:#139442"> Digest</span></h1>
<h2>Surveillance Robot</h2><br><br>
<a href="#" id="up" style="font-size:30px;text-decoration:none;">  &#x1F881;<br>Forward</a><br><br></center>
<a href="#" id="left" style="font-size:30px;text-decoration:none;"> &#x1F880; Left</a>&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;&nbsp;
<a href="#" id="right" style="font-size:30px; text-decoration:none; position : absolute; left: 200px; top; 250px"> Right &#x1F882;</a><br><br>
<center><a href="#" id="down" style="font-size:30px;text-decoration:none;"> Backward<br> &#x1F883;</a></center>
</div>
</body>
<script>
$( document ).ready(function(){
    $("#down").on("mousedown", function() {
     $.get('/down_side');
     }).on('mouseup', function() {
     $.get('/stop');
    });
    $("#up").on("mousedown", function() {
     $.get('/up_side');
     }).on('mouseup', function() {
     $.get('/stop');
    });
    $("#left").on("mousedown", function() {
     $.get('/left_side');
     }).on('mouseup', function() {
     $.get('/stop');
    });
    $("#right").on("mousedown", function() {
     $.get('/right_side');
     }).on('mouseup', function() {
     $.get('/stop');
    });
});
</script>
</html>
"""

import io
import picamera
import logging
import socketserver
import RPi.GPIO as GPIO
import time
from flask import Flask
from flask import render_template, request, redirect, url_for, make_response
from threading import Condition
from http import server

class StreamingOutput(object):
    def __init__(self):
        self.frame = None
        self.buffer = io.BytesIO()
        self.condition = Condition()

    def write(self, buf):
        if buf.startswith(b'\xff\xd8'):
            # New frame, copy the existing buffer's content and notify all
            # clients it's available
            self.buffer.truncate()
            with self.condition:
                self.frame = self.buffer.getvalue()
                self.condition.notify_all()
            self.buffer.seek(0)
        return self.buffer.write(buf)

class StreamingHandler(server.BaseHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(301)
            self.send_header('Location', '/index.html')
            self.end_headers()
        elif self.path == '/index.html':
            content = PAGE.encode('utf-8')
            self.send_response(200)
            self.send_header('Content-Type', 'text/html')
            self.send_header('Content-Length', len(content))
            self.end_headers()
            self.wfile.write(content)
        elif self.path == '/stream.mjpg':
            self.send_response(200)
            self.send_header('Age', 0)
            self.send_header('Cache-Control', 'no-cache, private')
            self.send_header('Pragma', 'no-cache')
            self.send_header('Content-Type', 'multipart/x-mixed-replace; boundary=FRAME')
            self.end_headers()
            try:
                while True:
                    with output.condition:
                        output.condition.wait()
                        frame = output.frame
                    self.wfile.write(b'--FRAME\r\n')
                    self.send_header('Content-Type', 'image/jpeg')
                    self.send_header('Content-Length', len(frame))
                    self.end_headers()
                    self.wfile.write(frame)
                    self.wfile.write(b'\r\n')
            except Exception as e:
                logging.warning(
                    'Removed streaming client %s: %s',
                    self.client_address, str(e))
        else:
            self.send_error(404)
            self.end_headers()

class StreamingServer(socketserver.ThreadingMixIn, server.HTTPServer):
    allow_reuse_address = True
    daemon_threads = True

with picamera.PiCamera(resolution='820x660', framerate=24) as camera:
    output = StreamingOutput()
    #Uncomment the next line to change your Pi's Camera rotation (in degrees)
    camera.rotation = 180
    camera.start_recording(output, format='mjpeg')
    try:
        address = ('', 8000)
        server = StreamingServer(address, StreamingHandler)
        server.serve_forever()
    finally:
        camera.stop_recording()

#app = Flask(__name__, template_folder='template')

m11=17
m12=27
m21=23
m22=24

GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(m11, GPIO.OUT)
GPIO.setup(m12, GPIO.OUT)
GPIO.setup(m21, GPIO.OUT)
GPIO.setup(m22, GPIO.OUT)
GPIO.output(m11 , 0)
GPIO.output(m12 , 0)
GPIO.output(m21, 0)
GPIO.output(m22, 0)
app = Flask(__name__) #set up flask server
#when the root IP is selected, return index.html page
@app.route('/')
def index():
    return render_template('index.html')
#recieve which pin to change from the button press on index.html
#each button returns a number that triggers a command in this function
#
#Uses methods from motors.py to send commands to the GPIO to operate the motors
@app.route('/<changepin>', methods=['POST'])
def reroute(changepin):
    changePin = int(changepin) #cast changepin to an int
    if changePin == 1:
        print ("Left")
        GPIO.output(m11 , 0)
        GPIO.output(m12 , 0)
        GPIO.output(m21 , 1)
        GPIO.output(m22 , 0)
    elif changePin == 2:
        print ("Forward")
        GPIO.output(m11 , 1)
        GPIO.output(m12 , 0)
        GPIO.output(m21 , 1)
        GPIO.output(m22 , 0)
    elif changePin == 3:
        print ("Right")
        GPIO.output(m11 , 1)
        GPIO.output(m12 , 0)
        GPIO.output(m21 , 0)
        GPIO.output(m22 , 0)
    elif changePin == 4:
        print ("Reverse")
        GPIO.output(m11 , 0)
        GPIO.output(m12 , 1)
        GPIO.output(m21 , 0)
        GPIO.output(m22 , 1)
    else:
        GPIO.output(m11 , 0)
        GPIO.output(m12 , 0)
        GPIO.output(m21 , 0)
        GPIO.output(m22 , 0)
    response = make_response(redirect(url_for('index')))
    return(response)
app.run(debug=True, host='0.0.0.0', port=8000) #set up the server in debug mode to the port 8000

"""
GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(m11, GPIO.OUT)
GPIO.setup(m12, GPIO.OUT)
GPIO.setup(m21, GPIO.OUT)
GPIO.setup(m22, GPIO.OUT)

# Preset so its not moving
GPIO.output(m11 , 0)
GPIO.output(m12 , 0)
GPIO.output(m21, 0)
GPIO.output(m22, 0)


@app.route("/")
def index():
    return render_template('index.html')

@app.route('/left_side')
def left_side():
    data1="LEFT"
    GPIO.output(m11 , True)
    GPIO.output(m12 , True)
    GPIO.output(m21 , True)
    GPIO.output(m22 , False)
    return 'true'

@app.route('/right_side')
def right_side():
   data1="RIGHT"
   GPIO.output(m11 , False)
   GPIO.output(m12 , True)
   GPIO.output(m21 , True)
   GPIO.output(m22 , True)
   return 'true'

@app.route('/up_side')
def up_side():
   data1="FORWARD"
   GPIO.output(m11 , False)
   GPIO.output(m12 , True)
   GPIO.output(m21 , True)
   GPIO.output(m22 , False)
   return render_template('index.html')

@app.route('/down_side')
def down_side():
   data1="BACK"
   GPIO.output(m11 , True)
   GPIO.output(m12 , False)
   GPIO.output(m21 , False)
   GPIO.output(m22 , True)
   return 'true'

@app.route('/stop')
def stop():
   data1="STOP"
   GPIO.output(m11 , False)
   GPIO.output(m12 , False)
   GPIO.output(m21 , False)
   GPIO.output(m22 , False)
   return  'true'

if __name__ == "__main__":
 app.run(host='0.0.0.0',port=5000)"""
