## Projeto final de Eletrónica Digital e Microprocessadores

>Ana Cruz nº 201705191
>
>Ana Rita Diogo nº 201707122
>
> Mestrado Integrado em Engenharia Física
>
> 6 de Julho de 2020

### 1. Introdução

O trabalho proposto para este projeto consiste na utilização da placa ESP32 Pico Kit para aceder a serviços REST através da ligação à Internet, e consequentemente utilizá-los recorrendo às funcionalidades das componentes presentes na placa, como os LEDs e os botões. O projeto a seguir apresentado segue as condições anteriores, acedendo a serviços REST que devolvem informação estatística relacionada com a pandemia de COVID-19 e número de habitantes do país em questão, e que em função do número de casos por milhão de habitantes por país acende os LED's de acordo com a gravidade da doença no país selecionado.

### 2. Projeto

O código para a realização do projeto foi desenvolvido com recurso ao *software* Studio Visual Code, sendo criados dois ficheiros *python* principais, boot.py onde foi escrito o código para efetuar a ligação à Wifi e main.py, onde se encontram os códigos para obter os dados da API e que controlam os botões em função desses dados.
A secção de código apresentada abaixo efetua a ligação da placa à rede Wifi utilizando o módulo *network*, onde as variáveis ssid e password são strings que são respetivamente o SSID da rede a a palavra-passe de acesso à mesma:

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

Para obter os dois dados necessários recorremos a duas APIs: uma que devolvia dados quanto à pandemia de COVID-19, como o número total de casos, número de mortes e número de recuperados de um certo país, e outro que devolvia o número da população desse mesmo país.
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

Já para obter o valor da população, o *url* do serviço REST[2] é o seguinte: <https://data.opendatasoft.com/api/records/1.0/search/?dataset=world-population%40kapsarc&rows=1&refine.year=2018&refine.country_name=Portugal>, sendo que definimos o link de forma a obter os dados do ano de 2018 (o mais recente que o *website* permite) e para Portugal. A resposta é apresentada da seguinte forma:

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

O código escrito para controlar os LEDs é o seguinte:

```python

from machine import Pin

red_led = Pin(21, Pin.OUT) #led vermelho
yellow_led = Pin(22, Pin.OUT) #led amarelo
green_led = Pin(19, Pin.OUT) #led verde

cases = 10        #casos de covid-19
population = 2000        #numero de habitantes

n = cases/(population/(10^6))  # casos por milhão de habitantes 

while True:
  if n <= 10: #menor que 10 casos por milhão de habitantes
    red_led.value(False)
    yellow_led.value(False)
    green_led.value(True)  #liga o led vermelho
    
  elif n <= 500: #maior que 500 casos por milhão de habitantes
    red_led.value(True) #liga o led verde
    yellow_led.value(False)
    green_led.value(False)

  else: #entre 10 e 500 casos por milhão de habitantes
    red_led.value(False)
    yellow_led.value(True) #liga o led amarelo
    green_led.value(False)

```
   O programa acima demonstrado, permite através do número de casos ativos de Covid-19 em cada país acender os Leds medidante o estado em que se encontra a respetiva evolução da pandemia do país em questão. Para verificar o estado de de cada país definiu-se uma variável n , em que n =(número de casos ativos)/(número de habitantes por país)*10^6, em que desta forma permite averiguar o número de casos ativos na população por milhão de habitantes.
    A escolha foi feita de forma a que o LED verde acendesse, caso o valor de n fosse inferior a 300 , o Led amarelo caso 300<n<1000 e por fim LED vermelho caso o valor de n seja superior a 1000, os critérios escolhidos para a cor do Led foram feitos com base nos valores obtidos no seguinte *website*: <https://en.wikipedia.org/wiki/COVID-19_pandemic>.
    
![alt text](https://github.com/anaritadiogo/projetofinal/blob/master/mapa.png "Mapa do impacto da pandemia COVID-19.") \
Figura 1 - Total de casos de COVID-19 por cada milhão de habitantes.[3]

#### 2.3 Resultados
  Para a análise do nosso projeto, escolheram-se 3 países diferentes para averiguar o estado de evolução da pandemia em cada um deles, para isso fizeram-se a análise dos seguintes países: Angola, Polónia e Portugal.
 
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


### Conclusão

Após testar o código para diferentes países com diferentes graus de gravidade para o número de casos de COVID-19, verificámos que de facto acendiam os LEDs corretos para cada situação, de acordo com a rãzão dos casos totais por milhão de habitantes.
O código é bastante simples e claro, no entanto poderia ser simplificado com a utilização de uma API que obtivesse tanto a informação em relação à pandemia e a população do país. No entanto não foi encontrada nenhuma API com estas características. Ainda quanto aos serviços REST é de notar que nenhuma das APIs usadas requer palavra passe, o que facilita a sua ultilização. Em geral, o código funciona executando os comandos devidamente e foram obtidos os resultados esperados.

### Bibliografia

>[1] - Coronavirus (COVID19) Tracker: <https://documenter.getpostman.com/view/11203393/SzfAz776?version=latest&fbclid=IwAR0h-icJdhMWDngEW6vmJhOEzVY5i6hYeATOeIHcIbqWeG_YiLZgWfg0Yto>
>
>[2] - World Population - Opendatadoft: <https://data.opendatasoft.com/explore/dataset/world-population%40kapsarc/api/?disjunctive.country_name&rows=1&timezone=GMT&refine.year=2018>
>
>[3] - COVID-19 pandemic: https://pt.wikipedia.org/wiki/Pandemia_de_COVID-19
