# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 15:34:18 2024

@author: pstas
"""

#import base64
#import geopy.distance
#import numpy as np
import os
#import folium'
import streamlit as st
import pandas as pd
import pydeck as pdk
import numpy as np

import locale
# Set the locale to default 'C' locale
locale.setlocale(locale.LC_ALL, 'C')

#%%

__location__ = os.path.realpath(
    os.path.join(os.getcwd(), os.path.dirname(__file__)))


#%%

def data_import(file):
    data_file = pd.read_csv(os.path.join(__location__, file))
    return data_file

#%%

#Title and page set up
st.set_page_config(layout="wide")
st.sidebar.title("BC Manufacted Housing")
st.title("Dashboard")
st.info("Choose a municipality from the dropdown to get started")


#Import data
data = data_import('BC Mobile Home Database Sample.csv')

#Delete after index 9 - THIS WILL HAVE TO BE REMOVED
final_data = data.iloc[:9]

#City List
city_list = final_data["Municipality"].unique()
city_list = city_list.tolist()

#Drop down of municipalities
municipality = st.sidebar.selectbox("Municipalities",city_list)

#Map data is filtered by the municipoality selected
map_data = final_data.loc[final_data['Municipality']==municipality].reset_index(drop=True)


#Community Types in selected community
community_list = map_data["Community"].unique()

#Muti-select of community types generated from community_list
community = st.sidebar.multiselect("Community Type", community_list, default=community_list)
map_data = map_data.loc[map_data['Community'].isin(community)].reset_index(drop=True)


#Map starting points based on municipality selected
latitude=map_data["lat"][0]
longitude=map_data["lon"][0]
    

tooltip = {
    "html": "{Civic Address}",
    "style": {"background": "grey", "color": "white", "font-family": '"Helvetica Neue", Arial', "z-index": "10000"},
}

st.pydeck_chart(pdk.Deck(
    map_style=None,
    tooltip=tooltip,
    initial_view_state=pdk.ViewState(
        latitude=latitude,
        longitude=longitude,
        zoom=10,
        pitch=25,
    ),
    layers=[
        pdk.Layer(
            'ScatterplotLayer',
            data=map_data,
            get_position='[lon, lat]',
            get_color='[200, 30, 0, 160]',
            get_radius=200,
            pickable=True,
        ),
    ],
))

#Drop unwanted chart collumns
chart_data = map_data.drop(['PID', 'lat', 'lon', 'Municipality', 'Zone Code', 'Zone Description', 'Width', 'Depth','BCA Description', 'Source', 'Listing', '2024 Assessed Land Value', 'Contact', 'Transacted Year'], axis=1)

#Convert lot size to acres
chart_data['Lot Size'] = chart_data['Lot Size'].div(43560).round(2)

#Metrics
col1, col2, col3 = st.columns(3)
col1.metric("Total Communities", chart_data['Civic Address'].count(), delta=None, delta_color="normal", help=None, label_visibility="visible")
col2.metric("Median Lot Size (Acres)", chart_data['Lot Size'].median().round(1), delta=None, delta_color="normal", help=None, label_visibility="visible")

try:
    col3.metric("Avg. Assessed Value per Acre", '${:,.2f}'.format(chart_data['2024 Assessed Total Value'].sum() / chart_data['Lot Size'].sum()), delta=None, delta_color="normal", help=None, label_visibility="visible")
except:
    col3.metric("Avg. Assessed Value per Acre", "NA", delta=None, delta_color="normal", help=None, label_visibility="visible")


#Drop empty columns
chart_data.dropna(how='all', axis=1, inplace=True) 


#Data frame clean up
st.data_editor(
    chart_data,
    column_config={
        "satellite": st.column_config.LinkColumn(
            "Satellite", display_text="Open"
        ),
        "Streetview": st.column_config.LinkColumn(
            "Streetview", display_text="Open"
        ),
        "Website": st.column_config.LinkColumn(
            "Website", display_text="Open"
        ),
        "Listing": st.column_config.LinkColumn(
            "Listing", display_text="Open"
        ),
        "Transaction Details": st.column_config.LinkColumn(
            "Transaction Details", display_text="Open"
        ),
    },
    hide_index=True,
)

