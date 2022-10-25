import serial

class Beep_Serial:
    def __init__(self, port, baudrate, bytesize, parity, stopbits, timeout):
        self.beep_ser = None
        self.port = port
        self.baudrate = baudrate
        self.bytesize = bytesize
        if(parity == "None"):
            self.parity = serial.PARITY_NONE
        self.stopbits = stopbits
        self.timeout = timeout
        self.SerialPortInitialized = False

    def openSerialPort(self):
        try:
            self.beep_ser = serial.Serial(port = self.port,
                                          baudrate = self.baudrate,
                                          bytesize = self.bytesize,
                                          parity = self.parity,
                                          stopbits = self.stopbits,
                                          timeout = self.timeout)
            self.SerialPortInitialized = True
            return True
        except Exception as e:
            return e
        
    def closeSerialPort(self):
        if(self.SerialPortInitialized == True):
            self.beep_ser.close()

    def send_Bytes(self, data):
        self.beep_ser.write(data)
        
    def read_Bytes(self):
        return (self.beep_ser.read())
        

