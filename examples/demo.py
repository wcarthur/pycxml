import os
from pycxml.pycxml import loadfile

inputFile = os.path.expanduser(r"~/geoscience/data/2011013100.xml")
outputPath = os.path.expanduser(r"~/geoscience/data")

events = loadfile(inputFile)
print(len(events))

print(events[0].head()[["latitude", "pcentre", "windspeed", "rmax", "poci"]])

for event in events:
    member = event.iloc[0]['member']
    disturbance = event.iloc[0]['disturbance']

    outfilename = os.path.join(outputPath, f"{disturbance}.{member}.csv")
    event.to_csv(outfilename, float_format="%.2f")
