import config as cfg
import matplotlib.pyplot as plt

pathtoresultdata = ""

df1 = cfg.pd.read_csv(pathtoresultdata)

y = df1["Score"].to_numpy()
y1 = [eval(yy.replace(" ", ","))[0] for yy in y]
y2 = [eval(yy.replace(" ", ","))[1] for yy in y]

x = df1["Timestamp"].to_numpy()
xx = []
labs = []
for d in x:
    date= cfg.datetime.fromtimestamp(d).strftime('%H:%M:%S')
    xx.append(date)
    
    if date == '14:10:21' or date == '14:10:23' or date == '14:10:27' or date == '14:10:25':
        labs.append(date)
    else:
        labs.append("")


#plt.xticks([0, 2, 5, 10])
pass
# Crear datos
"""x = cfg.np.linspace(0, 10, 100)
y = cfg.np.sin(x)

# Crear el gráfico"""
fig, ax = plt.subplots()
plt.plot(xx, y1, color='green', label="Probabilidad de comportamiento normal", linewidth=3)
plt.plot(xx, y2, color='brown', label="Probabilidad ransomware", linewidth=3)

plt.grid(True)

#plt.axhline(y=0.5, color='black', linestyle='--',  label='Umbral de detección')

plt.axvline(x='14:10:21', color='red', linestyle='--',linewidth=2.5,  label='Inicio/final de la prueba') 
plt.axvline(x='14:10:25', color='red', linestyle='--', linewidth=2.5)
plt.axvline(x='14:10:23', color='blue', linestyle='--', label='Inicio/cese de detección', linewidth=1.5)
plt.axvline(x='14:10:27', color='blue', linestyle='--')

ax.xaxis.set_tick_params(width=2, labelsize=20) 
ax.yaxis.set_tick_params(width=2, labelsize=20)
ax.tick_params(length=8)
ax.legend(loc='upper right', title='Líneas y función', bbox_to_anchor=(4, 6), ncol=3)

plt.xticks(xx, rotation=45, ha='right', va='top', labels=labs)
plt.legend(fontsize=24, frameon=True, framealpha=1, borderpad=1.5, handlelength=1.5)

# Mostrar el gráfico
plt.show()