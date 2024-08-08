import config as cfg

def train_model(config):
    tgfiles = []

    for prname in config["input_data"]:
        csvfile = prname[0].split("_")[0] + "_all.csv"
        
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

    h = config["datatype"]
    h.append("Instant") if config["mode"] == 0 else h.append("Interval")
    
    for fn in tgfiles:
        df = cfg.pd.read_csv(config["input_dir"] + fn)
        df = df[h]
        df, interval = encode_categoricals(df)

        if config["alg"] == "svm":
            model = train_svm(df, interval)
        
        elif config["alg"] == "iforest":
            model = train_iforest(df, interval)

        mode = "normal" if config["mode"] == 0 else "advanced"

        cfg.joblib.dump(model, cfg.def_output_model_dir + config["alg"] + "/" + mode + "_" + config["alg"] + "_" + fn.split(".")[0] + ".pkl")

        #model.save(cfg.models_directory + config["alg"] + fn.split(".")[0] + ".keras")

def encode_categoricals(df):
    cod = []
    interval = None
    
    if "Instant" in df.columns:

        for c in df["Instant"]:
            cod.append((int(c.split(":")[0]) * 60) + int(c.split(":")[1]))
        
        cod = cfg.pd.Series(cod)

        interval = cod.unique()[1] - cod.unique()[0]

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

def train_svm(data, interval):
    X_train = data.dropna()
    #X_train = cfg.preprocessing.StandardScaler().fit_transform(data)
    #Y_train = cfg.pd.Series([0 for x in range(0, data.shape[0])])

    model = cfg.svm.OneClassSVM(verbose=True)
    model.fit(X_train)
    
    model.interval = interval

    return model

def train_iforest(data, interval):
    X_train = data.dropna()

    model = cfg.IsolationForest(random_state=0).fit(X_train)
    model.fit(X_train)

    model.interval = interval

    return model


"""def train_svm_tf(data):
    def hinge_loss(y_true, y_pred):    
        return cfg.tf.maximum(0., 1- y_true*y_pred)

    #X_train, X_val, Y_train, Y_val = cfg.train_test_split(data, cfg.pd.Series([0 for x in range(0, data.shape[0])]), test_size=0.2, random_state=42)
    X_train = data
    Y_train = cfg.pd.Series([0 for x in range(0, data.shape[0])])

    X_train_tf = cfg.tf.convert_to_tensor(X_train)
    
    normalizer = cfg.tf.keras.layers.Normalization(axis=-1)
    normalizer.adapt(X_train_tf)

    #model = cfg.tf.keras.Sequential([normalizer, cfg.tf.keras.layers.Dense(10, activation='relu'), cfg.tf.keras.layers.Dense(10, activation='relu'), cfg.tf.keras.layers.Dense(1)])
    #model.compile(optimizer='adam', loss=cfg.tf.keras.losses.BinaryCrossentropy(from_logits=True), metrics=['accuracy'])

    model = cfg.tf.keras.Sequential([normalizer])
    model.add(cfg.tf.keras.layers.Dense(1, activation='linear', kernel_regularizer=cfg.tf.keras.regularizers.l2()))
    model.compile(optimizer='adam', loss=hinge_loss)

    model.fit(X_train_tf, Y_train, epochs=15, batch_size=2) #verbose=False

    #Z = model.predict(X_val)

    return model"""