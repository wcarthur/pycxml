import os
from pycxml.pycxml import loadfile
import numpy as np

inputFile = os.path.expanduser(r"~/geoscience/data/ensembles.xml")
outputPath = os.path.expanduser(r"~/geoscience/data")

events = loadfile(inputFile)
print(f"Number of memebers: {len(events)}")
print("Max dp: ", (events[0].poci - events[0].pcentre).max())
print("min dp: ", (events[0].poci - events[0].pcentre).min())
print("Max pc: ", events[0].pcentre.max())
print("Min pc: ", events[0].pcentre.min())
print("Max penv: ", events[0].poci.max())
print("Min penv: ", events[0].poci.min())
print()
idx = np.argmin(events[0].pcentre)
print(
    events[0].iloc[idx][
        ["validtime", "windspeed", "latitude", "translation_speed", "R34avg", "poci"]
    ]
)
print()
print(events[0].iloc[idx][["R34NEQ", "R34SEQ", "R34SWQ", "R34NWQ"]])

for event in events:
    member = event.iloc[0]["member"]
    disturbance = event.iloc[0]["disturbance"]

    outfilename = os.path.join(outputPath, f"{disturbance}.{member}.csv")
    event.to_csv(outfilename, float_format="%.2f")
