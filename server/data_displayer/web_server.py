from flask import Flask, render_template, session, redirect, request
import json
import pandas as pd
import plotly
import plotly.express as px
from flask_socketio import SocketIO, emit
from threading import Lock
import multiprocessing as mp
import re

import hashlib
import random

from pymongo import MongoClient

MONGO_DIR = "mongodb://127.0.0.1:27017/"
MONGO_CRED_DB = "wscreds"
MONGO_DATA_DB = "test"

app = Flask(__name__, static_url_path='',  static_folder='web/static', template_folder='web/templates')

sk = hashlib.sha256()
sk.update(str(random.getrandbits(128)).encode())
app.secret_key = sk.hexdigest()

socketio = SocketIO(app, cors_allowed_origins="*")

thread = None
thread_lock = Lock()

manager = mp.Manager()
display_info = manager.dict()

@app.route('/dashboard')
def plots():
    if 'logged_in' not in session:
        return redirect("http://127.0.0.1:5000/login")

    else:
        if session['logged_in']:
            return render_template('bar.html')
        else:
            return redirect("http://127.0.0.1:5000/login")
        

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/login_creds', methods=['POST'])
def logincreds():
    c = connect_to_db(MONGO_CRED_DB)["credentials"]

    user = re.sub('[^A-Za-z0-9]+', '', request.form["user"])
    h = hashlib.sha256()
    h.update(request.form["password"].encode())
    passwd = h.hexdigest()
    
    data = c.find_one({user : passwd},{"_id": 0})
    if data == None:
        return render_template('login.html')
    else:
        session['logged_in'] = True
        return redirect("http://127.0.0.1:5000/dashboard")

@app.route('/logout')
def logout():
    session['logged_in'] = False
    return redirect("http://127.0.0.1:5000/login")

@socketio.event
def connect():
    print("Connected")
    time_data = list(range(0,101))
    global thread
    with thread_lock:
        if thread is None:
            with app.app_context():
                thread = socketio.start_background_task(background_thread)
    emit('actualize_plots', {'time': time_data, 'CPU_data': [], 'time_limit': [0,100]})

@socketio.event
def host_list(message):
    if message["data"] == "get_hosts":
        lHOST = connect_to_db(MONGO_DATA_DB).list_collection_names()
        socketio.emit('actualize_host_list', {'hosts':lHOST})

@socketio.event
def selected_host(message):
    display_info.update({'current_host' : message["data"]})
    lPID, lPROCNAME = get_process_list()
    lPROCINFO = ["Pid: " + lPID[i] + " - ProcName: " + lPROCNAME[i] for i in range(0,len(lPID))]

    display_info.update({'current_proc_name' : lPROCNAME[0], 'current_proc_pid' : lPID[0]})
    socketio.emit('actualize_proc_list', {'proc_list':lPROCINFO, 'eid':message["eid"]})

@socketio.event
def selected_proc(message):
    procname = re.findall("\(.*\)", message["data"])[0]
    procpid = re.findall("Pid: .* -", message["data"])[0]
    procpid = procpid[5:len(procpid)-2]

    display_info.update({'current_proc_name' : procname, 'current_proc_pid' : procpid})

def background_thread():
    """Example of how to send server generated events to clients."""
    time_data = list(range(0,101))
    while True:
        print("Sending")   
        lCPU, lRAM, lRDISK, lWDISK, time_limit, pclimit, rdlimit, wdlimit = get_plot_data()
        socketio.emit('actualize_plots', {'time': time_data, 'CPU_data': lCPU, 'RAM_data' : lRAM, 'RDISK_data' : lRDISK, 'WDISK_data' : lWDISK, 'time_limit': time_limit, 'percent_limit' : pclimit, 'rd_limit' : rdlimit, 'wdlimit' : wdlimit})
        socketio.sleep(2)

#DataBase Management
def connect_to_db(db):
    client = MongoClient(MONGO_DIR)
    return client[db]

def get_hosts_list():
    return connect_to_db(MONGO_DATA_DB).list_collection_names()

def get_process_list():
    c = connect_to_db(MONGO_DATA_DB)[display_info.get('current_host')]
    data = c.find({},{"_id": 0})
    readed_data = {}
    for d in data:
        readed_data.update(d)

    last_date = list(readed_data.keys())
    last_date = last_date[len(last_date)-1]

    list_of_pid = []
    list_of_procnames = []

    for p in readed_data[last_date]:
        list_of_pid.append(p["pid"])
        list_of_procnames.append(p["name"])

    return list_of_pid, list_of_procnames

def get_plot_data():
    if display_info.get('current_host') != None:
        c = connect_to_db(MONGO_DATA_DB)[display_info.get('current_host')]

        #data = c.find({},{"_id": 0})
        data = reversed(list(c.find({},{"_id": 0}).sort({"_id": -1}).limit(100)))
        readed_data = {}
        for d in data:
            readed_data.update(d)

        dates = list(readed_data.keys())
        time_limits = [0, len(dates)-1]

        list_of_cpu = []
        list_of_ram = []
        list_of_rdisk = []
        list_of_wdisk = []
        
        for d in dates:
            for p in readed_data[d]:
                if p["pid"] == display_info.get('current_proc_pid') and p["name"] == display_info.get('current_proc_name'):
                    list_of_cpu.append(float(p["CPU"]))
                    list_of_ram.append(float(p["RAM"]))
                    list_of_rdisk.append(int(p["RDISK"])/1000000)
                    list_of_wdisk.append(int(p["WDISK"])/1000000)

        percentlimit = [0, 100]
        rdlimit = [0, max(list_of_rdisk) + 10]
        wdlimit = [0, max(list_of_wdisk) + 10]

        return list_of_cpu, list_of_ram, list_of_rdisk, list_of_wdisk, time_limits, percentlimit, rdlimit, wdlimit
    else:
        return [], [], [], [], [], [], [], []

if __name__ == '__main__':
    socketio.run(app)