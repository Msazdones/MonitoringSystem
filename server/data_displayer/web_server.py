from flask import Flask, render_template, session
import json
import pandas as pd
import plotly
import plotly.express as px
from flask_socketio import SocketIO, emit
from threading import Lock
import multiprocessing as mp
import re

from pymongo import MongoClient

app = Flask(__name__, static_url_path='',  static_folder='web/static', template_folder='web/templates')
socketio = SocketIO(app, cors_allowed_origins="*")

thread = None
thread_lock = Lock()

manager = mp.Manager()
display_info = manager.dict()

@app.route('/')
def plots():
    return render_template('bar.html')

@socketio.event
def connect():
    print("Connected")
    time_data = list(range(0,101))
    global thread
    with thread_lock:
        display_info.update({"prueba" : "test"})
    with thread_lock:
        if thread is None:
            with app.app_context():
                thread = socketio.start_background_task(background_thread)
    emit('actualize_plots', {'time': time_data, 'CPU_data': [], 'time_limit': [0,100]})

@socketio.event
def host_list(message):
    if message["data"] == "get_hosts":
        lHOST = connect_to_db().list_collection_names()
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
def connect_to_db():
    client = MongoClient("mongodb://127.0.0.1:27017/")
    return client["test"]

def get_hosts_list():
    return connect_to_db().list_collection_names()

def get_process_list():
    c = connect_to_db()[display_info.get('current_host')]
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
    print(display_info)
    if display_info.get('current_host') != None:
        c = connect_to_db()[display_info.get('current_host')]

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