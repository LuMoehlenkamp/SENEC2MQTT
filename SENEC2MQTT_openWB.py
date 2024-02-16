"""
Bridge zwischen Senec Speicher und MQTT
"""

__author__ = "Patrick Horbach"
__copyright__ = "Copyright 2022, Patrick Horbach"
__credits__ = ["Nicolas Inden", "Mikołaj Chwalisz"]
__license__ = "Apache-2.0 License"
__version__ = "0.2.0"
__maintainer__ = "Patrick Horbach"
__email__ = ""
__status__ = "Production"


import time
import paho.mqtt.client as mqtt
import Senec
from queue import Queue
import math

# BROKER_IP = "localhost"
BROKER_IP = "192.168.178.20"
BROKER_PORT = 1883
SENEC_IP = "192.168.178.40"

# The callback for when the client connects to the broker
#def on_connect(client, userdata, flags, rc):
    # Print result of connection attempt
    # print("Connected with result code {0}".format(str(rc)))

# The callback for when a PUBLISH message is received from the server.
# def on_message(client, userdata, msg):
#     if msg.topic == "Keller/Solar/control/SENEC2MQTTInterval":
#         q.put(int(msg.payload.decode("utf-8")))
#         print("Intervall vom MQTT: " + str(msg.payload.decode("utf-8")))

client = mqtt.Client("SENEC-openWB-bridge")
#client.on_connect = on_connect  # Define callback function for successful connection
# client.on_message = on_message  # Define callback function for receipt of a message
client.connect(BROKER_IP, BROKER_PORT)  # connect to broker

# connect to Senec
info = Senec.SenecAPI(SENEC_IP)

# go on forever
client.loop_start()

# while not q.empty():

try:
    # get Data from Senec
    data_dict = info.get_values()
    # openWB PV-Modul
    # PV-Leistung in W, int, positiv
    client.publish("openWB/set/pv/1/W", int(-1*data_dict['ENERGY']['GUI_INVERTER_POWER']))
    # Erzeugte Energie in Wh, float, nur positiv
    # client.publish("openWB/set/pv/1/WhCounter", 1000 * data_dict['STATISTIC']['LIVE_PV_GEN'])
    # openWB Batteie
    # Speicherleistung in Wall, int, positiv Ladung, negativ Entladung
    client.publish("openWB/set/houseBattery/W", int(data_dict['ENERGY']['GUI_BAT_DATA_POWER']))
    # Ladestand des Speichers, int, 0-100
    client.publish("openWB/set/houseBattery/%Soc", int(data_dict['ENERGY']['GUI_BAT_DATA_FUEL_CHARGE']))
    # openWB Strombezugsmodul
    # Bezugsleistung in Watt, int, positiv Bezug, negativ Einspeisung
    client.publish("openWB/set/evu/W", int(data_dict['ENERGY']['GUI_GRID_POW']))
    # Strom in Ampere für Phase1, float, Punkt als Trenner, positiv Bezug, negativ Einspeisung; SENEC liefert den Strom ohne VZ, daher nehmen wir das VZ von der Leistung
    client.publish("openWB/set/evu/APhase1", math.copysign(data_dict['PM1OBJ1']['I_AC'][0], data_dict['PM1OBJ1']['P_AC'][0]))
    # Strom in Ampere für Phase2, float, Punkt als Trenner, positiv Bezug, negativ Einspeisung; SENEC liefert den Strom ohne VZ, daher nehmen wir das VZ von der Leistung
    client.publish("openWB/set/evu/APhase2", math.copysign(data_dict['PM1OBJ1']['I_AC'][1], data_dict['PM1OBJ1']['P_AC'][1]))
    # Strom in Ampere für Phase3, float, Punkt als Trenner, positiv Bezug, negativ Einspeisung; SENEC liefert den Strom ohne VZ, daher nehmen wir das VZ von der Leistung
    client.publish("openWB/set/evu/APhase3", math.copysign(data_dict['PM1OBJ1']['I_AC'][2], data_dict['PM1OBJ1']['P_AC'][2]))
    # Bezogene Energie in Wh, float, Punkt als Trenner, nur Positiv
    #client.publish("openWB/set/evu/WhImported", 1000 * data_dict['STATISTIC']['LIVE_GRID_IMPORT'])
    # Eingespeiste Energie in Wh, float, Punkt als Trenner, nur Positiv
    #client.publish("openWB/set/evu/WhExported", 1000 * data_dict['STATISTIC']['LIVE_GRID_EXPORT'])

    # Spannung in Volt für Phase1, float, Punkt als Trenner
    client.publish("openWB/set/evu/VPhase1", data_dict['PM1OBJ1']['U_AC'][0])
    # Spannung in Volt für Phase2, float, Punkt als Trenner
    client.publish("openWB/set/evu/VPhase2", data_dict['PM1OBJ1']['U_AC'][1])
    # Spannung in Volt für Phase3, float, Punkt als Trenner
    client.publish("openWB/set/evu/VPhase3", data_dict['PM1OBJ1']['U_AC'][2])
    # Netzfrequenz in Hz, float, Punkt als Trenner
    client.publish("openWB/set/evu/HzFrequenz", data_dict['PM1OBJ1']['FREQ'])
    # PV1
    # Grid export limit (percent)
    # client.publish("Keller/Solar/GridLimit", data_dict['PV1']['POWER_RATIO'])
    #Leistung 1
    client.publish("openWB/set/evu/WPhase1", data_dict['PM1OBJ1']['P_AC'][0])
    #Leistung 2
    client.publish("openWB/set/evu/WPhase2", data_dict['PM1OBJ1']['P_AC'][1])
    #Leistung 3
    client.publish("openWB/set/evu/WPhase3", data_dict['PM1OBJ1']['P_AC'][2])
except:
    print("da ging was schief, später nochmal probieren")
# time.sleep(intervall)
