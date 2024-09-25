import config as cfg

resultpath = ""

df = cfg.pd.read_csv(resultpath)
print("CPU:", df["CPU"].mean(), "RAM:", df["RAM"].mean(), "RDISK:", df["RDISK"].mean(), "WDISK:", df["WDISK"].mean())
