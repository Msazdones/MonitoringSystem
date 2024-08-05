import config as cfg

def train_model(config):
    """cfg.os.environ["LD_LIBRARY_PATH"] = ""
    for d in cfg.matlab_dependencies:
        cfg.os.environ["LD_LIBRARY_PATH"] += cfg.matlab_dependencies_root + d + cfg.os.pathsep

    if(config["alg"] == "svm"):
        binary = cfg.path_to_training_binary
    elif(config["alg"] == "iforest"):
        binary = cfg.path_to_training_binary"""
    
    if(config["mode"] == 0):
        h = cfg.normal_csv_headers
    elif(config["mode"] == 1):
        h = cfg.advanced_csv_headers

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

    for fn in tgfiles:
        train_svm(config["input_dir"] + fn)

    #df = df.apply(LabelEncoder().fit_transform) 

    #clf = cfg.sklearn.svm.OneClassSVM(gamma='auto').fit()
    #clf.predict()
    #clf.score_samples(X)

    """for i in tgfiles:
        i = "'" + i + "'"
        execution = 'eval ' + '"' + binary + '"' + ' "' + config["input_dir"] + i + '" "' + config["alg"] + '" "' + ",".join(config["datatype"]) + '" "' + config["output_dir"] + '"'
        print(execution)
        cfg.os.system(execution)"""


def train_svm(fname):
    #carga de datos 
    df = cfg.pd.read_csv(fname)
    cfg.tf.convert_to_tensor(df)

    #preprocesado de datos 

    normalizer = cfg.tf.keras.layers.Normalization(axis=-1)
    normalizer.adapt(df)
    normalizer(df)
    #

    """df = cfg.pd.read_csv(fname)
    df = df.drop(["Timestamp", "Prname", "PID"], axis = 1)
    df["Instant"] = cfg.preprocessing.LabelEncoder().fit_transform(df["Instant"])"""
    
    #X_train, X_test, y_train, y_test = cfg.train_test_split(df.drop(["label"], axis=1), df["label"], test_size=1 / 3)
    #clf = cfg.svm.OneClassSVM(gamma='auto').fit(df)
    
    
    pass
    """categorical_cols = ['color', 'ciudad']

    # Aplica LabelEncoder
    for col in categorical_cols:
        le = LabelEncoder()
        df[col] = le.fit_transform(df[col])"""
