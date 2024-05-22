from pymongo import MongoClient
from itertools import islice
import os
import sys 
import time
from datetime import datetime
import re
import time
import subprocess
import socket
import numpy as np

import auxiliar_functions as aux

#parser and trainer configuration
def_data_dir = "./learning_and_detection/data_files/"
def_step = 1
def_samples = 20
def_output_model_dir = "./learning_and_detection/models/"
def_output_model_svm_dir = def_output_model_dir + "svm/"
csv_headers = "DATETIME,CPU,RAM,RDISK,WDISK,TOTALTIME"

path_to_training_binary = "./learning_and_detection/sourcecode/profilerstandaloneApplication/profiler"

#detector configuration
models_directory = "./learning_and_detection/models/"

detection_data_dir = "./learning_and_detection/detection_info/"
data_input_dir = "/input/"
data_output_dir = "/output/"

path_to_detector_binary = "./learning_and_detection/sourcecode/detect_anomaliesstandaloneApplication/detect_anomalies"

#log
LOG_HEADERS = "State,Datetime,AnomalyScore,AnomalyState,PID,Algorithm,DataDatetime,CPU(%),RAM(%),RDISK(Bytes),WDISK(Bytes),TOTALTIME(s)\n"
log_route = "./learning_and_detection/log/"

#auxiliary
DATABASE_DIR = "mongodb://127.0.0.1:27017/"
DATABASE_DB = "test"

#matlab configuration
matlab_dependencies_root = "/usr/local/MATLAB/R2023b/"
matlab_dependencies = ["/runtime/glnxa64", "/bin/glnxa64", "/sys/os/glnxa64", "/sys/opengl/lib/glnxa64"]