import os
import numpy as np
import pandas as pd

from pycxml import loadfile
from vincenty import vincenty

def sizeparam(R34, Vmax1, Rmax, x):
    V500 = R34/9. - 3.
    V500C = Vmax1*np.power(Rmax/500, x)
    S = V500/V500C
    return np.max(S, 0.4)

def deltaP(Vsrm1, Vmax1, R34, Rmax, x, latitude):
    S = sizeparam(R34, Vmax1, Rmax, x)
    if np.abs(latitude) < 18:
        dp = 5.962 - 0.267 * Vsrm1 - (Vsrm1 / 18.26)**2 - 6.8 * S
    else:
        dp = 23.286 - 0.483 * Vsrm1 - (Vsrm1 / 24.252)**2 - 12.587 * S - 0.483 * latitude

    return dp

def storm_relative(Vmax: float, Vtrans: float) -> float:
    """
    :param float Vmax: 1-minunte sustained wind speed (knots)
    :param float Vtrans: Translation speed of the storm (knots)

    :returns: Storm relative maximum wind speed
    """
    Vsrm = Vmax - 1.5 * Vtrans**0.63
    return Vsrm

def vortex_param(Vmax: float, latitude: float) -> float:
    """
    :param float Vmax: 1-minunte sustained wind speed (knots)
    :param float latitude: Latitude of the storm centre

    :returns: vortex parameter for a modified Rankine vortex
    """
    x = 0.1147 + 0.0055 * Vmax - 0.001 * (np.abs(latitude) - 25.)
    return x

def translation_speed(df: pd.DataFrame) -> pd.DataFrame:
    """
    Update the data frame to include storm translation speed

    :param df: `pd.DataFrame` containing track details (latitude, longitude, timestamp, etc.)
    """
    coords = df[['longitude', 'latitude']].values
    dists = [vincenty(coords[i], coords[i + 1]) for i in range(len(coords) - 1)]
    dt = df.validtime.diff().dt.seconds.values/3600
    #dt = np.diff(df.validtime) / (3600 * np.timedelta64(1, 's'))
    speed = np.zeros(len(df))
    speed[1:] = np.array(dists) / dt[1:]
    df['translation_speed'] = speed * 0.54
    return df

inputFile = r"C:\WorkSpace\data\2011013100.xml"
outputPath = r"C:\incoming\process\cxml"
events = loadfile(inputFile)
print(len(events))
for event in events:
    member = event.iloc[0]['member']
    disturbance = event.iloc[0]['disturbance']
    event['Vmax1'] = 0.54 * event['windspeed'] / 0.88
    # Update the translation speed
    event = translation_speed(event) 
    event['Vsrm'] = event.apply(lambda x: storm_relative(x['Vmax1'], x['translation_speed']), axis=1)
    event['x'] = event.apply(lambda x: vortex_param(x['Vmax1'], x['latitude']), axis=1)
    outfilename = os.path.join(outputPath, f"{disturbance}.{member}.csv")
    event.to_csv(outfilename, float_format="%.2f")
