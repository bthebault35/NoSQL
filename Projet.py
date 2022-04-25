from multiprocessing.connection import Client
import pymongo
from pymongo import MongoClient
from sklearn.neighbors import NeighborhoodComponentsAnalysis
from sqlalchemy import distinct
import matplotlib.pyplot as plt
import os
from math import sqrt
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool,ColumnDataSource,Div, Column
from bokeh.tile_providers import get_provider, Vendors
import numpy as np
import pandas as pd
import datetime
from bokeh.io import curdoc

curdoc().theme = 'light_minimal' #thème des graphique

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





rennes={"type": "Point", "coordinates": [-1.665177375354294, 48.117037996514576]}
date1=datetime.datetime.strptime("2022/01/26", "%Y/%m/%d")
date2=datetime.datetime.strptime("2022/01/30", "%Y/%m/%d")

#première requete pour récupérer les centres qui ont des créneaux aux dates correspondantes et ne garder que ces créneaux
creneau_entre_date=coll.find({"location":{"$near": {"$geometry": rennes,"$maxDistance": 50000}},
                  "visit_motives.slots":{"$elemMatch":{"$gte":date1,"$lt":date2}}},{"name":True,"visit_motives":True,"location.coordinates":True})

#2e requete pour récupérer les centres qui n'ont pas de creneaux sur la période
not_creneau=coll.find({"location":{"$near": {"$geometry": rennes,"$maxDistance": 50000}},
                  "$nor": [{"visit_motives.slots":{"$gte":date1,"$lt":date2}}]},{"name":True,"visit_motives":True,"location.coordinates":True})


coordx,coordy,name,creneau,color,legend=[],[],[],[],[],[]
for line in creneau_entre_date:
    nb_creneau=0
    for motives in line['visit_motives']:
        nb_creneau+=len(motives['slots'])
    xy=coor_wgs84_to_web_mercator(line["location"]["coordinates"][0],line["location"]["coordinates"][1])
    coordx.append(xy[0])
    coordy.append(xy[1])
    name.append(line["name"])
    creneau.append(nb_creneau)
    if nb_creneau > 500:
        color.append("green")
        legend.append("Plus de 500")
    else:
        color.append("orange")
        legend.append("Entre 1 et 500")



for line in not_creneau:
    xy=coor_wgs84_to_web_mercator(line["location"]["coordinates"][0],line["location"]["coordinates"][1])
    coordx.append(xy[0])
    coordy.append(xy[1])
    name.append(line["name"])
    creneau.append(0)
    color.append("red")
    legend.append("Aucun")



#Création de la carte
map = figure(x_axis_type="mercator", y_axis_type="mercator",active_scroll="wheel_zoom", title="Centres de vaccination autour de Rennes, créneaux du 26 au 29 Janvier 2022",toolbar_location=None,width=1000,height=800)
tile_provider = get_provider(Vendors.CARTODBPOSITRON)
map.add_tile(tile_provider)
df=pd.DataFrame({"name":name,"x":coordx,"y":coordy,"creneau":creneau,"color":color,"legende":legend})

lst_label=np.unique(legend) #liste des 3 labels

#Pour avoir une légende intéractive, on trace label par label
for label in lst_label:
    df_label=df[df["legende"]==label]
    source=ColumnDataSource(df_label)
    map.circle("x","y",color='color',size=15,source=source,legend_group="legende")
    hover_tool = HoverTool(tooltips=[('Centre', '@name'),('Nombre de crénaux', '@creneau')])
    map.add_tools(hover_tool)

#Paramètres graphiques
map.legend.title = "Nombre de créneaux"
map.legend.label_text_font = "times"
map.legend.label_text_font_style = "bold"
map.legend.label_text_color = "black"
map.legend.border_line_width = 3
map.legend.border_line_color = "black"
map.legend.border_line_alpha = 1
map.legend.background_fill_color = "white"
map.legend.background_fill_alpha = 1
map.legend.click_policy="hide"
map.legend.location="top_right"
map.xgrid.grid_line_color = None
map.ygrid.grid_line_color = None
map.xaxis.major_label_text_color = None
map.yaxis.major_label_text_color = None
map.xaxis.major_tick_line_color = None
map.xaxis.minor_tick_line_color = None
map.yaxis.major_tick_line_color = None
map.yaxis.minor_tick_line_color = None
map.yaxis.axis_line_color = None
map.xaxis.axis_line_color = None



########################################################
texte1=Div(text="""
<style>
body { 
    background-color: #2A2B2C; 
    text-align: justify;
    text-justify:inter-word;
    }
.bk-root .bk-tab {
    background-color: grey;
    width: 33%;
    color: white;
    font-style: italic;
    font-size: 20px;
}

.bk-root .bk-tabs-header .bk-tab.bk-active{
background-color: white;
color: #2A2B2C;
font-style: normal;
font-weight: bold;
}

.bk-root .bk-tabs-header .bk-tab:hover{
background-color: white;
color: #2A2B2C;
}


</style>

<body>
<font color="white" size="4" face="Bookman Old Style, Book Antiqua, Garamond">
<h2> Carte des centres de vaccination</h3>
</br>
</br>
</font></body>""")



texte2=Div(text="""
<body>
<font color="white" size="4" face="Bookman Old Style, Book Antiqua, Garamond">
</br>
</br>
<p> Cette carte nous montre que sur les 25 centres de vaccinations situés à moins de 50km de Rennes, plus de la moitié n'ont effectué de vaccination entre le 26 et le 29 Janvier 2022</p>
</font></body>""")

layout=Column(texte1,map,texte2)
show(layout)


