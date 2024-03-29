## Projeto final de Eletrónica Digital e Microprocessadores

>Ana Cruz nº 201705191
>
>Ana Rita Diogo nº 201707122
>
> Mestrado Integrado em Engenharia Física
>
> 6 de Julho de 2020

### 1. Introdução

Este trabalho foi realizado no âmbito da cadeira de EDM, em que se pretendeu essencialmente utilizar a placa ESP32 para aceder a serviços REST. através da ligação à Internet, e consequentemente utilizá-los recorrendo às funcionalidades das componentes presentes na placa, como os LEDs e os botões.\
O projeto a seguir apresentado segue as condições anteriores, acedendo a serviços REST que devolvem informação estatística relacionada com a pandemia de COVID-19 por país e o número de habitantes do país em questão. Através do cálculo do número de casos por milhão de habitantes por país LEDs acendem de acordo com a gravidade da doença no país selecionado.

### 2. Projeto

O código para a realização do projeto foi desenvolvido com recurso ao *software* Studio Visual Code, sendo criados dois ficheiros *python* principais: boot.py onde foi escrito o código para efetuar a ligação à rede wifi e main.py onde se encontram os códigos para obter os dados das respetivas APIs que controlam os LEDs em função desses dados.\
A secção de código apresentada abaixo efetua a ligação da placa à rede wifi utilizando o módulo *network*, onde as variáveis ssid e password são strings que são respetivamente o SSID da rede a a palavra-passe de acesso à mesma:

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

Para obter os dados necessários ao cálculo da razão entre os casos e a população recorremos a duas APIs: uma que devolve dados quanto à pandemia de COVID-19, como o número total de casos, número de mortes e número de recuperados de um certo país, e outro que devolve o número da população desse mesmo país.
O *url* do serviço REST utilizado para obter os dados estatísticos[1] é o seguinte: <https://covid-19.dataflowkit.com/v1/portugal>, uma vez que pretendemos obter os dados que se referem a Portugal. Para aceder a qualquer outro país basta subtituir o nome no *url*, e para aceder ao dados mundiais substituímos pela palavra 'world'. A resposta, neste caso para Portugal, dada pelo serviço é apresentada da seguinte forma:

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

Já para obter o valor da população, o *url* do serviço REST[2] é o seguinte: <https://data.opendatasoft.com/api/records/1.0/search/?dataset=world-population%40kapsarc&rows=1&refine.year=2018&refine.country_name=Portugal>, sendo que definimos o link de forma a obter os dados do ano de 2018 (o mais recente que o *website* permite) e para Portugal, a resposta é apresentada da seguinte forma:

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

A partir das APIs podemos então calcular a razão de casos totais, que na primeira API correspodem ao valor de "Total Cases_text", por milhão de habitantes dividindo pelo valor de "value" dentro de "fields".

#### 2.2 LEDs

A ligação das componentes na placa é feita da seguinte forma:
 
![alt text](https://github.com/anaritadiogo/projetofinal/blob/master/esquema.png "Esquema do circuito eletrónico") \
Figura 1 - Esquema do circuito eletrónico.

![alt text](https://github.com/anaritadiogo/projetofinal/blob/master/placa.png "Placa com as ligações") \
Figura 2 - Ligações feitas na placa.

O código escrito para controlar os LEDs e imprimir o texto com os dados a partir das APIs é o seguinte:

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
   O programa acima demonstrado, permite através do número de casos ativos de Covid-19 em cada país acender os Leds medidante o estado em que se encontra a respetiva evolução da pandemia do país em questão. Para verificar o estado de de cada país definiu-se uma variável *n* , em que *n*=((número de casos)/(número de habitantes por país))10^6, em que desta forma permite averiguar o número de casos ativos na população por milhão de habitantes.
    A escolha foi feita de forma a que o LED verde acendesse, caso o valor de n fosse inferior a 300 , o Led amarelo caso 300<n<1000 e por fim LED vermelho caso o valor de n seja superior a 1000, os critérios escolhidos para a cor do Led foram feitos com base nos valores obtidos no seguinte *website*: <https://en.wikipedia.org/wiki/COVID-19_pandemic>.
    
![alt text](https://github.com/anaritadiogo/projetofinal/blob/master/mapa.png "Mapa do impacto da pandemia COVID-19.") \
Figura 1 - Total de casos de COVID-19 por cada milhão de habitantes.[3]

#### 2.3 Resultados
  Para a análise do nosso projeto, escolheram-se 3 países diferentes para averiguar o estado de evolução da pandemia em cada um deles, para isso fizeram-se a análise dos seguintes países: China, Polónia e Portugal.
 
<ins>Análise para o caso da China</ins>

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

Após a execução do programa verificou-se que o Led verde acendeu, pois o valor obtido para n(aproximadamente 60) encontra-se no intervalo estipulado para o Led verde, ou seja n<100.\

<ins>Análise para o caso da Polónia</ins>

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
Após a execução do programa verificou-se que o Led amarelo acendeu, pois o valor obtido para n(aproximadamente 959) encontra-se no intervalo estipulado para o Led amarelo, ou seja n >100 e n <3000.

<ins>Análise para o caso de Portugal</ins>

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
Após a execução do programa verificou-se que o Led vermelho acendeu, pois o valor obtido para n(aproximadamente 4320), encontra-se no intervalo estipulado para o Led vermelho, ou seja e n>3000.

### Conclusão

Após testar o código para diferentes países com diferentes graus de gravidade para o número de casos de COVID-19, verificámos que de facto acendiam os LEDs corretos para cada situação, de acordo com a razão dos casos totais por milhão de habitantes.\
O código é bastante simples e claro, no entanto poderia ser simplificado com a utilização de uma API que obtivesse tanto a informação em relação à pandemia e a população do país. No entanto, não foi encontrada nenhuma API com estas características, optou-se pela utilização de 2 APIs, em que uma delas devolvia o número de habitantes de cada país.\
Ainda quanto aos serviços REST é de notar que nenhuma das APIs usadas requer palavra passe, o que facilita a sua ultilização. Uma desvantagem do uso deste tipo de API é que os dados só são atualizados a uma certa hora, pelo que por vezes ao correr o código antes de terem sido atualizados, não são obtidos os dados corretos. Em geral, o código funciona executando os comandos devidamente e foram obtidos os resultados esperados.

### Bibliografia

>[1] - Coronavirus (COVID19) Tracker: <https://documenter.getpostman.com/view/11203393/SzfAz776?version=latest&fbclid=IwAR0h-icJdhMWDngEW6vmJhOEzVY5i6hYeATOeIHcIbqWeG_YiLZgWfg0Yto>
>
>[2] - World Population - Opendatadoft: <https://data.opendatasoft.com/explore/dataset/world-population%40kapsarc/api/?disjunctive.country_name&rows=1&timezone=GMT&refine.year=2018>
>
>[3] - COVID-19 pandemic: https://pt.wikipedia.org/wiki/Pandemia_de_COVID-19
