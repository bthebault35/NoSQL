#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 11:48:00 2022
@author: theocavenne
"""

from pymongo import MongoClient
from bokeh.plotting import figure, show
from bokeh.models import HoverTool,ColumnDataSource, Div
from bokeh.tile_providers import get_provider, Vendors
from bokeh.layouts import column
import numpy as np
import pandas as pd
from bokeh.io import curdoc


curdoc().theme = 'light_minimal' #thème des graphique


###########################DEFINITION DE FONCTION############################################################

#Fonction pour mettre les coordonnées au bon format
def coor_wgs84_to_web_mercator(lon, lat):
    k = 6378137
    x = lon * (k * np.pi/180.0)
    y = np.log(np.tan((90 + lat) * np.pi/360.0)) * k
    return (x,y)
#######################################################################################







#####################CONNEXION A LA BDD##################################################################

dbURI="mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(dbURI)
db=client['food']
coll=db['NYfood']
#######################################################################################



#######################################################################################
#Requete NoSQL
#######################################################################################


#Liste des notes associées aux restaurants français de New-York
list_NYfood=list(coll.aggregate([
    {"$unwind":"$grades"},
    {"$match":{"cuisine":"French"}},
    {"$group":{"_id":{"Name":"$name","Borough":"$borough","Address":"$address.street","coord":"$address.loc.coordinates","Note":"$grades.grade"},"Nb_notes":{"$sum":1}}},
    {"$sort":{"_id":1}}
]))

#Création d'une variable pour chaque type de note ('A', 'B', 'C', 'P', 'Z', 'Not Yet Graded') pour chaque restaurant
#afin d'obtenir un dataframe avec chaque restaurant et ses nombres de notes pour chaque type de note.
name,borough,adress,latitude,longitude,nb_a,nb_b,nb_c,nb_p,nb_z,nb_nyg=[],[],[],[],[],[],[],[],[],[],[]
for ligne in list_NYfood:
    name.append(ligne["_id"]["Name"])
    borough.append(ligne["_id"]["Borough"])
    X,Y=coor_wgs84_to_web_mercator(ligne["_id"]["coord"][0],ligne["_id"]["coord"][1])
    latitude.append(Y)
    longitude.append(X)
    adress.append(ligne["_id"]["Address"])
    if ligne["_id"]["Note"]=='A':
        nb_a.append(ligne["Nb_notes"])
        nb_b.append(0)
        nb_c.append(0)
        nb_p.append(0)
        nb_z.append(0)
        nb_nyg.append(0)
    elif ligne["_id"]["Note"]=='B':
        nb_a.append(0)
        nb_b.append(ligne["Nb_notes"])
        nb_c.append(0)
        nb_p.append(0)
        nb_z.append(0)
        nb_nyg.append(0)
    elif ligne["_id"]["Note"] == 'C':
        nb_a.append(0)
        nb_b.append(0)
        nb_c.append(ligne["Nb_notes"])
        nb_p.append(0)
        nb_z.append(0)
        nb_nyg.append(0)
    elif ligne["_id"]["Note"] == 'P':
        nb_a.append(0)
        nb_b.append(0)
        nb_c.append(0)
        nb_p.append(ligne["Nb_notes"])
        nb_z.append(0)
        nb_nyg.append(0)
    elif ligne["_id"]["Note"] == 'Z':
        nb_a.append(0)
        nb_b.append(0)
        nb_c.append(0)
        nb_p.append(0)
        nb_z.append(ligne["Nb_notes"])
        nb_nyg.append(0)
    else:
        nb_a.append(0)
        nb_b.append(0)
        nb_c.append(0)
        nb_p.append(0)
        nb_z.append(0)
        nb_nyg.append(ligne["Nb_notes"])

df=pd.DataFrame({'Name':name,
                 'Borough':borough,
                 'Latitude':latitude,
                 'Longitude':longitude,
                 'Addresse':adress,
                 'A':nb_a,
                 'B':nb_b,
                 'C':nb_c,
                 'P':nb_p,
                 'Z':nb_z,
                 'NotYetGraded':nb_nyg
                 })

#Regroupent par restaurant
newdf=df.groupby(['Name','Borough','Latitude','Longitude','Addresse'],as_index=False).sum()


#######################################################################################
#Création de la carte
#######################################################################################


source=ColumnDataSource(newdf)

p = figure(x_axis_type="mercator",
           y_axis_type="mercator",
           active_scroll="wheel_zoom",
           title="Restaurants français de New-York",
           x_range=(-8245000,-8225000), y_range=(4955000,4995000),
           toolbar_location=None)

tile_provider = get_provider(Vendors.CARTODBPOSITRON)

p.add_tile(tile_provider)

p.scatter(x="Longitude",y="Latitude",source=source,size =5,alpha=0.5)

TOOLTIPS = [
    ('Nom', '@Name'),
    ('Quartier', '@Borough'),
    ('Adresse', '@Addresse'),
    ('Notes',''),
    ('A', '@A'),
    ('B', '@B'),
    ('C', '@C'),
    ('P', '@P'),
    ('Z', '@Z')]

hover_tool = HoverTool(tooltips=TOOLTIPS)

p.add_tools(hover_tool)
p.xgrid.grid_line_color = None
p.ygrid.grid_line_color = None
p.xaxis.major_label_text_color = None
p.yaxis.major_label_text_color = None
p.xaxis.major_tick_line_color = None
p.xaxis.minor_tick_line_color = None
p.yaxis.major_tick_line_color = None
p.yaxis.minor_tick_line_color = None
p.yaxis.axis_line_color = None
p.xaxis.axis_line_color = None


#######################################################################################
#Mise en page
#######################################################################################



entete=Div(text="""
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
<h2> Carte des restaurants français de New York</h2>
</br>
</br>
</font></body>""")

texte=Div(text="""
<body>
<font color="white" size="4" face="Bookman Old Style, Book Antiqua, Garamond">
</br>
</br>
<h2> Carte représentant les restaurants français de New York et leurs notes associées.</h2>
<p> Cette carte nous montre tout les restaurants de cuisine française ainsi que les notes qui leurs ont été attribuées.</p>
</font></body>""")

layout=column(entete,p,texte)

show(layout)