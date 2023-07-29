from flask import Flask
from flask_cors import CORS
import os
import boto3
import threading
import time
app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
ec2 = boto3.client('ec2')

INSTANCE_ID=os.getenv('INSTANCE_ID')
def stop_server():
    ec2.stop_instances(InstanceIds=[INSTANCE_ID])
class Timer:
    def __init__(self, seconds, target):
        self.target = target
        self.thread = threading.Timer(seconds, self.target)
        self.start_time = time.time()
    def start(self):
        self.thread.start()
    def cancel(self):
        self.thread.cancel()
    def increase(self, seconds):
        self.cancel()
        remaining = self.thread.interval - (time.time() - self.start_time)
        new_interval = remaining + seconds
        self.thread = threading.Timer(new_interval, self.target)
        self.start_time = time.time()
        self.thread.start()
    def get_remaining_time(self):
        if self.thread.is_alive():
            return self.thread.interval - (time.time() - self.start_time)
        else:
            return 0

timer = None
@app.route('/start')
def start_server():
    global timer
    ec2.start_instances(InstanceIds=[INSTANCE_ID])
    timer = Timer(7200, stop_server)
    timer.start()
    return 'Server started'
@app.route('/stop')
def stop_server_route():
    global timer
    if timer:
        timer.cancel()
        stop_server()
    return 'Server stopped'
@app.route('/increase-time')
def increase_time():
    global timer
    if timer:
        timer.increase(3600)
    return 'Server time increased by 1 hour'
@app.route('/ip')
def get_ip():
    response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
    return response['Reservations'][0]['Instances'][0]['PublicIpAddress']
@app.route('/time-left')
def get_time_left():
    global timer
    response = ec2.describe_instances(InstanceIds=[INSTANCE_ID])
    state = response['Reservations'][0]['Instances'][0]['State']['Name']
    if state == 'running':
        if timer:
            remaining_time = timer.get_remaining_time()
            return {"time-left": int(remaining_time)}
        else:
            timer = Timer(3600, stop_server)
            timer.start()
            return {"time-left": 3600}
    else:
        return {"time-left": -1}
if __name__ == '__main__':
    app.run(debug=True)

