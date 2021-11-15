from flask import Flask
from flask import render_template, request
import RPi.GPIO as GPIO
import time

app = Flask(__name__, template_folder='template')

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

# Preset to ensure rover in not moving on start
GPIO.output(m11 , 0)
GPIO.output(m12 , 0)
GPIO.output(m21, 0)
GPIO.output(m22, 0)

@app.route("/")
def index():
    return render_template('/webpage.html')

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
   return 'true'

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
   return 'true'

if __name__ == "__main__":
 app.run(host='0.0.0.0',port=5000)
