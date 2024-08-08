import multiprocessing as mp
import datetime
import socket
from pymongo import MongoClient
import select
import ssl
import re
from hashlib import sha256

import reception_system as rs
import data_management_system as dms
import reception_system as rec

MAX_BLIND_DATA = 1000000000
MAX_CLIENTS = 5
DECODING = "latin-1"
ACK_MSG = b"OK"
NACK_MSG = b"NOK"
PASS_REQ = b"PASS"
PASS_RES = "AUTH"
DATA_SIZE = "SIZE"

HOST = "192.168.50.16"  # Standard loopback interface address (localhost)
PORT = 65432  # Port to listen on (non-privileged ports are > 1023)
MAX_CLIENTS = 5

MONGO_DIR = "mongodb://127.0.0.1:27017/"
DB = "test"
DB_CREDS = "credentials"
COLLECTION = "Client_"

credsCOLL = "credentials"