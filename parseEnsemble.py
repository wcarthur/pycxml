import logging
import pandas as pd
import geopandas as gpd

logger = logging.getLogger()
xmlfile = r"C:\WorkSpace\data\tc\cxml\2011013100.xml"

# Build dataframe of ensemble members
members = pd.read_xml(xmlfile, xpath="./data/disturbance")
breakpoint()
for idx, member in members.iterrows():
    print(f"Processing {idx}")
    ID = member.ID
    fixdf = pd.read_xml(xmlfile, xpath=f"./data[@member='{idx}']/disturbance/fix")
    intdf = pd.read_xml(xmlfile, xpath=f"./data[@member='{idx}']/disturbance/fix/cycloneData/maximumWind")
    outdf = fixdf.join(intdf)
    outdf['ensembleMember'] = idx
    outdf['ID'] = member.ID
    outgdf = gpd.GeoDataFrame(outdf, geometry=gpd.points_from_xy(outdf.longitude, outdf.latitude))
    print(f"C:/incoming/que/{ID}.{idx:03d}.geojson")
    outgdf.to_file(f"C:/incoming/que/{ID}.{idx:03d}.geojson", driver="GeoJSON")