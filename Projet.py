from multiprocessing.connection import Client
import pymongo
from pymongo import MongoClient
from sklearn.neighbors import NeighborhoodComponentsAnalysis
from sqlalchemy import distinct
import matplotlib.pyplot as plt
import os
from bokeh.plotting import figure, show, output_file
from bokeh.tile_providers import get_provider, Vendors
import numpy as np
import datetime



###########################DEFINITION DE FONCTION############################################################


def coor_wgs84_to_web_mercator(lon, lat):
    k = 6378137
    x = lon * (k * np.pi/180.0)
    y = np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return (x,y)

#####################CONNEXION A LA BDD##################################################################

dbURI="mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(dbURI)
db=client['doctolib']
coll=db['dump_Jan2022']
#######################################################################################






p = figure(x_axis_type="mercator", y_axis_type="mercator",active_scroll="wheel_zoom", title="Première carte",x_range=(-2000000, 6000000), y_range=(-1000000, 7000000),)
tile_provider = get_provider(Vendors.CARTODBPOSITRON)
p.add_tile(tile_provider)


rennes={"type": "Point", "coordinates": [-1.665177375354294, 48.117037996514576]}
date1=datetime.datetime.strptime("2022/01/26", "%Y/%m/%d")
date2=datetime.datetime.strptime("2022/01/30", "%Y/%m/%d")
#{"visit_motives.slots":{"$gte": date1, "$lt": date2}
cursor=coll.find({"location":{"$near": {"$geometry": rennes,"$maxDistance": 50000}}})

for line in cursor[0:100]:
    print(line['visit_motives'])
    print("\n")
    xy=coor_wgs84_to_web_mercator(line["location"]["coordinates"][0],line["location"]["coordinates"][1])
    p.diamond(xy[0],xy[1],color='red',size=10)

show(p)


