import config as cfg

def train_model(config):
    tgfiles = []

    for prname in config["input_data"]:
        e = prname[0].split("_")
        csvfile = "_".join(e[0:len(e)-2]) + "_" + e[len(e)-2] + "_all.csv"
        
        if(len(prname) == 1):
            tgfiles.append(prname[0])

        else:
            with open(config["input_dir"] + csvfile, "w") as outfile:
                #outfile.write(h + "\n")
                f = open(config["input_dir"] + prname[0], "r")
                outfile.write(f.read())
                f.close()

                for fname in prname[1::]:
                    
                    with open(config["input_dir"] + fname, "r") as infile: 
                        next(infile)
                        
                        for line in infile:
                            outfile.write(line)
                tgfiles.append(csvfile)

    h = config["datatype"].copy()
    h.append("Instant") if config["mode"] == 0 else h.append("Interval")
    h.append("Label")
    
    for fn in tgfiles:
        df = cfg.pd.read_csv(config["input_dir"] + fn)
        df = df[h]
        df, interval = encode_categoricals(df)

        if config["alg"] == "ocsvm":
            model, scaler = train_ocsvm(df)
        
        elif config["alg"] == "nn_anom":
            model, scaler = train_autoencoder(df)

        elif config["alg"] == "svm":
            model, scaler = train_svm(df)

        elif config["alg"] == "nn_class":
            model, scaler = train_neuralnetwork_classifier(df)

        mode = "normal" if config["mode"] == 0 else "advanced"
        
        features = config["datatype"].copy()
        features.append("Instant") if interval == None else features.append("Interval")

        cfg.joblib.dump((model, scaler, interval, features), cfg.def_output_model_dir + config["alg"] + "/" + mode + "_" + config["alg"] + "_" + fn.split(".")[0] + ".pkl")

        #model.save(cfg.models_directory + config["alg"] + fn.split(".")[0] + ".keras")

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

def train_ocsvm(data):
    X_train = data.dropna()
    X_train = X_train.drop(["Label"], axis=1)

    scaler = cfg.MinMaxScaler()
    scaler.fit(X_train)
    X_train = cfg.pd.DataFrame(scaler.transform(X_train), columns=X_train.columns.values)

    model = cfg.svm.OneClassSVM(verbose=True, nu=0.1)
    model.fit(X_train)

    return model, scaler

def train_svm(data):
    Y_train = data["Label"]
    X_train = data.dropna()
    X_train = X_train.drop(["Label"], axis=1)
    
    scaler = cfg.MinMaxScaler() 
    scaler.fit(X_train)
    X_train = cfg.pd.DataFrame(scaler.transform(X_train), columns=X_train.columns.values)

    model = cfg.svm.SVC()
    model.fit(X_train, Y_train)

    return model

def train_autoencoder(data):
    X_train = data.dropna()
    X_train = X_train.drop(["Label"], axis=1)

    scaler = cfg.MinMaxScaler()
    scaler.fit(X_train)
    X_train = cfg.pd.DataFrame(scaler.transform(X_train), columns=X_train.columns.values) 

    imputdim = X_train.shape[1]
    input_layer = cfg.layers.Input(shape=(imputdim,))

    encoder = cfg.layers.Dense(20, activation='tanh')(input_layer)
    encoder = cfg.layers.Dense(14, activation='relu')(encoder)
    
    decoder = cfg.layers.Dense(20, activation='tanh')(encoder)
    decoder = cfg.layers.Dense(imputdim, activation='relu')(decoder)

    autoencoder = cfg.models.Model(inputs=input_layer, outputs=decoder)

    sgd = cfg.optimizers.SGD(learning_rate=0.01)
    autoencoder.compile(optimizer='sgd', loss='mse')

    nits = 100
    tam_lote = 32
    autoencoder.fit(X_train, X_train, epochs=nits, batch_size=tam_lote, shuffle=True, verbose=1)

    return autoencoder, scaler

def train_neuralnetwork_classifier(data):
    pass