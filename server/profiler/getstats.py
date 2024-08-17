import config as cfg

df = cfg.pd.read_csv("C:/Users/Miguel\Desktop\\tfm2\code\MonitoringSystem\MonitoringSystem\server\profiler\learning_and_detection\data_files\\normal_mode\global_global.csv")
print("CPU:", df["CPU"].mean(), "RAM:", df["RAM"].mean(), "RDISK:", df["RDISK"].mean(), "WDISK:", df["WDISK"].mean())

pass