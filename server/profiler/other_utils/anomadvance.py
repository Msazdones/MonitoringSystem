import config as cfg

def train_nn(X_train, y_train):
    model = cfg.Sequential()

    model.add(cfg.layers.Dense(64, activation='relu', input_dim=X_train.shape[1]))
    model.add(cfg.layers.Dense(32, activation='relu'))
    model.add(cfg.layers.Dense(3, activation='softmax'))

    model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
    model.fit(X_train, y_train, epochs=10, batch_size=32)

    return model

def train_svm(X_train, Y_train):
    model = cfg.svm.SVC()
    model.fit(X_train, Y_train)
    
    return model

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

traindatapath = ""
testdatapath = ""

dftrain = cfg.pd.read_csv(traindatapath)
dftest = cfg.pd.read_csv(testdatapath)

features = ["CPU", "RAM", "RDISK", "WDISK", "Instant"]

Y_train = dftrain["Label"]
Y_test = dftest["Label"]
Y_test[Y_test == "anomaly_behaviour"] = "maliciouswebserver"

dftrain = dftrain[features]
dftest = dftest[features]

dftrain, i = encode_categoricals(dftrain)
dftest, i = encode_categoricals(dftest)

scaler = cfg.MinMaxScaler() 
scaler.fit(dftrain)

dftrain = cfg.pd.DataFrame(scaler.transform(dftrain), columns=dftrain.columns.values) 
dftest = cfg.pd.DataFrame(scaler.transform(dftest), columns=dftest.columns.values) 

le = cfg.LabelEncoder().fit(Y_train)

Y_train = le.transform(Y_train)
Y_test = le.transform(Y_test)

Y_trainn = cfg.to_categorical(Y_train)
Y_testn = cfg.to_categorical(Y_test)


model = train_nn(dftrain, Y_trainn)

#model = train_svm(dftrain, Y_train)

scores = model.predict(dftest)

#preds = model.predict(dftest)
#ecm = cfg.np.mean(cfg.np.power(dftest - preds, 2), axis=1)

#status = cfg.np.array([0 if e > 0.5 else 1 for e in ecm])


pass