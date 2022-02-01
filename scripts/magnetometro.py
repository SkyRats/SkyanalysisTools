import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

from sklearn.linear_model    import LinearRegression
from sklearn.naive_bayes     import GaussianNB

PROJECT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
LOGS_DIR = os.path.join(PROJECT_DIR, 'logs')

def read_log(logname):
    actuator_controls_0_0 = pd.read_csv(os.path.join(LOGS_DIR, "actuator_controls_0_0", logname))
    vehicle_magnetometer_0 = pd.read_csv(os.path.join(LOGS_DIR, "vehicle_magnetometer_0", logname))
    actuator_armed_0 = pd.read_csv(os.path.join(LOGS_DIR, "actuator_armed_0", logname))

    t0 = actuator_armed_0['timestamp'][0]
    vehicle_magnetometer_0['time_rel'] = (vehicle_magnetometer_0['timestamp'] - t0)/1e6
    actuator_controls_0_0['time_rel'] = (actuator_controls_0_0['timestamp'] - t0)/1e6
    vehicle_magnetometer_0['norm'] = np.sqrt(
                                vehicle_magnetometer_0['magnetometer_ga[0]']**2 +
                                vehicle_magnetometer_0['magnetometer_ga[1]']**2 +
                                vehicle_magnetometer_0['magnetometer_ga[2]']**2)
    
    return actuator_controls_0_0, vehicle_magnetometer_0, actuator_armed_0

def mag_regr(logname, wl):
    angular = []
    linear = []
    actuator_controls_0_0, vehicle_magnetometer_0, actuator_armed_0 = read_log(logname)
    
    x = np.asarray(vehicle_magnetometer_0['time_rel']).reshape(-1, 1)
    y = np.asarray(vehicle_magnetometer_0['norm']).reshape(-1, 1)

    for i in range(int(len(x)/wl)-1):
        reg = LinearRegression().fit(x[i*wl:(i+1)*wl], y[i*wl:(i+1)*wl])
        linear.append(reg.intercept_[0])
        angular.append(reg.coef_[0,0])

    
    return angular, linear

def mag_corr(logname):
    actuator_controls_0_0, vehicle_magnetometer_0, actuator_armed_0 = read_log(logname)

    time_mag = vehicle_magnetometer_0['time_rel'].to_numpy()
    time_thrust = actuator_controls_0_0['time_rel'].to_numpy()
    mag = vehicle_magnetometer_0['norm'].to_numpy()
    thrust = actuator_controls_0_0['control[3]'].to_numpy()

    # Sincroniza as duas séries nos tempos de time_mag
    i0 = 0
    while time_mag[i0] < time_thrust[0]:
        i0 += 1
    t = time_mag[i0:]
    mag = mag[1:] # mag tá sincronizado com t
    thrust_sinc = []
    for i in range(len(t)):
        j = 0 # 1o time_thrust que é maior que t
        while time_thrust[j] < t[i]:
            j += 1
        
        # entre j-1 e j
        # (thr - thrust[j-1])/(t[i] - time_thrust[j-1]) = (thrust[j] - thrust[j-1])/(time_thrust[j] - time_thrust[j-1])
        thr = thrust[j-1] + (thrust[j] - thrust[j-1])/(time_thrust[j] - time_thrust[j-1])*(t[i] - time_thrust[j-1])
        thrust_sinc.append(thr)

    thrust_sinc = np.asarray(thrust_sinc)
    
    return np.corrcoef(mag, thrust_sinc)[0,1]
    

    
def main():
    logInput = input("Digite o nome do log: ")
    lognames  = ["log_21_2021-8-12-18-27-34.csv"] # Aqui são cada log |||Vamo pegar isso de fora ja pronto ne?
    magStatus = [1] #Aqui fala se o log é bom ou não, um booleano

    cont = 0
    corr = []
    angular = []
    linear = []
    for logname in lognames # Calcula os coef de corr e ang e linear de cada log
        corr[cont] = mag_corr(logname)
        angular[cont], linear[cont] = mag_regr(logname, 100)

    #print(f"Correlação entre o módulo do campo magnético e o thrust: \n {corr} \n")
    #print(f"Coeficientes ang e lin: \n {np.mean(angular)}, {np.mean(linear)} \n")
    X_data  = pd.dataframe([corr, angular, linear], columns = "Corr", "Angular", "Linear")
    Y_data  = pd.dataframe(magStatus, columns = "Status")

    nb = GaussianNB()
    nb.fit(X_data, Y_data)

    angInp, linInp = mag_regr(logname, 100)
    X_predict = pd.dataframe([mag_corr(logInpu), angInp, linInp] 
    result  = nb.predict(X_predict)



if __name__ == "__main__":
    main()
