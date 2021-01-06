#!/usr/bin/env python
# coding: utf-8

# ### import libraries

# In[1]:


import requests
import pandas as pd
import numpy as np 
import random
 get_ipython().system('conda install -c conda-forge geopy --yes')


# In[2]:


get_ipython().system('conda install -c conda-forge folium=0.5.0 --yes')


# In[3]:


get_ipython().system('pip install beautifulsoup4')


# In[4]:


get_ipython().system('pip install lxml')


# In[9]:


from geopy.geocoders import Nominatim
import folium
from bs4 import BeautifulSoup
import matplotlib.cm as cm
import matplotlib.colors as colors
from pandas.io.json import json_normalize
from sklearn.cluster import KMeans
from IPython.display import Image 
from IPython.core.display import HTML
from IPython.display import display_html


# ### code to scrap wikipedia page -Output will be in form of HTML table

# src=requests.get('https://en.wikipedia.org/wiki/List_of_postal_codes_of_Canada:_M').text
# soup=BeautifulSoup(src,'lxml')
# print(soup.title)
# tabular=str(soup.table)
# display_html(tabular,raw=True)

# ### Convert above HTML table into pandas dataframe

# In[14]:


df=pd.read_html(tabular)
df=df[0]
df.head()


# In[15]:


#dropping the rows where boroughs are not assigned
df.drop(df.loc[df['Borough']=='Not assigned'].index ,inplace=True)


# In[16]:


df.head()


# In[19]:


# combining  the neighbourhood with same postal code
df=df.groupby(['Postal Code','Borough'],sort=False).agg(', '.join)
df.reset_index(inplace=True)
df.head()


# In[20]:


#replacing the names of neighbourhoods which are not assigned
df['Neighbourhood'] = np.where(df['Neighbourhood'] == 'Not assigned',df['Borough'], df['Neighbourhood'])
df.head()


# In[22]:


df.shape


# ### importing CSV file for latitudes and longitudes

# In[23]:


latlon=pd.read_csv('https://cocl.us/Geospatial_data')
latlon.head()


# In[24]:


# merging two tables
df=pd.merge(df,latlon,on='Postal Code')
df.head()


# ### Clustering and plotting neighborhood of canada with borough=toronto

# In[25]:


# getting rows which contain toronto in borough
df=df[df['Borough'].str.contains('Toronto')]
df.head()


# In[27]:


# visualization of all neighborhood using folium
map_toronto = folium.Map(location=[43.651070,-79.347015],zoom_start=10)

for lat,lng,borough,neighbourhood in zip(df['Latitude'],df['Longitude'],df['Borough'],df['Neighbourhood']):
    label = '{}, {}'.format(neighbourhood, borough)
    label = folium.Popup(label, parse_html=True)
    folium.CircleMarker(
    [lat,lng],
    radius=5,
    popup=label,
    color='blue',
    fill=True,
    fill_color='#3186cc',
    fill_opacity=0.7,
    parse_html=False).add_to(map_toronto)
map_toronto


# ### KMeans for clustering

# In[34]:


k=5
tclustering = df.drop(['Postal Code','Borough','Neighbourhood'],1)
kmeans = KMeans(n_clusters = k,random_state=0).fit(tclustering)
kmeans.labels_
df.insert(0, 'Cluster Labels', kmeans.labels_)


# In[33]:


df.head()


# In[35]:


# create map
map_clusters = folium.Map(location=[43.651070,-79.347015],zoom_start=10)

# set color scheme for the clusters
x = np.arange(k)
ys = [i + x + (i*x)**2 for i in range(k)]
colors_array = cm.rainbow(np.linspace(0, 1, len(ys)))
rainbow = [colors.rgb2hex(i) for i in colors_array]

# add markers to the map
markers_colors = []
for lat, lon, neighbourhood, cluster in zip(df['Latitude'], df['Longitude'], df['Neighbourhood'], df['Cluster Labels']):
    label = folium.Popup(' Cluster ' + str(cluster), parse_html=True)
    folium.CircleMarker(
        [lat, lon],
        radius=5,
        popup=label,
        color=rainbow[cluster-1],
        fill=True,
        fill_color=rainbow[cluster-1],
        fill_opacity=0.7).add_to(map_clusters)
       
map_clusters


# In[ ]:




