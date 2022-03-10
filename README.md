## Digital Electronics and Microprocessors Final Project

>Ana Cruz nº 201705191
>
>Ana Rita Diogo nº 201707122
>
> Integrated Master in Physics Engineering 
>
> July 6, 2020 

### 1. Introduction

This work was carried out within the scope of the EDM ("Eletrónica Digital e Microprocessadores") course, which proposes using the ESP32 board to access REST. services via Internet connection, and consequently use them through the functionalities of the components present on the board, such as LEDs and buttons.\
The project presented below follows the previous conditions, accessing REST services that return statistical information related to the COVID-19 pandemic by country and the number of inhabitants of the country in question. By calculating the number of cases per million inhabitants per country LEDs light up according to the severity of the disease in the selected country. 

### 2. Project

The code to carry out the project was developed using the *software* Studio Visual Code, creating two main *python* files: boot.py where the code to connect to the wifi network was written and main.py where the codes to obtain the data of the respective APIs that control the LEDs according to this data.\
The code section shown below connects the card to the wifi network using the *network* module, where the ssid and password variables are strings that are respectively the network SSID and the password to access it:

```python

import network   #importar módulo network
def do_connect():
  wlan = network.WLAN(network.STA_IF)
  wlan.active(True)
  if not wlan.isconnected():
    print('connecting to network...')
    wlan.connect('ssid', 'password') #ssid é o ssid da rede e password a palavra chave de acesso à mesma
    while not wlan.isconnected():
      pass
  print('network config:', wlan.ifconfig())
do_connect()

```
Para que o acesso aos serviços REST seja mais fácil, foi utilizada uma biblioteca *urequests* que foi instalada executando o seguinte comando no REPL do Visual Studio Code:

```python
import upip
upip.install('micropython-urequests')
```

#### 2.1 APIs

To obtain the data necessary to calculate the ratio between cases and population, we use two APIs: one that returns data regarding the COVID-19 pandemic, such as the total number of cases, number of deaths and number of recovered from a certain country , and another that returns the population number of that same country.
The *url* of the REST service used to obtain the statistical data[1] is as follows: <https://covid-19.dataflowkit.com/v1/portugal>, as we intend to obtain data referring to Portugal . To access any other country just replace the name in the *url*, and to access the world data we replace it with the word 'world'. The answer, in this case for Portugal, given by the service is presented as follows: 

```python
{
  "New Deaths_text": "+7",
  "Total Recovered_text": "28,
 772",
  "Total Cases_text": "43,
 659",
  "Total Deaths_text": "1,
 605",
  "New Cases_text": "+503",
  "Active Cases_text": "13,
 282",
  "Last Update": "2020-07-04 21:24",
  "Country_text": "Portugal"
}
```

To get the population value, the *url* of the REST[2] service is as follows: <https://data.opendatasoft.com/api/records/1.0/search/?dataset=world-population%40kapsarc&rows= 1&refine.year=2018&refine.country_name=Portugal>, and we defined the link in order to obtain the data for the year 2018 (the most recent that the *website* allows) and for Portugal, the answer is presented as follows: 

```python
{
  "records": [
    {
      "fields": {
        "country_name": "Portugal",
        "value": 1.028176e+07,
        "year": "2018"
      },
      "recordid": "c9d8fb02c3a0fb513a5e7d5738a470581a7f3bd1",
      "datasetid": "world-population@kapsarc",
      "record_timestamp": "1970-01-01T00:00:00+00:00"
    }
  ],
  "nhits": 1,
  "facet_groups": [
    {
      "name": "country_name",
      "facets": [
        {
          "path": "Portugal",
          "name": "Portugal",
          "count": 1,
          "state": "refined"
        }
      ]
    },
    {
      "name": "year",
      "facets": [
        {
          "path": "2018",
          "name": "2018",
          "count": 1,
          "state": "refined"
        }
      ]
    }
  ],
  "parameters": {
    "timezone": "UTC",
    "refine": {
      "year": "2018",
      "country_name": "Portugal"
    },
    "format": "json",
    "rows": 1,
    "dataset": [
      "world-population@kapsarc"
    ]
  }
}
```

From the APIs we can then calculate the ratio of total cases, which in the first API correspond to the value of "Total Cases_text", per million inhabitants dividing by the value of "value" within "fields". 

#### 2.2 LEDs

The connection of components on the board is done as follows: 
 
![alt text](https://github.com/anaritadiogo/projetofinal/blob/master/esquema.png "Esquema do circuito eletrónico") \
Figure 1 - Electronic circuit diagram.

![alt text](https://github.com/anaritadiogo/projetofinal/blob/master/placa.png "Placa com as ligações") \
Figure 2 - Connections made on the board .

The code written to control the LEDs and print the text with the data from the APIs is as follows: 

```python
from time import sleep
import urequests
from ujson import dumps
from machine import Pin

green_led = Pin(19, Pin.OUT) #led verde
yellow_led = Pin(22,Pin.OUT) #led amarelo
red_led = Pin(21,Pin.OUT)   #led vermelho

def prettify(s):
  i = 0
  for c in s:
    if c in ['[', '{']:
      print(c)
      i += 2
      print(i*' ', end='')
    elif c in [']', '}']:
      print("")
      i -= 2
      print(i*' ', end='')
      print(c, end='')
    elif c == ',':
      print(c)
      print((i-1)*' ', end='')
    else:
      print(c, end='')
  print("")

while True:
  url1 = "https://data.opendatasoft.com/api/records/1.0/search/?dataset=world-population%40kapsarc&rows=1&refine.country_name=Angola&refine.year=2018"
  url2 = "https://covid-19.dataflowkit.com/v1/angola"
  r1 = urequests.get(url1).json()
  r2 = urequests.get(url2).json()
  prettify(dumps(r1))
  prettify(dumps(r2))

  casos_ativos1 = r2["Total Cases_text"]  #casos ativos de covid-19
  casos_ativos1 = casos_ativos1.replace(',','')
  casos_ativos = float(casos_ativos1)

  pop = r1["records"][0]["fields"]["value"]    #Número de habitantes por país

  n = (casos_ativos/pop)*10**6 # casos por milhão de habitantes

 
  print("There are {0} new cases in {1} of COVID-19 as of today.\
  There are also {2} new deaths and {3} cases in total since the beginning\
  of the pandemic. The total confirmed cases per million people in {1} is {4}."\
  .format(r2["New Cases_text"],r2["Country_text"],r2["New Deaths_text"], r2["Total Cases_text"],n))


  # Casos por milhão de habitantes 
  if n <= 300: # menor ou igual a 300 por milhão de habitantes
    red_led.value(False)
    yellow_led.value(False)
    green_led.value(True)  #liga o led verde
    
  elif n >300 and n < 1000: # entre 100 e 1000 por milhão de habitantes
    red_led.value(False) 
    yellow_led.value(True)  #liga o led amarelo
    green_led.value(False)

  else: # superior a 1000 por milhão de habitantes
    red_led.value(True)    #liga o led vermelho
    yellow_led.value(False) 
    green_led.value(False)
  break

```
The program shown above allows, through the number of active cases of Covid-19 in each country, to light up the LEDs according to the state of the respective evolution of the pandemic in the country in question. In order to verify the status of each country, a variable *n* was defined, where *n*=((number of cases)/(number of inhabitants per country))10^6, which in this way allows to ascertain the number of of active cases in the population per million inhabitants.
The choice was made so that the green LED lights up if the value of n is less than 300 , the yellow LED if 300<n<1000 and finally the red LED if the value of n is greater than 1000, the chosen criteria for the LED color were made based on the values obtained from the following *website*: <https://en.wikipedia.org/wiki/COVID-19_pandemic>. 
    
![alt text](https://github.com/anaritadiogo/projetofinal/blob/master/mapa.png "Mapa do impacto da pandemia COVID-19.") \
Figure 3 - Total COVID-19 cases per million inhabitants.[3]

#### 2.3 Results
  For the analysis of our project, 3 different countries were chosen to investigate the state of evolution of the pandemic in each of them, for this the following countries were analyzed: China, Poland and Portugal. 
 
<ins>Analysis for the case of China </ins>

```python
{
  "records": [
    {
      "fields": {
        "country_name": "China",
        "value": 1.39273e+09,
        "year": "2018"
      },
      "recordid": "7dd23faa032eb7d54ace71050f68a88311455d51",
      "datasetid": "world-population@kapsarc",
      "record_timestamp": "1970-01-01T00:00:00+00:00"
    }
  ],
  "nhits": 1,
  "facet_groups": [
    {
      "name": "country_name",
      "facets": [
        {
          "path": "China",
          "name": "China",
          "count": 1,
          "state": "refined"
        }
      ]
    },
    {
      "name": "year",
      "facets": [
        {
          "path": "2018",
          "name": "2018",
          "count": 1,
          "state": "refined"
        }
      ]
    }
  ],
  "parameters": {
    "timezone": "UTC",
    "refine": {
      "year": "2018",
      "country_name": "China"
    },
    "format": "json",
    "rows": 1,
    "dataset": [
      "world-population@kapsarc"
    ]
  }
}
{
  "New Deaths_text": "",
  "Total Recovered_text": "78,
 528",
  "Total Cases_text": "83,
 565",
  "Total Deaths_text": "4,
 634",
  "New Cases_text": "+8",
  "Active Cases_text": "403",
  "Last Update": "2020-07-07 14:30",
  "Country_text": "China"
}
There are +8 new cases in China of COVID-19 as of today.  There are also  new deaths and 83,565 cases in total since the beginning  of the pandemic. The total confirmed cases per million people in China is 60.00087.
MicroPython v1.12 on 2019-12-20; ESP32 module with ESP32
Type "help()" for more information.
```

After running the program, it was verified that the green LED turned on, since the value obtained for n (approximately 60) is in the stipulated range for the green LED, that is, n<100.\

<ins>Analysis for the case of Poland </ins>

```python
  
  {
  "records": [
    {
      "fields": {
        "country_name": "Poland",
        "value": 3.797855e+07,
        "year": "2018"
      },
      "recordid": "1264aabdf2a47889f684cbf34dfc4184fd8e7c18",
      "datasetid": "world-population@kapsarc",
      "record_timestamp": "1970-01-01T00:00:00+00:00"
    }
  ],
  "nhits": 1,
  "facet_groups": [
    {
      "name": "country_name",
      "facets": [
        {
          "path": "Poland",
          "name": "Poland",
          "count": 1,
          "state": "refined"
        }
      ]
    },
    {
      "name": "year",
      "facets": [
        {
          "path": "2018",
          "name": "2018",
          "count": 1,
          "state": "refined"
        }
      ]
    }
  ],
  "parameters": {
    "timezone": "UTC",
    "refine": {
      "year": "2018",
      "country_name": "Poland"
    },
    "format": "json",
    "rows": 1,
    "dataset": [
      "world-population@kapsarc"
    ]
  }
}
{
  "New Deaths_text": "+7",
  "Total Recovered_text": "24,
 238",
  "Total Cases_text": "36,
 412",
  "Total Deaths_text": "1,
 528",
  "New Cases_text": "+257",
  "Active Cases_text": "10,
 646",
  "Last Update": "2020-07-07 09:30",
  "Country_text": "Poland"
}
There are +257 new cases in Poland of COVID-19 as of today.  There are also +7 new deaths and 36,412 cases in total since the beginning  of the pandemic. The total confirmed cases per million people in Poland is 958.7518

```
After running the program, it was verified that the yellow LED turned on, since the value obtained for n (approximately 959) is in the range stipulated for the yellow LED, that is, n >100 and n <3000. 

<ins>Analysis for the case of Portugal</ins>

```python
{
  "records": [
    {
      "fields": {
        "country_name": "Portugal",
        "value": 1.028176e+07,
        "year": "2018"
      },
      "recordid": "c9d8fb02c3a0fb513a5e7d5738a470581a7f3bd1",
      "datasetid": "world-population@kapsarc",
      "record_timestamp": "1970-01-01T00:00:00+00:00"
    }
  ],
  "nhits": 1,
  "facet_groups": [
    {
      "name": "country_name",
      "facets": [
        {
          "path": "Portugal",
          "name": "Portugal",
          "count": 1,
          "state": "refined"
        }
      ]
    },
    {
      "name": "year",
      "facets": [
        {
          "path": "2018",
          "name": "2018",
          "count": 1,
          "state": "refined"
        }
      ]
    }
  ],
  "parameters": {
    "timezone": "UTC",
    "refine": {
      "year": "2018",
      "country_name": "Portugal"
    },
    "format": "json",
    "rows": 1,
    "dataset": [
      "world-population@kapsarc"
    ]
  }
}
{
  "New Deaths_text": "+9",
  "Total Recovered_text": "29,
 445",
  "Total Cases_text": "44,
 416",
  "Total Deaths_text": "1,
 629",
  "New Cases_text": "+287",
  "Active Cases_text": "13,
 342",
  "Last Update": "2020-07-07 13:30",
  "Country_text": "Portugal"
}
There are +287 new cases in Portugal of COVID-19 as of today.  There are also +9 new deaths and 44,416 cases in total since the beginning  of the 
pandemic. The total confirmed cases per million people in Portugal is 4319.882.
MicroPython v1.12 on 2019-12-20; ESP32 module with ESP32
Type "help()" for more information.
```
After running the program, it was found that the red LED turned on, since the value obtained for n (approximately 4320) is in the range stipulated for the red LED, that is, and n>3000.

### Conclusion

After testing the code for different countries with different degrees of severity for the number of COVID-19 cases, we verified that they actually lit the correct LEDs for each situation, according to the ratio of total cases per million inhabitants.\
The code is quite simple and clear, however it could be simplified using an API that would obtain both information regarding the pandemic and the country's population. However, no API with these characteristics was found, we chose to use 2 APIs, in which one of them returned the number of inhabitants of each country.\
Still regarding REST services, it should be noted that none of the APIs used require a password, which makes it easier to use. A disadvantage of using this type of API is that the data is only updated at a certain time, so sometimes when running the code before it has been updated, the correct data is not obtained. In general, the code works by executing the commands properly and the expected results were obtained. 
