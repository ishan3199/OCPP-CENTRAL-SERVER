# https://ctlsys.com/support/how_to_compute_the_modbus_rtu_message_crc/
#==============================================================
# Compute the MODBUS RTU CRC
#
#==============================================================
def calcCRC(buf, len):
    crc = 0xFFFF
    pos = 0
    while (pos < len):
        crc ^= buf[pos]          # XOR byte into least sig. byte of crc
        i = 8
        while (i != 0):
        # Loop over each bit
            if ((crc & 0x0001) != 0):           # If the LSB is set
                crc >>= 1                       # Shift right and XOR 0xA001
                crc ^= 0xA001
            else:                                # Else LSB is not set
                crc >>= 1                        # Just shift right
            i = i - 1
        pos = pos + 1

    msb = ((crc>>8)&0x00FF)
    lsb = (crc&0x00FF)
    list_reversed = [lsb, msb]
    return list_reversed