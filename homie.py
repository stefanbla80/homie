#!/usr/bin/python
import os, sys, time, datetime
from flask import Flask, jsonify, render_template
import RPi.GPIO as GPIO
import gpiozero
import random
import serial
import smbus
import math
import subprocess

#-----------------------------------------------------------------------------

app = Flask(__name__)

@app.route( "/" )
def index():
    return app.send_static_file('index.html')

#-----------------------------------------------------------------------------

@app.route('/gettemp1')
def gettemp1():
    temp1 = readTemp1()

@app.route('/gettemp2')
def gettemp2():
    temp2 = readTemp2()

@app.route('/getvolt1')
def getvolt1():
    volt1 = readI2c(0x48, 0x03)
    
@app.route('/getrpm1')
def getrpm1():
    rpm1 = readRPM1()

#-----------------------------------------------------------------------------

@app.route( "/getdyntemp1" )
def getdyntemp1():
    value = readTemp1()
    return jsonify( {"getdyntemp1": value} )

@app.route( "/getdyntemp2" )
def getdyntemp2():
    value = readTemp2()
    return jsonify( {"getdyntemp2": value} )

@app.route( "/getdynvolt1" )
def getdynvolt1():
    value = readVolt1(0x48, 0x03)
    return jsonify( {"getdynvolt1": value} )

@app.route( "/getdyncputemp" )
def getdyncputemp():
    value = getCpuTemperature()
    return jsonify( {"getdyncputemp": value} )

@app.route( "/getdynrpm1" )
def getdynrpm1():
    value = readRPM1()
    return jsonify( {"getdynrpm1": value} )

#-----------------------------------------------------------------------------

def readTemp1():
    # 1-wire Slave Datei lesen
    file1 = open('/sys/bus/w1/devices/28-01143398c928/w1_slave')
    filecontent = file1.read()
    file1.close()
 
    # Temperaturwerte auslesen und konvertieren
    stringvalue = filecontent.split("\n")[1].split(" ")[9]
    temperature = float(stringvalue[2:]) / 1000
 
    # Temperatur ausgeben
    rueckgabewert = '%6.1f' % temperature 
    return(rueckgabewert)

#-----------------------------------------------------------------------------

def readTemp2():
    # 1-wire Slave Datei lesen
    file2 = open('/sys/bus/w1/devices/28-0114339173a4/w1_slave')
    filecontent = file2.read()
    file2.close()
 
    # Temperaturwerte auslesen und konvertieren
    stringvalue = filecontent.split("\n")[1].split(" ")[9]
    temperature = float(stringvalue[2:]) / 1000
 
    # Temperatur ausgeben
    rueckgabewert = '%6.1f' % temperature 
    return(rueckgabewert)

#-----------------------------------------------------------------------------

i2c = smbus.SMBus(1)     # Erzeugen und Öffnen einer I2C-Instanz

def readVolt1(i2cDeviceAddr, channel):  #definition der function
    #Prüfen ob man das zweimal Auslesen wirklich
    wert2=i2c.read_byte_data (i2cDeviceAddr, channel)  # erster Zugriff weist Bauteil an, neu zu lesen
    time.sleep(0.5)
    wert2=i2c.read_byte_data (i2cDeviceAddr, channel)  # erst zweiter Zugriff liefert aktuellen Wert
    voltage2= wert2*((3.3/255)*5)
    if voltage2 > 2.0:
        rueckgabewert2 = '%6.1f' % voltage2
        return(rueckgabewert2)
    else:
        rueckgabewert2 = '%6.1f' % 0
        return(rueckgabewert2)

#-----------------------------------------------------------------------------

def getCpuTemperature():
    tempFile = open( "/sys/class/thermal/thermal_zone0/temp" )
    cpu_temp = tempFile.read()
    tempFile.close()
    return round(float(cpu_temp) / 1000, 1)

#-----------------------------------------------------------------------------

TACHO_PIN = gpiozero.Button(24)

class Tacho:
    def __init__(self):
        self.startzeit = None
        self.zaehler = 0
        self.messung = 0
        self.messung_old = datetime.datetime.now()

    def start_frequenzzaehlung(self):
        TACHO_PIN.when_pressed = self.zaehler_erhoehen
        self.startzeit = datetime.datetime.now()

    def stop_frequenzzaehlung(self):
        TACHO_PIN.when_pressed = None
        self.ergebnisse_auswerten()
        self.zaehler = 0

    def zaehler_erhoehen(self):
        now = datetime.datetime.now()
        self.messung = (now - self.messung_old).total_seconds()
        self.messung_old = now
        self.zaehler += 1

    def ergebnisse_auswerten(self):
        try:
            messung = 1 / self.messung
        except ZeroDivisionError:
            messung = 0     
        if messung >= 100:
            rpm = self.zaehler / 2 * 60
        else:
            rpm = messung / 2 * 60
        #print(rpm)
        return(rpm)

#-----------------------------------------------------------------------------
              
def readRPM1():
    tacho = Tacho()
    while True:
        tacho.start_frequenzzaehlung()
        while (datetime.datetime.now() - tacho.startzeit).total_seconds() < 1:
            time.sleep(0.02)
        tacho.stop_frequenzzaehlung()
        time.sleep(1)

#-----------------------------------------------------------------------------

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')