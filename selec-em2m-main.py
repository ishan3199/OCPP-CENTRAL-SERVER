import MODBUS_CRC16
import struct
import serial


# code developed for sending data through ocpp and import this file to server script and use below functions


# Register address list
#


EM2M_DEFAULT_SLAVE_ADDRESS = 0x01
FUNCTION_CODE = 0x04

TOTAL_ACTIVE_ENERGY_REG = 0x01
IMPORT_ACTIVE_ENERGY_REG = 0x03
EXPORT_ACTIVE_ENERGY_REG = 0x05
TOTAL_REACTIVE_ENERGY_REG = 0x07
IMPORT_REACTIVE_ENERGY_REG = 0x09
EXPORT_REACTIVE_ENERGY_REG = 0x0B
APPARENT_ENERGY_REG = 0x0D
ACTIVE_POWER_REG = 0x0F
REACTIVE_POWER_REG = 0x11
APPARENT_POWER_REG = 0x13
VOLTAGE_REG = 0x15
CURRENT_REG = 0x17
POWER_FACTOR_REG = 0x19
FREQUENCY_REG = 0x1B
MAX_DEMAND_ACTIVE_POWER_REG = 0x1D
MAX_DEMAND_REACTIVE_POWER_REG = 0x1F
MAX_DEMAND_APPARENT_POWER_REG = 0x21


COM_PORT_NAME = 'COM7'  #change it for raspbery pi
#============================================================

def readVoltage():
    ser = serial.Serial(COM_PORT_NAME, 9600, 8, 'N', 1, timeout=3, writeTimeout=4, interCharTimeout=3)
    if(True == ser.is_open):
        print("Serial port Opened Successfully")
        str = [EM2M_DEFAULT_SLAVE_ADDRESS, 4, 0, VOLTAGE_REG, 0, 2]
        len_str = len(str)
        crc_list = MODBUS_CRC16.calcCRC(str, len_str)
        str.append(crc_list[0])
        str.append(crc_list[1])
        ser.write(str)
        response = ser.read(9)
        voltageByte = response[3:7]
        voltageFloatTuple = struct.unpack('>f', voltageByte)   #big endian
        voltage = voltageFloatTuple[0]
        ser.close()
        print("Serial port Closed")
        return "SUCCESS", voltage
    else:
        print("Serial port failed to open")
        return "FAILURE", 0.00
#============================================================

def readFrequency():
    ser = serial.Serial(COM_PORT_NAME, 9600, 8, 'N', 1, timeout=3, writeTimeout=4, interCharTimeout=3)
    if(True == ser.is_open):
        print("Serial port Opened Successfully")
        str = [EM2M_DEFAULT_SLAVE_ADDRESS, 4, 0, FREQUENCY_REG, 0, 2]
        len_str = len(str)
        crc_list = MODBUS_CRC16.calcCRC(str, len_str)
        str.append(crc_list[0])
        str.append(crc_list[1])
        ser.write(str)
        response = ser.read(9)
        FreqByte = response[3:7]
        FreqFloatTuple = struct.unpack('>f', FreqByte)   #big endian
        Freq = FreqFloatTuple[0]
        ser.close()
        print("Serial port Closed")
        return "SUCCESS", Freq
    else:
        print("Serial port failed to open")
        return "FAILURE", 0.00



