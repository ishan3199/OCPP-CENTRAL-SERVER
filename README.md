# OCPP-CENTRAL-SERVER
This is a python based Central management system server for OCPP along with some chargepoint testing tools.

#### Central management system server for Open chargepoint protocol is a websocket based server that listens to incoming chargepoint originated OCPP1.6 Json messages. 

Different ocpp handler functions are used that are able to handle incoming calls and return an OCPP1.6 JSON response.

In an Electric vehicle charging scenario, The EVSE (ev-charger) and the backend server communicates using the open charge point protocol. There are a set of PDU'S defined in the 
ocpp 1.6 documentation such as Bootnotification, Start transaction, Change config and other feature profile based functions that are implemented in my server as well as chargepoint script.


###### Chargepoint script.

A chargepoint simulator script is developed that mimics the evse originated OCPP messages and performs functions based on the server response.


###### Meter-values 

A package is developed in which I have developed functions to read voltage and frequency that can be imported and used by the chargepoint to send live meter values to server.


I have used the Web-sockets library, OCPP 1.6 library, asyncio, logging and modbus.


THANKS FOR READING!!!!!
