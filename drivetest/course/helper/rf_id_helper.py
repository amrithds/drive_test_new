import binascii

def getInputFromRFID(rfid, brand=None):
    """getInputFromRFID

    Args:
        rfid (_type_): rfid port object
        brand (_type_): Optional

    Returns:
        _type_: string
    """
    hex_string = ''
    if brand=='RADICAL' :
        s = rfid.readline()
        hex_string=s.decode('utf-8','ignore')[1:].strip()
    else:
        s = rfid.read(8)
        hex_string= binascii.hexlify(s).decode('utf-8')
    return hex_string