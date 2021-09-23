import os
import numpy as np
import pandas as pd

PROJECT_DIR = os.path.join(os.path.dirname(os.path.realpath(__file__)), '..')
TMP_DIR = os.path.join(PROJECT_DIR, 'tmp')
LOGS_DIR = os.path.join(PROJECT_DIR, 'logs')

def mag_corr(logname):
    actuator_controls_0_0 = pd.read_csv(os.path.join("D:\\Documentos\\Skyrats\\SkyanalysisTools\\logs\\actuator_controls_0_0", logname))
    vehicle_magnetometer_0 = pd.read_csv(os.path.join("D:\\Documentos\\Skyrats\\SkyanalysisTools\\logs\\vehicle_magnetometer_0", logname))
    actuator_armed_0 = pd.read_csv(os.path.join("D:\\Documentos\\Skyrats\\SkyanalysisTools\\logs\\actuator_armed_0", logname))

    t0 = actuator_armed_0['timestamp'][0]
    vehicle_magnetometer_0['time_rel'] = (vehicle_magnetometer_0['timestamp'] - t0)/1e6
    actuator_controls_0_0['time_rel'] = (actuator_controls_0_0['timestamp'] - t0)/1e6
    vehicle_magnetometer_0['norm'] = np.sqrt(vehicle_magnetometer_0['magnetometer_ga[0]']**2 +
                                vehicle_magnetometer_0['magnetometer_ga[1]']**2 +
                                vehicle_magnetometer_0['magnetometer_ga[2]']**2)

    time_mag = vehicle_magnetometer_0['time_rel'].to_numpy()
    time_thrust = actuator_controls_0_0['time_rel'].to_numpy()
    mag = vehicle_magnetometer_0['norm'].to_numpy()
    thrust = actuator_controls_0_0['control[3]'].to_numpy()

    # seguindo os tempos de time_mag
    t = time_mag[1:] # TODO: quando comecar
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
    
    return np.corrcoef(mag, thrust_sinc)


def main():
    df = pd.DataFrame(columns=["Correlation", "Variance"], index=pd.Series(name="Name"))
    # log_31_...    variancia_mag   correlacao
    for logname in os.listdir(os.path.join(LOGS_DIR, "vehicle_magnetometer_0")):
        actuator_controls_0_0 = pd.read_csv(os.path.join("D:\\Documentos\\Skyrats\\SkyanalysisTools\\logs\\actuator_controls_0_0", logname))
        vehicle_magnetometer_0 = pd.read_csv(os.path.join("D:\\Documentos\\Skyrats\\SkyanalysisTools\\logs\\vehicle_magnetometer_0", logname))
        actuator_armed_0 = pd.read_csv(os.path.join("D:\\Documentos\\Skyrats\\SkyanalysisTools\\logs\\actuator_armed_0", logname))

        t0 = actuator_armed_0['timestamp'][0]
        vehicle_magnetometer_0['time_rel'] = (vehicle_magnetometer_0['timestamp'] - t0)/1e6
        actuator_controls_0_0['time_rel'] = (actuator_controls_0_0['timestamp'] - t0)/1e6
        vehicle_magnetometer_0['norm'] = np.sqrt(vehicle_magnetometer_0['magnetometer_ga[0]']**2 +
                                    vehicle_magnetometer_0['magnetometer_ga[1]']**2 +
                                    vehicle_magnetometer_0['magnetometer_ga[2]']**2)

        time_mag = vehicle_magnetometer_0['time_rel'].to_numpy()
        time_thrust = actuator_controls_0_0['time_rel'].to_numpy()
        mag = vehicle_magnetometer_0['norm'].to_numpy()
        thrust = actuator_controls_0_0['control[3]'].to_numpy()

        # seguindo os tempos de time_mag
        t = time_mag[1:] # TODO: quando comecar
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


        corr = np.corrcoef(mag, thrust_sinc)
        variancia = np.var(mag)
        print(logname, corr[1,0], variancia)
        df.loc[logname] = {"Correlation": corr[1,0], "Variance": variancia}
        # var = np.var(...)
    print(df)
    print(df["Variance"][0])
    df.to_csv("distribution.csv")
        
if __name__ == "__main__":
    main()