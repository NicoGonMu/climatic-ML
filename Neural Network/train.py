import os
import json
import codecs
import pybrain
import linecache
from pybrain.tools.shortcuts import buildNetwork
from pybrain.datasets import SupervisedDataSet
from pybrain.supervised.trainers import BackpropTrainer

#Create neural netwotk: 4 inputs, 30 hidden layers, 1 output
net = buildNetwork(4, 30, 1, bias = True)

#Create data structure: [tmax, tmin, presMax, presMin] -> [consumo]
ds = SupervisedDataSet(4, 1)

#Prepare data.json (Create a dictionary indexed by date):
consData = {}
datajson = open("../Extracted data/data.json")
months = {"enero":"01", "febrero":"02", "marzo":"03", "abril":"04", "mayo":"05", "junio":"06", 
          "julio":"07", "agosto":"08", "septiembre":"09", "octubre":"10", "noviembre":"11", "diciembre":"12", }
for line in datajson:
    data = json.loads(line)
    date = data['date'].split(' ')
    if len(date[0]) == 1: date[0] = "0" + date[0]
    consData[date[2] + "-" + months[date[1]] + "-" + date[0]] = float(data['generacion']) / 1000 
datajson.close()

#Read climData and insert examples to the network:
climData = open("../Extracted data/climData.json")
for line in climData:
    clim = json.loads(line)
    tmax = float(clim['tmax'].replace(',', '.'))
    tmin = float(clim['tmin'].replace(',', '.'))
    #Normalize pressure values
    presMax = float(clim['presMax'].replace(',', '.')) /100
    presMin = float(clim['presMin'].replace(',', '.')) /100
    print("(" + str(tmax) + ", " + str(tmin) + ", " + str(presMax) + ", " + str(presMin) + ") -> " + str(consData[clim['fecha']]))    
    ds.addSample([tmax, tmin, presMax, presMin], consData[clim['fecha']])    
climData.close()

valid = False
while(not valid):
    i = raw_input('Do you want a simple or a complete training? (For one epoch or until convergence) (S/C) ')
    if (i in "SCsc"): valid = True

#Train the network
trainer = BackpropTrainer(net, ds, momentum = 0.1, verbose = True, weightdecay = 0.01)
if(i in "Ss"):
    valid = False
    while(not valid):
        i = raw_input('How many epochs do you want the network to train?\n')
        if i.isdigit(): valid = True
    i = int(i)
    error = trainer.trainEpochs(i)
else:
    print("This operation can take a while. Please, be patient.")
    error = trainer.trainUntilConvergence()

print("Network TRAINED!\n")

#Test the network
valid = False
while(not valid):
    print("\n\nSelect a testing option:\n     1. Test a value.\n     2. Test file values (ones used to train the NN).\n     3. Exit.")
    i = input()
    if(i == 1):
        i = input('\nIntroduce an output to test or [] to exit (input format: "[tmax, tmin, presMax/100, presMin/100]"): ')
        res = net.activate(i) * 1000
        print(res)

    elif(i == 2):
        i = raw_input('Please, name the file where you want the results to be written in: ')
        climData = open("../Extracted data/climData.json")        
        results = codecs.open(i, 'a', encoding = 'utf-8')
        for line in climData:
            clim = json.loads(line)
            tmax = float(clim['tmax'].replace(',', '.'))
            tmin = float(clim['tmin'].replace(',', '.'))
            presMax = float(clim['presMax'].replace(',', '.')) /100
            presMin = float(clim['presMin'].replace(',', '.')) /100                
            result = str(net.activate([tmax, tmin, presMax, presMin]) * 1000) + "\n"
            results.write(result)
        results.close()
        climData.close()
        print("\nDONE. You can find the results on " + i + " file.")
                
    elif(i == 3): 
        valid = True
        break    