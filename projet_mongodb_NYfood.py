#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Apr 29 11:48:00 2022

@author: theocavenne
"""


from pymongo import MongoClient
from bokeh.plotting import figure, show, output_file
from bokeh.models import HoverTool,ColumnDataSource, Div, Column, Row, Legend
from bokeh.tile_providers import get_provider, Vendors
from bokeh.models.widgets import Tabs, Panel
from bokeh.layouts import column, row
from bokeh.transform import factor_cmap
import numpy as np
import pandas as pd
import datetime
from bokeh.io import curdoc

dbURI="mongodb+srv://etudiant:ur2@clusterm1.0rm7t.mongodb.net/"
client = MongoClient(dbURI)
db=client['food']
coll=db['NYfood']

#df_NYfood.dtypes

list_NYfood=list(coll.aggregate([
    {"$unwind":"$grades"},
    {"$match":{"cuisine":"French"}},
    {"$group":{"_id":{"Name":"$name","Borough":"$borough","Adress":"$adress.street","coord":"$address.loc.coordinates","Note":"$grades.grade"},"Nb_notes":{"$sum":1}}}
]))

df_NYfood=pd.DataFrame(columns=['Name','Borough','Latitude','Longitude','Note','Nb_notes'])

for i in range(len(list_NYfood)):
    df_NYfood=df_NYfood.append({'Name':list_NYfood[i]['_id']['Name'],
                                'Borough':list_NYfood[i]['_id']['Borough'],
                                'Latitude':list_NYfood[i]['_id']['coord'][1],
                                'Longitude':list_NYfood[i]['_id']['coord'][0],
                                'Note':list_NYfood[i]['_id']['Note'],
                                'Nb_notes':list_NYfood[i]['Nb_notes']}, 
                               ignore_index=True)


k = 6378137
df_NYfood["x"] = df_NYfood['Longitude'] * (k * np.pi / 180.0)
df_NYfood["y"] = np.log(np.tan((90 + df_NYfood['Latitude']) * np.pi / 360.0)) * k

source = ColumnDataSource(df_NYfood)

p = figure(x_axis_type="mercator", y_axis_type="mercator", active_scroll="wheel_zoom", title="Restaurants")
tile_provider = get_provider(Vendors.CARTODBPOSITRON)
p.add_tile(tile_provider)
p.triangle(x="x",y="y",source=source,size =5)

TOOLTIPS = [
    ('Name', '@Name'),
    ('Borough', '@Borough'),
    ('Note', '@Note'),
    ('Nombre de notes', '@Nb_notes')]
hover_tool = HoverTool(tooltips=TOOLTIPS)
p.add_tools(hover_tool)
show(p)




