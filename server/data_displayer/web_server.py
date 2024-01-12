from flask import Flask, render_template, session
import json
import pandas as pd
import plotly
import plotly.express as px
from flask_socketio import SocketIO, emit
from threading import Lock
import multiprocessing as mp

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
    
    #esto será sustituido por una respuesta a un click en el proceso determinado
    display_info.update({'current_proc' : lPROCINFO[0]})
    #lCPU, lRAM, lRDISK, lWDISK, time_limit = get_plot_data()
    #print(lPROCINFO[0], lCPU)
    #print(list(range(time_limit[0],time_limit[1]+1)), time_limit)
    #socketio.emit('actualize_plots', {'time': list(range(time_limit[0],time_limit[1]+1)), 'CPU_data': lCPU, 'time_limit': time_limit})
    #
    socketio.emit('actualize_proc_list', {'proc_list':lPROCINFO, 'eid':message["eid"]})

def background_thread():
    """Example of how to send server generated events to clients."""
    time_data = list(range(0,101))
    while True:
        print("Sending")    
        lCPU, lRAM, lRDISK, lWDISK, time_limit = get_plot_data()
        print(lCPU)
        socketio.emit('actualize_plots', {'time': time_data, 'CPU_data': lCPU, 'time_limit': time_limit})
        socketio.sleep(10)

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
    if display_info.get('current_host') != None:
        c = connect_to_db()[display_info.get('current_host')]

        data = c.find({},{"_id": 0})
        readed_data = {}
        for d in data:
            readed_data.update(d)

        dates = list(readed_data.keys())

        if(len(dates) < 101):
            time_limits = [0,len(dates)-1]
        else:
            index_to_pop = len(dates) - 100 
            for i in range(0, index_to_pop):
                readed_data.pop(dates[i])
            for i in range(0, index_to_pop):
                del dates[i]
            time_limits = [0,100]

        list_of_cpu = []
        list_of_ram = []
        list_of_rdisk = []
        list_of_wdisk = []

        for d in dates:
            for p in readed_data[d]:
                if p["pid"] == display_info.get('current_proc')[5]:
                    list_of_cpu.append(p["CPU"])
                    list_of_ram.append(p["RAM"])
                    list_of_rdisk.append(p["RDISK"])
                    list_of_wdisk.append(p["WDISK"])

        return list_of_cpu, list_of_ram, list_of_rdisk, list_of_wdisk, time_limits
    else:
        return [], [], [], [], []

if __name__ == '__main__':
    socketio.run(app)