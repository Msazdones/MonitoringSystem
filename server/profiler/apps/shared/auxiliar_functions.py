import config as cfg

def connect_to_db():
    client = cfg.MongoClient(cfg.DATABASE_DIR)
    return client[cfg.DATABASE_DB]

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


def print_pr_options(l):
    pr = {}
    
    for c in l: 
        try:
            p = c.split("_")
            pname = p[0]
            pid = p[1].replace(".csv", "")

            if(pname not in pr.keys()):
                pr.update({pname : [pid]})
            
            else:
                pr[pname].append(pid)   
        except:
            pass

    i = 0
    
    for c in pr.keys():
        cadena = "(" + str(i) + ")" + c
        print(cadena + ":", str(pr[c]))
        i += 1
        print()
    
    tpl = [(x, pr[x]) for x in pr.keys()]
    return tpl

def print_options(l):
    col = 0
    i = 0
    for c in l:
        cadena = "(" + str(i) + ") " + c
        print(cadena + " " * (60 - (len(cadena))),  end="")
        i += 1
        if col == 3:
            print() 
            col = 0
        else:
            col += 1 

def process_R_and_W(df):
    df = df.drop(["Prname", "PID"], axis=1)
    df = df.groupby("Timestamp").sum()
    df["Timestamp"] = df.index.values

    df_sh = df.shift(1)

    df["RDISK"] = (df["RDISK"] - df_sh["RDISK"]) / (df["Timestamp"] - df_sh["Timestamp"])
    df["WDISK"] = (df["WDISK"] - df_sh["WDISK"]) / (df["Timestamp"] - df_sh["Timestamp"])

    df.iat[0, 2] = 0
    df.iat[0, 3] = 0

    df = df.drop(["Timestamp"], axis=1)

    return df

def get_encoded_instants(df):
    dates = df.index.values
    
    instants = []
    for d in dates:
        date = cfg.datetime.fromtimestamp(d)
        instants.append((date.hour * 60) + date.minute)

    df["Instant"] = instants

    return df