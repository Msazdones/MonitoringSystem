import config as cfg

def connect_to_db():
    client = cfg.MongoClient("mongodb://127.0.0.1:27017/")
    return client["test"]

def get_db_info(db_conn):
   return db_conn.list_collection_names()

def check_numeric_input(i, ll, hl):
    if (not i.isnumeric()):
        return False
    
    ii = int(i)
    if(hl == "-"):
        if (ii < ll):
            return False
    else:
        if ((ii < ll) or (ii > hl)):
            return False
    return True

def check_float_input(f, ll, hl):
    try:
        ff = float(f)
        
        if(hl == "-"):
            if (ff < ll):
                return False
        else:
            if ((ff < ll) or (ff > hl)):
                return False
        
        return True
    except:
        return False

def print_choosing_list(l):
    col = 0
    i = 0
    for c in l:
        cadena = "(" + str(i) + ") " + c
        print(cadena + " " * (60 - (len(cadena))),  end="")
        i = i + 1
        if col == 3:
            print() 
            col = 0
        else:
            col = col + 1 