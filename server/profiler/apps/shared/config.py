from pymongo import MongoClient
from itertools import islice
from itertools import product
import os
import sys 
import time
from datetime import datetime
import re
import time
import subprocess
import socket
import numpy as np
import statistics as st
import pandas as pd
from sklearn import preprocessing
from sklearn.model_selection import train_test_split
from sklearn import svm
from sklearn.ensemble import IsolationForest
#import tensorflow as tf
import joblib

import auxiliar_functions as aux

#parser and trainer configuration
def_normal_data_dir = "./learning_and_detection/data_files/normal_mode/" #../.
def_advanced_data_dir = "./learning_and_detection/data_files/advanced_mode/"
def_step = 1
def_samples = 20
def_output_model_dir = "./learning_and_detection/models/"
def_output_model_svm_dir = def_output_model_dir + "svm/"
normal_csv_headers = "CPU,RAM,RDISK,WDISK"
advanced_csv_headers = "CPU (mean),CPU (median),CPU (mode),CPU (variance),RAM (mean),RAM (median),RAM (mode),RAM (variance),RDISK (mean),RDISK (median),RDISK (mode),RDISK (variance),WDISK (mean),WDISK (median),WDISK (mode),WDISK (variance)"
all_metrics = ["mean", "median", "mode", "variance"]

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

#multiprocessing
nmprocess = 2