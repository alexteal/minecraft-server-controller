from flask import Flask
from flask_cors import CORS
import os
import boto3
import threading
import time
import subprocess
import os
import traceback

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
ec2 = boto3.client('ec2')

INSTANCE_ID=os.getenv('INSTANCE_ID')
MINECRAFT_SERVER=os.getenv('MINECRAFT_SERVER')

def run_command(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, shell=True)
    output, error = process.communicate()
    if error:
        raise Exception(error)
    return output.decode()

# Example usage:
output = run_command("ls -l")
print(output)

def stop_server():
    ec2.stop_instances(InstanceIds=[INSTANCE_ID])
    print("stopping server")
    traceback.print_stack()

class Timer:
    def __init__(self, seconds, target):
        self.target = target
        if seconds > 3600:
            seconds = 3600
        self.thread = threading.Timer(seconds, self.target)
        self.start_time = time.time()
        self.is_running = False  # Add a flag to check if the timer is running
    def start(self):
        self.thread.start()
        self.is_running = True
    def cancel(self):
        self.thread.cancel()
        self.is_running = False
    def increase(self, seconds):
        if self.thread.is_alive():
            remaining = self.thread.interval - (time.time() - self.start_time)
            new_interval = remaining + seconds
            if new_interval > 3600:
                new_interval = 3600
            self.thread.interval = new_interval
            self.start_time = time.time()
        else:
            self.start()
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
    try:
        return response['Reservations'][0]['Instances'][0]['PublicIpAddress']
    except Exception as e:
        print(e)
        return 'too early to check for ip. refresh page!'
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

@app.route('/status')
def get_system_status():
    output = run_command('ssh '+ str(MINECRAFT_SERVER) +' "mscs status atm8"')
    return {'status': output}
   
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


