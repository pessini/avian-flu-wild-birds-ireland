---
layout: default
title: Gathering Data
description: Web Scraping to aggregate data from BirdWatch Ireland and spatial data from Ordinance Survey Ireland.
---

[<< BACK](./)

```python
import geopandas as gpd
import json
from pathlib import Path
from shapely.geometry import Point
from shapely.geometry import Polygon

import pandas as pd
import numpy as np
from bs4 import BeautifulSoup
import requests
import urllib
from urllib import parse
from skimage import io
```

## BirdWatch Ireland - Species & Habitat Conservation

<img title="BirdWatch Ireland" src="https://raw.githubusercontent.com/pessini/avian-flu-wild-birds-ireland/main/img/BWI_logo_03_80px%402x.webp?raw=true" alt="BirdWatch Ireland" style='height:150px; padding: 15px' align = "right">**BirdWatch Ireland** is the largest independent conservation organisation in Ireland and their objective is the protection of wild birds and their habitats. They have been doing an incredible work protecting birds and biodiversity in Ireland. Check out their amazing work [here](https://birdwatchireland.ie/our-work/).

The data is collected using **Web Scraping** technique from BirdWatch Ireland's website. There is a [list of Ireland's birds](https://birdwatchireland.ie/irelands-birds-birdwatch-ireland/list-of-irelands-birds/) with detailed information on every species.

To create our dataset and merge with the data provided by the Department of Agriculture, Food and the Marine, the focus will be on the bird's image and common name.

**Note**: `scikit-image imread`: OpenCV represents images in BGR order, whereas scikit-image represents images in RGB order. To utilize OpenCV functions after downloading the image, there is a extra step which is to convert the image from RGB to BGR.


```python
# div class birds-with-filters (Parent)
# page/2/
no_pages = 24

def get_data(pageNo):  
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:66.0) 
    Gecko/20100101 Firefox/66.0", 
    "Accept-Encoding":"gzip, deflate", 
    "Accept":"text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8", "DNT":"1","Connection":"close", "Upgrade-Insecure-Requests":"1"}

    r = requests.get('https://birdwatchireland.ie/irelands-birds-birdwatch-ireland/list-of-irelands-birds/'+str(pageNo), headers=headers)#, proxies=proxies)
    content = r.content
    soup = BeautifulSoup(content)
    #print(soup)

    alls = []
    for d in soup.findAll('article', attrs={'class':'bird'}):
        
        # image
        image_div = d.find('div', attrs={'class':'bird-img'})
        img_html = image_div.find('img')

        # text
        bird_name = d.find('h3', attrs={'class':'title'})

        complementary_info = d.find('div', attrs={'class':'bird-info'})
        bird_info = complementary_info.find_all('p')
        irish_name = bird_info[0]
        scientific_name = bird_info[1]
        bird_family = bird_info[2]

        all1=[]

        if img_html is not None:
            str_image = img_html['data-src']

            # there is a URL on Page 20 with an accent 
            # Snow Goose - https://birdwatchireland.ie/app/uploads/2019/02/Snowy-Owl-08-with-kill-René-Bruun.jpg
            # for that reason it needs to parse.quote() ignoring : and /, otherwise it will throw an error

            image = io.imread(urllib.parse.quote(str_image, safe=':/'))
            all1.append(image)
        else:
            all1.append('0')

        if bird_name is not None:
            all1.append(bird_name.text) if bird_name.text != '' else all1.append(np.nan)
        else:    
            all1.append('0')

        if irish_name is not None:
            all1.append(irish_name.text) if irish_name.text != '' else all1.append(np.nan)
        else:
            all1.append('0')

        if scientific_name is not None:
            all1.append(scientific_name.text) if scientific_name.text != '' else all1.append(np.nan)
        else:
            all1.append('0')

        if bird_family is not None:
            all1.append(bird_family.text) if bird_family.text != '' else all1.append(np.nan)
        else:
            all1.append('0')

        alls.append(all1)    

    return alls
```


```python
results = []
# for i in range(1, no_pages+1):
for i in range(1, no_pages+1):
    url_to_append = "page/{}/".format(i)
    results.append(get_data(url_to_append))
    print(url_to_append+': OK')

flatten = lambda l: [item for sublist in l for item in sublist]
data_webscraping = flatten(results)
```


```python
df_birds = pd.DataFrame(data_webscraping, columns=['Image','Bird_Name','Irish_Name','Scientific_Name','Bird_Family'])
df_birds.to_pickle('./data/BirdWatchIreland.pkl')
#df_birds.to_csv('./data/BirdWatchIreland.csv', index=False)
```

---
## H5N1 Wild Bird Species Identification

<img title="Department of Agriculture, Food and the Marine" src="https://raw.githubusercontent.com/pessini/avian-flu-wild-birds-ireland/main/img/department-of-agriculture-food-and-the-marine.png?raw=true" alt="Department of Agriculture, Food and the Marine" align="center" style='height:150px; padding: 15px'>


Dataset provided by Ireland's [Department of Agriculture, Food and the Marine](https://data.gov.ie/dataset/h5n1-wild-bird-species-identification) which contains the locations of bird species captured in Ireland from 1980-09-01 to 2020-01-27 and wild birds that are targeted for the H5N1 strain of avian flu.


```python
wild_birds = pd.read_csv("./data/98696_58589762-e8f9-4bb0-9d39-09570efbad62.xls", encoding='latin-1')
birdwatch = pd.read_pickle('./data/BirdWatchIreland.pkl')
wild_birds.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Scientific_Name</th>
      <th>Common_Name</th>
      <th>Date</th>
      <th>Year</th>
      <th>Month</th>
      <th>Day</th>
      <th>Time</th>
      <th>Country</th>
      <th>Country_State_County</th>
      <th>State</th>
      <th>County</th>
      <th>Locality</th>
      <th>Latitude</th>
      <th>Longitude</th>
      <th>Parent_Species</th>
      <th>target_H5_HPAI</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>Acrocephalus scirpaceus</td>
      <td>Eurasian Reed Warbler</td>
      <td>15/09/2015</td>
      <td>2015</td>
      <td>9</td>
      <td>15</td>
      <td>1100</td>
      <td>Ireland</td>
      <td>IE-C-GY</td>
      <td>Connaught</td>
      <td>Galway</td>
      <td>Inishmore (Inis Mór)</td>
      <td>53.1291</td>
      <td>-9.7507</td>
      <td>Acrocephalus scirpaceus</td>
      <td>0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>Acrocephalus scirpaceus</td>
      <td>Eurasian Reed Warbler</td>
      <td>15/09/2015</td>
      <td>2015</td>
      <td>9</td>
      <td>15</td>
      <td>1100</td>
      <td>Ireland</td>
      <td>IE-C-GY</td>
      <td>Connaught</td>
      <td>Galway</td>
      <td>Inishmore (Inis Mór)</td>
      <td>53.1291</td>
      <td>-9.7507</td>
      <td>Acrocephalus scirpaceus</td>
      <td>0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>Limosa haemastica</td>
      <td>Hudsonian Godwit</td>
      <td>15/09/2015</td>
      <td>2015</td>
      <td>9</td>
      <td>15</td>
      <td>1100</td>
      <td>Ireland</td>
      <td>IE-C-GY</td>
      <td>Connaught</td>
      <td>Galway</td>
      <td>Inishmore (Inis Mór)</td>
      <td>53.1291</td>
      <td>-9.7507</td>
      <td>Limosa haemastica</td>
      <td>0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>Limosa haemastica</td>
      <td>Hudsonian Godwit</td>
      <td>15/09/2015</td>
      <td>2015</td>
      <td>9</td>
      <td>15</td>
      <td>1100</td>
      <td>Ireland</td>
      <td>IE-C-GY</td>
      <td>Connaught</td>
      <td>Galway</td>
      <td>Inishmore (Inis Mór)</td>
      <td>53.1291</td>
      <td>-9.7507</td>
      <td>Limosa haemastica</td>
      <td>0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>Limosa haemastica</td>
      <td>Hudsonian Godwit</td>
      <td>15/09/2015</td>
      <td>2015</td>
      <td>9</td>
      <td>15</td>
      <td>1100</td>
      <td>Ireland</td>
      <td>IE-C-GY</td>
      <td>Connaught</td>
      <td>Galway</td>
      <td>Inishmore (Inis Mór)</td>
      <td>53.1291</td>
      <td>-9.7507</td>
      <td>Limosa haemastica</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>



**JOIN** the two bird datasets to link image to the specie. Using Scientific Name as key column


```python
birdwatch.head()
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Image</th>
      <th>Bird_Name</th>
      <th>Irish_Name</th>
      <th>Scientific_Name</th>
      <th>Bird_Family</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>[[[193, 145, 9], [189, 141, 5], [185, 137, 1],...</td>
      <td>Arctic Tern</td>
      <td>Geabhróg artach</td>
      <td>Sterna paradisaea</td>
      <td>Terns</td>
    </tr>
    <tr>
      <th>1</th>
      <td>[[[33, 72, 87], [35, 74, 89], [37, 76, 93], [4...</td>
      <td>Balearic Shearwater</td>
      <td>Cánóg Bhailéarach</td>
      <td>Puffinus mauretanicus</td>
      <td>Tubenoses</td>
    </tr>
    <tr>
      <th>2</th>
      <td>[[[52, 64, 88], [55, 67, 91], [57, 69, 93], [5...</td>
      <td>Bar-tailed Godwit</td>
      <td>Guilbneach stríocearrach</td>
      <td>Limosa lapponica</td>
      <td>Waders</td>
    </tr>
    <tr>
      <th>3</th>
      <td>[[[89, 78, 46], [88, 77, 45], [85, 74, 42], [8...</td>
      <td>Barn Owl</td>
      <td>Scréachóg reilige</td>
      <td>Tyto alba</td>
      <td>Owls</td>
    </tr>
    <tr>
      <th>4</th>
      <td>[[[130, 112, 74], [129, 111, 73], [127, 109, 7...</td>
      <td>Barnacle Goose</td>
      <td>Gé ghiúrainn</td>
      <td>Branta leucopsis</td>
      <td>Geese</td>
    </tr>
  </tbody>
</table>
</div>



```python
bird_flu = wild_birds.join(birdwatch.set_index('Scientific_Name'), on='Scientific_Name', lsuffix='_original', rsuffix='_bwi')
```


```python
# Selecting only infected birds
infected_birds = bird_flu[bird_flu['target_H5_HPAI'] == 1]
top_infected_species = infected_birds.groupby('Scientific_Name').size().sort_values(ascending=False)
top_infected_species
```




    Scientific_Name
    Chroicocephalus ridibundus    332
    Cygnus olor                   273
    Ardea cinerea                 259
    Egretta garzetta              227
    Larus marinus                 152
    Anas platyrhynchos            144
    Buteo buteo                   121
    Aythya fuligula               119
    Pica pica                     118
    Cygnus cygnus                 105
    Falco peregrinus               92
    Tadorna tadorna                83
    Tachybaptus ruficollis         78
    Larus canus                    76
    Branta bernicla                63
    Somateria mollissima           44
    Anser anser                    43
    Anas acuta                     40
    Aythya marila                  37
    Anser brachyrhynchus           33
    Podiceps cristatus             29
    Anas crecca                    25
    Turdus pilaris                 21
    Branta canadensis              18
    Aythya ferina                  18
    Bucephala clangula             16
    Mergus merganser               15
    Haliaeetus albicilla            4
    dtype: int64




```python
infected_birds_new = top_infected_species.to_frame().join(birdwatch.set_index('Scientific_Name'), on='Scientific_Name', lsuffix='_original', rsuffix='_bwi')
```


```python
infected_birds_new[infected_birds_new.isna().any(axis=1)]
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>0</th>
      <th>Image</th>
      <th>Bird_Name</th>
      <th>Irish_Name</th>
      <th>Bird_Family</th>
    </tr>
    <tr>
      <th>Scientific_Name</th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
      <th></th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>Chroicocephalus ridibundus</th>
      <td>332</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>Branta bernicla</th>
      <td>63</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
    <tr>
      <th>Aythya marila</th>
      <td>37</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
      <td>NaN</td>
    </tr>
  </tbody>
</table>
</div>



---

There are **3 species** among those classified as Infected Birds which do not have image. Something might be different on those two datasets. Let's investigate.

- Chroicocephalus ridibundus
- Branta bernicla
- Aythya marila

`Chroicocephalus ridibundus`: have the same Common Name Black-headed Gull on both dataset but on BirdWatch Ireland's dataset the Scientific Name is Larus ridibundus. I will switch the Scientific name so that the Join can work.

---

`Branta bernicla`: There are three subspecies of Brant (or Brent) Goose.
- **Branta bernicla nigricans** — Black-bellied Brant of extreme north-east Siberia to north central Canada.
- **Branta bernicla bernicla** — Dark-bellied Brant of northern and central Siberia.
- **Branta bernicla hrota** — Pale-bellied Brant of Canada, Greenland, Svalbard and Franz Josef Land.

A fourth Brent Goose population has been recorded in Ireland, though its taxonomic status remains uncertain and it has no scientific name. It is generally known colloquially as **‘Grey-bellied Brant’**.

**Department of Agriculture, Food and the Marine dataset**
- Branta bernicla                   63
- Branta bernicla hrota             45
- Branta bernicla bernicla           4
- Branta bernicla (Gray-bellied)     1


Black-bellied Brant (*nigricans*) is very similar to Light-bellied Brent Goose (*hrota*) and care is needed to distinguish the two species. Brent Goose (Dark-bellied) and Black Brant are a rare winter visitor. As Brent Goose (Light-bellied) is the most common species in Ireland and it is easily mistaken by Black-bellied Brant (*nigricans*), I will combine Pale-bellied Brant and Black-bellied Brant.


Sources: 

[https://www.waterfowl.org.uk/wildfowl/swans-geese-allies/brent-goose/](https://www.waterfowl.org.uk/wildfowl/swans-geese-allies/brent-goose/)

[https://www.birdguides.com/articles/identification/brent-geese-photo-id-guide/](https://www.birdguides.com/articles/identification/brent-geese-photo-id-guide/)

---

`Aythya marila`: Greater Scaup from the Duck family is under the Scientific Name Anas marila on BirdWatch Ireland's dataset.


```python
wild_birds_copy = wild_birds.copy()
birdwatch_copy = birdwatch.copy()
```


```python
# Fixing 1st issue 'Chroicocephalus ridibundus'
birdwatch_copy['Scientific_Name'] = birdwatch_copy['Scientific_Name'].replace('Larus ridibundus','Chroicocephalus ridibundus')
```


```python
# Different Brent Geese species
wild_birds_copy[wild_birds_copy['Scientific_Name'].str.startswith('Branta bernicla')].drop_duplicates(subset='Common_Name').drop(['Year', 'Month','Day','Time','Country','Country_State_County','State','Latitude','Longitude'], axis='columns')
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Scientific_Name</th>
      <th>Common_Name</th>
      <th>Date</th>
      <th>County</th>
      <th>Locality</th>
      <th>Parent_Species</th>
      <th>target_H5_HPAI</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>179</th>
      <td>Branta bernicla</td>
      <td>Brant</td>
      <td>30/04/2016</td>
      <td>Donegal</td>
      <td>Donegal</td>
      <td>Branta bernicla</td>
      <td>1</td>
    </tr>
    <tr>
      <th>1055</th>
      <td>Branta bernicla hrota</td>
      <td>Brant (Atlantic)</td>
      <td>13/12/2016</td>
      <td>Wexford</td>
      <td>Wexford Wildfowl Reserve</td>
      <td>Branta bernicla</td>
      <td>0</td>
    </tr>
    <tr>
      <th>6235</th>
      <td>Branta bernicla bernicla</td>
      <td>Brant (Dark-bellied)</td>
      <td>03/01/2019</td>
      <td>Galway</td>
      <td>Barna Pier, County Galway, IE (53.249, -9.15)</td>
      <td>Branta bernicla</td>
      <td>0</td>
    </tr>
    <tr>
      <th>6839</th>
      <td>Branta bernicla (Gray-bellied)</td>
      <td>Brant (Gray-bellied)</td>
      <td>18/03/2019</td>
      <td>Louth</td>
      <td>Dundalk Bay--Lurgangreen (hide and saltmarsh)</td>
      <td>Branta bernicla</td>
      <td>0</td>
    </tr>
  </tbody>
</table>
</div>




```python
birdwatch_copy[birdwatch_copy['Irish_Name'] == 'Cadhan']
```




<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Image</th>
      <th>Bird_Name</th>
      <th>Irish_Name</th>
      <th>Scientific_Name</th>
      <th>Bird_Family</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>7</th>
      <td>[[[36, 18, 4], [33, 15, 1], [42, 24, 10], [49,...</td>
      <td>Black Brant</td>
      <td>Cadhan</td>
      <td>Branta bernicla nigricans</td>
      <td>Geese</td>
    </tr>
    <tr>
      <th>18</th>
      <td>[[[157, 171, 184], [157, 171, 184], [156, 170,...</td>
      <td>Brent Goose (Dark-bellied)</td>
      <td>Cadhan</td>
      <td>Branta bernicla bernicla</td>
      <td>Geese</td>
    </tr>
    <tr>
      <th>19</th>
      <td>[[[153, 176, 190], [153, 176, 190], [153, 176,...</td>
      <td>Brent Goose (Light-bellied)</td>
      <td>Cadhan</td>
      <td>Branta bernicla hrota</td>
      <td>Geese</td>
    </tr>
  </tbody>
</table>
</div>

```python
#infected_birds = bird_flu[bird_flu['target_H5_HPAI'] == 1]
top_infected_species = wild_birds_copy.groupby('Scientific_Name').size().sort_values(ascending=False)
top_infected_species[top_infected_species.index.str.startswith('Branta bernicla')]
```

    Scientific_Name
    Branta bernicla                   63
    Branta bernicla hrota             45
    Branta bernicla bernicla           4
    Branta bernicla (Gray-bellied)     1
    dtype: int64




```python
# Fixing 2nd issue 'Branta bernicla'
wild_birds_copy['Scientific_Name'] = wild_birds_copy['Scientific_Name'].replace(['Branta bernicla'],'Branta bernicla hrota')
```


```python
birdwatch_copy[birdwatch_copy['Bird_Family'] == 'Ducks']
```


<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>Image</th>
      <th>Bird_Name</th>
      <th>Irish_Name</th>
      <th>Scientific_Name</th>
      <th>Bird_Family</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>32</th>
      <td>[[[179, 185, 185], [179, 185, 185], [178, 184,...</td>
      <td>Common Scoter</td>
      <td>Scótar</td>
      <td>Melanitta nigra</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>46</th>
      <td>[[[32, 36, 45], [33, 37, 46], [34, 38, 47], [3...</td>
      <td>Eider</td>
      <td>Éadar</td>
      <td>Somateria mollissima</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>51</th>
      <td>[[[96, 131, 163], [96, 131, 163], [96, 131, 16...</td>
      <td>Gadwall</td>
      <td>Gadual</td>
      <td>Anas strepera</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>54</th>
      <td>[[[119, 149, 77], [120, 150, 78], [122, 149, 7...</td>
      <td>Garganey</td>
      <td>Praslacha shamhraidh</td>
      <td>Anas querquedula</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>59</th>
      <td>[[[159, 169, 171], [158, 168, 170], [158, 168,...</td>
      <td>Goldeneye</td>
      <td>Órshúileach</td>
      <td>Bucephala clangula</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>61</th>
      <td>[[[66, 67, 51], [69, 70, 54], [72, 73, 57], [7...</td>
      <td>Goosander</td>
      <td>Síolta mhór</td>
      <td>Mergus merganser</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>71</th>
      <td>[[[180, 196, 212], [180, 196, 212], [180, 196,...</td>
      <td>Green-winged Teal</td>
      <td>Praslacha ghlaseiteach</td>
      <td>Anas carolinensis</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>108</th>
      <td>[[[26, 24, 12], [26, 24, 12], [26, 24, 12], [2...</td>
      <td>Long-tailed Duck</td>
      <td>Lacha earrfhada</td>
      <td>Clangula hyemalis</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>111</th>
      <td>[[[119, 154, 192], [120, 155, 193], [122, 157,...</td>
      <td>Mallard</td>
      <td>Mallard</td>
      <td>Anas platyrhynchos</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>128</th>
      <td>[[[102, 91, 59], [96, 85, 53], [91, 81, 46], [...</td>
      <td>Pintail</td>
      <td>Biorearrach</td>
      <td>Anas acuta</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>129</th>
      <td>[[[193, 196, 203], [193, 196, 203], [193, 196,...</td>
      <td>Pochard</td>
      <td>Póiseard cíordhearg</td>
      <td>Aythya ferina</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>137</th>
      <td>[[[21, 19, 20], [21, 19, 20], [21, 19, 20], [2...</td>
      <td>Red-breasted Merganser</td>
      <td>Síolta rua</td>
      <td>Mergus serrator</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>149</th>
      <td>[[[89, 88, 86], [89, 88, 86], [90, 89, 87], [9...</td>
      <td>Ring-necked Duck</td>
      <td>Lacha mhuinceach</td>
      <td>Aythya collaris</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>156</th>
      <td>[[[65, 72, 38], [65, 72, 38], [65, 72, 38], [6...</td>
      <td>Ruddy Duck</td>
      <td>Lacha rua</td>
      <td>Oxyura jamaicensis</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>162</th>
      <td>[[[171, 161, 102], [167, 157, 98], [164, 152, ...</td>
      <td>Scaup</td>
      <td>Lacha iascán</td>
      <td>Anas marila</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>165</th>
      <td>[[[62, 85, 116], [61, 84, 115], [61, 84, 115],...</td>
      <td>Shelduck</td>
      <td>Seil-lacha</td>
      <td>Tadorna tadorna</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>167</th>
      <td>[[[105, 117, 129], [105, 117, 129], [105, 117,...</td>
      <td>Shoveler</td>
      <td>Spadalach</td>
      <td>Anas clypeata</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>171</th>
      <td>[[[88, 109, 136], [87, 108, 135], [87, 108, 13...</td>
      <td>Smew</td>
      <td>Síolta gheal</td>
      <td>Mergellus albellus</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>185</th>
      <td>[[[81, 107, 142], [86, 112, 147], [91, 117, 15...</td>
      <td>Surf Scoter</td>
      <td>Scótar toinne</td>
      <td>Mellanitta perspicillata</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>188</th>
      <td>[[[204, 208, 217], [204, 208, 217], [204, 208,...</td>
      <td>Teal</td>
      <td>Praslacha</td>
      <td>Anas crecca</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>191</th>
      <td>[[[159, 159, 157], [159, 159, 157], [159, 159,...</td>
      <td>Tufted Duck</td>
      <td>Lacha bhadánach</td>
      <td>Aythya fuligula</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>195</th>
      <td>[[[131, 124, 105], [139, 132, 114], [117, 110,...</td>
      <td>Velvet Scoter</td>
      <td>Sceadach</td>
      <td>Mellanitta fusca</td>
      <td>Ducks</td>
    </tr>
    <tr>
      <th>204</th>
      <td>[[[51, 48, 39], [46, 43, 34], [42, 39, 30], [4...</td>
      <td>Wigeon</td>
      <td>Rualacha</td>
      <td>Anas penelope</td>
      <td>Ducks</td>
    </tr>
  </tbody>
</table>
</div>




```python
# Fixing 3rd issue 'Anas marila'
birdwatch_copy['Scientific_Name'] = birdwatch_copy['Scientific_Name'].replace('Anas marila','Aythya marila')
```


```python
final_df = wild_birds_copy.join(birdwatch_copy.set_index('Scientific_Name'), on='Scientific_Name', lsuffix='_original', rsuffix='_bwi')

final_df.to_pickle('./data/bird-flu.pkl')
```

---

## Ordnance Survey *Ireland* (OSi) - Ireland’s National Mapping Agency

<img title="Ordnance Survey Ireland (OSi)" src="https://raw.githubusercontent.com/pessini/avian-flu-wild-birds-ireland/main/img/Logo-Colour-298x100.jpeg?raw=true" alt="Ireland’s National Mapping Agency" align="right" style='height:120px; padding: 15px'>The spacial data is provided by [**Ordnance Survey *Ireland* (OSi)**](https://www.osi.ie/) under [Creative Commons licence](https://creativecommons.org/licenses/by/4.0/legalcode).

Ordnance Survey Ireland has evolved from the Ordnance Survey Office which was established in 1824, later becoming a state body under the Ordnance Survey Ireland Act 2001. Under this Act, Ordnance Survey Ireland continued its mainstream public service function of creating and maintaining the definitive mapping records of the State and also assumed the commercial function assigned to it under the Act of developing its commercial business and sales revenues.

**Administrative Areas** dataset generated from the [**2019 OSi National Statutory Boundary dataset**](https://data-osi.opendata.arcgis.com/datasets/OSi::administrative-areas-osi-national-statutory-boundaries-/about).

Dataset License: https://creativecommons.org/licenses/by/4.0/


```python
url_geoJSON = 'https://opendata.arcgis.com/datasets/0d5984f732c54246bd087768223c92eb_0.geojson'
admin_areas_json = 'data/Administrative_Areas_Ireland.json'
```


```python
# GeoJSON API
admin_areas = gpd.read_file(url_geoJSON, driver='GeoJSON')
```

### Adding Count of bird flu occurences on each Administrative Area


```python
avian_flu = wild_birds.copy()
avian_flu['geometry'] = None

for index, row in avian_flu.iterrows():
    avian_flu.loc[index, 'geometry'] = Point(row.Longitude, row.Latitude)
```

**Coordinate Reference System (CRS)**: Setting a projection with Spatial Reference [**EPSG Code**](https://epsg.io/29902)


```python
gdf_infected_birds = gpd.GeoDataFrame(avian_flu, geometry='geometry').set_crs(epsg=29902, inplace=True)
```

On the dataset with birds' information we have only Latitude and Longitude, so first I convert them in geometry Points to use later on a polygon operation. After that, a loop is created and for every point an intersect operation is done to check if the Point belongs to that Polygon (Administrative Area). 


```python
# adding Count of bird flu occurences on each Administrative Area
for index, area in admin_areas.iterrows():
    
    count_infected_birds = len(gdf_infected_birds[(gdf_infected_birds['target_H5_HPAI'] == 1) & (gdf_infected_birds.intersects(area.geometry)) ])
    count_healthy_birds = len(gdf_infected_birds[(gdf_infected_birds['target_H5_HPAI'] == 0) & (gdf_infected_birds.intersects(area.geometry)) ])
    total_birds = count_healthy_birds + count_infected_birds
    
    admin_areas.loc[index, 'TOTAL_BIRDS'] = total_birds
    admin_areas.loc[index, 'HEALTHY_BIRDS'] = count_healthy_birds
    admin_areas.loc[index, 'INFECTED_BIRDS'] = count_infected_birds
```

```python
admin_areas.head()
```
<div>
<style scoped>
    .dataframe tbody tr th:only-of-type {
        vertical-align: middle;
    }

    .dataframe tbody tr th {
        vertical-align: top;
    }

    .dataframe thead th {
        text-align: right;
    }
</style>
<table border="0" class="dataframe">
  <thead>
    <tr style="text-align: right;">
      <th></th>
      <th>ENGLISH</th>
      <th>GAEILGE</th>
      <th>CONTAE</th>
      <th>COUNTY</th>
      <th>PROVINCE</th>
      <th>GUID</th>
      <th>CENTROID_X</th>
      <th>CENTROID_Y</th>
      <th>AREA</th>
      <th>CC_ID</th>
      <th>OBJECTID</th>
      <th>Shape__Area</th>
      <th>Shape__Length</th>
      <th>geometry</th>
      <th>TOTAL_BIRDS</th>
      <th>HEALTHY_BIRDS</th>
      <th>INFECTED_BIRDS</th>
    </tr>
  </thead>
  <tbody>
    <tr>
      <th>0</th>
      <td>DUBLIN CITY COUNCIL</td>
      <td>None</td>
      <td>Baile Átha Cliath</td>
      <td>DUBLIN</td>
      <td>Leinster</td>
      <td>2ae19629-1433-13a3-e055-000000000001</td>
      <td>716469.75</td>
      <td>735272.06</td>
      <td>1.283502e+08</td>
      <td>265011</td>
      <td>1</td>
      <td>1.283502e+08</td>
      <td>101493.212412</td>
      <td>POLYGON ((-6.38258 53.33367, -6.38261 53.33370...</td>
      <td>2161.0</td>
      <td>1642.0</td>
      <td>519.0</td>
    </tr>
    <tr>
      <th>1</th>
      <td>CORK CITY COUNCIL</td>
      <td>None</td>
      <td>Corcaigh</td>
      <td>CORK</td>
      <td>Munster</td>
      <td>2ae19629-1434-13a3-e055-000000000001</td>
      <td>565833.13</td>
      <td>571933.83</td>
      <td>1.865976e+08</td>
      <td>45511</td>
      <td>2</td>
      <td>1.865976e+08</td>
      <td>80293.730785</td>
      <td>POLYGON ((-8.38436 51.90533, -8.38425 51.90529...</td>
      <td>223.0</td>
      <td>182.0</td>
      <td>41.0</td>
    </tr>
    <tr>
      <th>2</th>
      <td>GALWAY CITY COUNCIL</td>
      <td>None</td>
      <td>Gaillimh</td>
      <td>GALWAY</td>
      <td>Connacht</td>
      <td>2ae19629-1435-13a3-e055-000000000001</td>
      <td>530067.66</td>
      <td>726500.52</td>
      <td>5.069505e+07</td>
      <td>65011</td>
      <td>3</td>
      <td>5.069505e+07</td>
      <td>64020.725628</td>
      <td>MULTIPOLYGON (((-9.13605 53.26682, -9.13606 53...</td>
      <td>989.0</td>
      <td>730.0</td>
      <td>259.0</td>
    </tr>
    <tr>
      <th>3</th>
      <td>OFFALY COUNTY COUNCIL</td>
      <td>None</td>
      <td>Uíbh Fhailí</td>
      <td>OFFALY</td>
      <td>Leinster</td>
      <td>2ae19629-1496-13a3-e055-000000000001</td>
      <td>631261.72</td>
      <td>709672.35</td>
      <td>2.000025e+09</td>
      <td>185001</td>
      <td>4</td>
      <td>2.000025e+09</td>
      <td>389927.708615</td>
      <td>POLYGON ((-7.97902 53.33689, -7.97878 53.33684...</td>
      <td>76.0</td>
      <td>69.0</td>
      <td>7.0</td>
    </tr>
    <tr>
      <th>4</th>
      <td>WICKLOW COUNTY COUNCIL</td>
      <td>None</td>
      <td>Cill Mhantáin</td>
      <td>WICKLOW</td>
      <td>Leinster</td>
      <td>2ae19629-149e-13a3-e055-000000000001</td>
      <td>707784.79</td>
      <td>690738.10</td>
      <td>2.025161e+09</td>
      <td>255001</td>
      <td>5</td>
      <td>2.025161e+09</td>
      <td>320629.958733</td>
      <td>MULTIPOLYGON (((-6.14602 52.78372, -6.14607 52...</td>
      <td>1231.0</td>
      <td>1062.0</td>
      <td>169.0</td>
    </tr>
  </tbody>
</table>
</div>
<br>
```python
# Saving the data downloaded to a local json file
admin_areas.to_file(admin_areas_json, driver='GeoJSON')
```

[<< BACK](./)