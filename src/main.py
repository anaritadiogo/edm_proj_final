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
  url1 = "https://data.opendatasoft.com/api/records/1.0/search/?dataset=world-population%40kapsarc&rows=1&refine.country_name=Poland&refine.year=2018"
  url2 = "https://covid-19.dataflowkit.com/v1/poland"
  r1 = urequests.get(url1).json()
  r2 = urequests.get(url2).json()
  prettify(dumps(r1))
  prettify(dumps(r2))

  casos_ativos1 = r2["Total Cases_text"]  #casos ativos de covid-19
  casos_ativos1 = casos_ativos1.replace(',','')
  casos_ativos = float(casos_ativos1)

  pop = r1["records"][0]["fields"]["value"]    #Número de habitantes

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

