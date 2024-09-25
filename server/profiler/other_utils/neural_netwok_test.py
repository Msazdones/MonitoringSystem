import config as cfg

from sklearn.metrics import precision_recall_curve

def parse_file_for_training(config, db_conn):
    for host in config["clients"]:
        jsondata = []
        
        #esto hay que revisarlo que funciona regular ahora con los cambios realizados
        if(config["samples"] == "all"):
            rawdata = db_conn[host].find({},{"_id": 0})

        else:
            rawdata = reversed(list(db_conn[host].find({},{"_id": 0}).sort({"_id": -1}).limit(config["samples"])))

        stepcnt = config["step"] - 1 #para quedarnos siempre con la primera muestra
        cnt = 0
        for d in rawdata:
            jsondata.append(d)

        if(len(jsondata) == 0):
            continue
        
        data = []
        # revisar esto para optimizarlo

        for jd in jsondata:
            date = cfg.datetime.strptime(str(jd["date"]), "%Y-%m-%d %H:%M:%S")
            timestamp = int(date.timestamp())

            data.append([timestamp, jd["name"], jd["label"], jd["data"]["pid"], float(jd["data"]["CPU"]), float(jd["data"]["RAM"]), float(jd["data"]["RDISK"]), float(jd["data"]["WDISK"])])

        df = cfg.pd.DataFrame(data, columns=["Timestamp", "Prname", "Label", "PID", "CPU", "RAM", "RDISK", "WDISK"])
        df = df.sort_values(["Timestamp"])

        return df

def train(X_train):
    dim_entrada = X_train.shape[1]
    capa_entrada = cfg.layers.Input(shape=(dim_entrada,))

    encoder = cfg.layers.Dense(20, activation='tanh')(capa_entrada)
    encoder = cfg.layers.Dense(14, activation='relu')(encoder)
    
    decoder = cfg.layers.Dense(20, activation='tanh')(encoder)
    decoder = cfg.layers.Dense(dim_entrada, activation='relu')(decoder)

    autoencoder = cfg.models.Model(inputs=capa_entrada, outputs=decoder)

    sgd = cfg.optimizers.SGD(learning_rate=0.01)
    autoencoder.compile(optimizer='sgd', loss='mse')

    nits = 100
    tam_lote = 32
    autoencoder.fit(X_train, X_train, epochs=nits, batch_size=tam_lote, shuffle=True, verbose=1)

    return autoencoder

def predict(ae, X_test):
    X_pred = ae.predict(X_test)

    ecm = cfg.np.mean(cfg.np.power(X_test-X_pred,2), axis=1)

    umbral_fijo = 0.5
    #Si el error cuadrático medio es mayor que el umbral, es un positivo
    Y_pred = cfg.np.array([0 if e > umbral_fijo else 1 for e in ecm])
    
    print("Prob")
    print(len(cfg.np.where(Y_pred == 0)[0]) / len(Y_pred))

    return ecm

def encode_categoricals(df):
    cod = []
    interval = None
    
    if "Instant" in df.columns:

        for c in df["Instant"]:
            cod.append((int(c.split(":")[0]) * 60) + int(c.split(":")[1]))
        
        cod = cfg.pd.Series(cod)

        df["Instant"] = cod

    elif "Interval" in df.columns:

        for c in df["Interval"]:
            t0 = c.split("-")[0]
            t1 = c.split("-")[1]
            m0 = (int(t0.split(":")[0]) * 60) + int(t0.split(":")[1])
            m1 = (int(t1.split(":")[0]) * 60) + int(t1.split(":")[1])

            cod.append(m0 + m1)
            
            if interval == None:
                interval = m1 - m0

        df["Interval"] = cod

    return df, interval

def process_R_and_W(df):
    df = df.drop(["Prname", "PID"], axis=1)
    df = df.groupby(["Timestamp", "Label"], as_index=False).sum()
    df = df.set_index(["Timestamp"])
    df["Timestamp"] = df.index.values

    df_sh = df.shift(1)

    df["RDISK"] = (df["RDISK"] - df_sh["RDISK"]) / (df["Timestamp"] - df_sh["Timestamp"])
    df["WDISK"] = (df["WDISK"] - df_sh["WDISK"]) / (df["Timestamp"] - df_sh["Timestamp"])

    df.iat[0, 3] = 0
    df.iat[0, 4] = 0

    df = df.drop(["Timestamp"], axis=1)

    return df


traindatapath = ""

df = cfg.pd.read_csv(traindatapath)
Y = df["Label"]
if len(Y.unique()) > 1:
    for l in Y.unique():
        Y = Y.replace(l, Y.unique()[0])

X = df.drop(["Label", "Timestamp"], axis=1)
X, i = encode_categoricals(X)

scaler = cfg.MinMaxScaler()
scaler.fit(X)

X = cfg.pd.DataFrame(scaler.transform(X), columns=X.columns.values) 

ae = train(X)

config = {"pr_target" : "global", "clients" : ["Client_192_168_50_201"], "step" : 1, "samples" : "all"}
X_anom = parse_file_for_training(config, cfg.aux.connect_to_db())
config = {"pr_target" : "global", "clients" : ["Client_192_168_50_202"], "step" : 1, "samples" : "all"}
X_normal = parse_file_for_training(config, cfg.aux.connect_to_db())

X_anom = cfg.aux.process_R_and_W(X_anom)
X_normal = cfg.aux.process_R_and_W(X_normal)

X_anom = X_anom.drop(["Label"], axis = 1)
dates = X_anom.index.values

instants = []
for d in dates:      
    date = cfg.datetime.fromtimestamp(d)
    instants.append(str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2))
X_anom["Instant"] = instants

X_normal = X_normal.drop(["Label"], axis = 1)
dates = X_normal.index.values


instants = []     
for d in dates:      
    date = cfg.datetime.fromtimestamp(d)
    instants.append(str(date.hour).zfill(2) + ":" + str(date.minute).zfill(2))
X_normal["Instant"] = instants

X_anom, i = encode_categoricals(X_anom)
X_normal, i = encode_categoricals(X_normal)

X_anom = cfg.pd.DataFrame(scaler.transform(X_anom), columns=X.columns.values) 
X_normal = cfg.pd.DataFrame(scaler.transform(X_normal), columns=X.columns.values) 

print("Comportamiento anómalo")
predict(ae, X_anom)

print("Comportamiento normal")
predict(ae, X_normal)
pass