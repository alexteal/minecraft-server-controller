from flask import Flask
from flask_cors import CORS
import os
import boto3
import threading
import time
import paramiko
import os

app = Flask(__name__)
CORS(app)  # This will enable CORS for all routes
ec2 = boto3.client('ec2')

INSTANCE_ID=os.getenv('INSTANCE_ID')
MINECRAFT_SERVER=os.getenv('MINECRAFT_SERVER')

def execute_ssh_command(host, command):
    ssh_config = paramiko.SSHConfig()
    user_config_file = os.path.expanduser("~/.ssh/config")
    if os.path.exists(user_config_file):
        with open(user_config_file) as f:
            ssh_config.parse(f)
    cfg = {'hostname': host, 'username': None, 'port': 22}
    user_config = ssh_config.lookup(cfg['hostname'])
    for k in ('hostname', 'username', 'port'):
        if k in user_config:
            cfg[k] = user_config[k]
    if 'identityfile' in user_config:
        cfg['key_filename'] = user_config['identityfile']
    client = paramiko.SSHClient()
    client.load_system_host_keys()
    client.set_missing_host_key_policy(paramiko.WarningPolicy())
    client.connect(cfg['hostname'], cfg['port'], cfg['username'], key_filename=cfg.get('key_filename'))
    stdin, stdout, stderr = client.exec_command(command)
    output = stdout.read().decode('utf-8')
    error = stderr.read().decode('utf-8')
    client.close()
    return output, error


def stop_server():
    ec2.stop_instances(InstanceIds=[INSTANCE_ID])

class Timer:
    def __init__(self, seconds, target):
        self.target = target
        if(seconds > 3600):
            seconds = 3600
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
        if(new_interval > 3600):
            new_interval = 3600
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
    output, error = execute_ssh_command(MINECRAFT_SERVER, 'mscs status atm8')
    if(error == None):
        return {'status': output}
    return {'status': error}
   
if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')

