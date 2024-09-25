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

def train(X_train, y_train):
    model = cfg.Sequential()

    model.add(cfg.layers.Dense(64, activation='relu', input_dim=X_train.shape[1]))
    model.add(cfg.layers.Dense(32, activation='relu'))
    model.add(cfg.layers.Dense(2, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=10, batch_size=32)

    return model

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
testdatapath = ""

dftrain = cfg.pd.read_csv(traindatapath)
dftest= cfg.pd.read_csv(testdatapath)

dftrain, i = encode_categoricals(dftrain)
dftest, i = encode_categoricals(dftest)

ytrain = dftrain["Label"]
dftrain = dftrain.drop(["Label", "Timestamp"], axis=1)

ytest = dftest["Label"]
dftest = dftest.drop(["Label", "Timestamp"], axis=1)

######################################

scaler = cfg.MinMaxScaler() 

scaler = cfg.MinMaxScaler() 
scaler.fit(dftrain)
dftrain = cfg.pd.DataFrame(scaler.transform(dftrain), columns=dftrain.columns.values)
dftest = cfg.pd.DataFrame(scaler.transform(dftest), columns=dftest.columns.values)

#X_train, X_test, Y_train, Y_test = cfg.train_test_split(X_data, Y_data, test_size=0.33, random_state=42)

le = cfg.LabelEncoder().fit(ytrain)

Y_train = le.transform(ytrain)
Y_test = le.transform(ytest)

Y_trainn = cfg.to_categorical(Y_train)
Y_testn = cfg.to_categorical(Y_test)


model = train(dftrain, Y_trainn)

loss, accuracy = model.evaluate(dftest, Y_testn)
print('Accuracy:', accuracy)