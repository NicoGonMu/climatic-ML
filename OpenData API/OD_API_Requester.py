import json
import time
import codecs
import requests

#------------ Init calling parameters -------------
host = "https://opendata.aemet.es/opendata/api/valores/climatologicos/diarios/datos"
headers = { 'cache-control': "no-cache", 'api_key': 'APIKEY HERE' }
estacion = "/estacion/B278" #"Palma de Mallorca - Aeropuerto" station
#--------------------------------------------------

data = codecs.open('climData.json', 'w', encoding = 'utf-8')
#Loop through days 
for yy in range(2012, 2017):
    for m in range(1, 13):
        mm = str(m)
        mm = mm if (len(mm) > 1) else '0' + mm   
        for d in range (1, 29):
            dd = str(d)
            dd = dd if (len(dd) > 1) else '0' + dd 
            #URL construction
            date = str(yy) + "-" + mm + "-" + dd
            fechaini = "/fechaini/" + date + "T00:00:00UTC"
            fechafin = "/fechafin/" + date + "T23:59:59UTC"
            url = host + fechaini + fechafin + estacion
            #AEMET API call (GET)
            response = requests.get(url, headers = headers, verify = False)

            #Unserialize data into JSON
            responseData = json.loads(response.text)

            #Actual Data information
            response = requests.get(responseData['datos'], headers = headers, verify = False)

            #Convert data into JSON and write it
            line = json.loads(response.text)[0]
            line = json.dumps(dict(line), ensure_ascii = False) + "\n"            
            data.write(line)
            print(line)

            #For respecting qpm calls, wait
            time.sleep(3)
        time.sleep(5)
    time.sleep(5)
data.close()
