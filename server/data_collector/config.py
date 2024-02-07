import multiprocessing as mp
import datetime
import socket
from pymongo import MongoClient
import select
import ssl
import re

import reception_system as rs
import data_management_system as dms
import reception_system as rec

MAX_BLIND_DATA = 1000000000
DECODING = "latin-1"
ACK_MSG = b"OK"
HOST = "127.0.0.1"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
MAX_CLIENTS = 5

MONGO_DIR = "mongodb://127.0.0.1:27017/"
DB = "test"
COLLECTION = "Client_"