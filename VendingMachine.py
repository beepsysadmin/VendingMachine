#   Vending Machine
#   Dated : 13 August 2022
#   Last Modified : 13 August 2022
#   Implemented by : Shakeel
from Beep_Serial import Beep_Serial
import time
import struct
import _1_Token_POS
from datetime import date
from datetime import datetime

class Beep_Vending_Machine:
    def __init__(self):
        self.Initialize_VM_Msg1 = bytearray([0x01,0x01,0x10,0x96,0x01,0x02,0x3C,0x01,0xA9])
        self.Initialize_VM_Msg2 = bytearray([0x09,0x57,0x46,0x56,0x30,0x30,0x30,0x30,0x31,0x30,0x30,0x30,0x36,0x36,0x30,0x32,0x52,0x53,0x32,0x33,0x32,0x2D,0x4D,0x44,0x42,0x56,0x34,0x33,0x30,0x32,0xA6])
        self.Begin_Session = bytearray([0x03,0xFF,0xFF,0x01])
        self.Reset_Cmd = bytearray([0x00,0x00])
        self.Approve_Cmd = bytearray([0x05,0x05])
        self.Reject_Cmd = bytearray([0x06,0x06])
        self.End_Session = bytearray([0x07,0x07])
        self.beep_serial = Beep_Serial('/dev/ttyUSB0', 9600,8, "None", 1,120)
        self.VmResponseList_SecondInit = []
        self.product_details = []
        self.dispense_details = []
        self.product_price = ""
        self.Confirmation_Message = ""
        self.processing_first_initialization = False
        self.processing_second_initialization = False
        self.isSerialPortReady = False
        self.isVendingMachineReady = False
        self.EndSession = False
        self.today = date.today().strftime("%m/%d/%y")
        self.logFile = open("logs.txt","a")

    def check_serial_port(self):
        if(self.beep_serial.openSerialPort() == True):
            self.logFile.write(self.today+"\n")
            self.logFile.write("------------------------------------\n")
            self.logFile.write("serial port ready\n")
            self.logFile.write("It will take 2 Minutes for system to Initialize\n")
            self.logFile.write("Please wait!\n")
            self.isSerialPortReady = True
        else:
            self.isSerialPortReady = False
            self.logFile.write("Error Opening Serial Port\n")

    def process_response_Init(self):
        ####### Initialization Handling
        if(self.isVendingMachineReady == False):
            if(self.processing_first_initialization):
                while True:
                    if(int(self.beep_serial.read_Bytes().hex()) == 0x03):
                        self.processing_first_initialization = False
                        break
            if(self.processing_second_initialization):
                while True:
                    received_response = self.beep_serial.read_Bytes().hex()
                    if(received_response != ""):
                        self.VmResponseList_SecondInit.append(int(received_response))
                    if(received_response == ""):
                        for i in self.VmResponseList_SecondInit[len(self.VmResponseList_SecondInit)-7:len(self.VmResponseList_SecondInit)-1]:
                            self.Confirmation_Message += str(i)
                        if(bytes.fromhex(self.Confirmation_Message).decode() == '140115'):
                            self.processing_second_initialization = False
                            self.isVendingMachineReady = True
                            self.logFile.write('Initialization Success\n')
                            self.logFile.write('-------------------------------------------\n')
                            self.logFile.close()
                            break
                        elif(bytes.fromhex(self.Confirmation_Message).decode() != '140115'):
                            self.isVendingMachineReady = False
                            self.processing_second_initialization = False
                            self.logFile.write('Initialization Failed!\n')
                            self.logFile.write('-------------------------------------------')
                            self.logFile.close()
                            '''self.resetVM()
                            self.initialize_system()'''
                            #self.resetVm()
                            break
    ##################################################
                        
    def process_payment(self, product_price):
        self.logFile.write("Product Price: " +str(product_price)+"\n")
        msg = _1_Token_POS.makeMessage(float(product_price))
        _1_Token_POS.setSerialPort(True)
        if (_1_Token_POS.checkTerminalStatus() == True):
            time.sleep(1)
            _1_Token_POS.sendRequestCommand(msg)
            if (_1_Token_POS.isACKReceived() == True):
                if (_1_Token_POS.readMessageData() == True):
                    _1_Token_POS.TransactionDetails.append("2")
                    _1_Token_POS.sendAck()
                    _1_Token_POS.setSerialPort(False)
                    _1_Token_POS.sendDataToDashBoard()
                    self.logFile.write("SUCCESS\n")
                    return True
                else:
                    self.logFile.write("either LRC Corrupted or account is empty or Cless error\n")
                    _1_Token_POS.TransactionDetails.append("9")
                    _1_Token_POS.sendAck()
                    _1_Token_POS.setSerialPort(False)
                    _1_Token_POS.sendDataToDashBoard()
                    return False
            else:
                self.logFile.write("Terminal did not responded properly when transaction request was send\n")
                _1_Token_POS.TransactionDetails.append("9")
                _1_Token_POS.setSerialPort(False)
                _1_Token_POS.sendDataToDashBoard()
                return False
        else:
            self.logFile.write("Terminal seems to be offline or not responding\n")
            _1_Token_POS.setSerialPort(False)
            return False
        
    
    def process_approval(self):
        self.beep_serial.send_Bytes(self.Approve_Cmd)
        self.dispense_details.clear()
        self.EndSession = False
        while True:
                res = self.beep_serial.read_Bytes().hex()
                if(int(res) == 0x03):
                    while True:
                        res = self.beep_serial.read_Bytes().hex()
                        if(self.EndSession == False):
                            self.dispense_details.append(int(res))
                        if(int(res) == 0x03):
                            if(self.EndSession == True):
                                break
                            self.EndSession = True
                            continue
                            
                            
                    if(self.EndSession == True):
                        self.EndSession == False
                        break
    
    def process_denial(self):
        self.beep_serial.send_Bytes(self.Reject_Cmd)
        while True:
                res = self.beep_serial.read_Bytes().hex()
                if(int(res) == 0x03):
                    while True:
                        res = self.beep_serial.read_Bytes().hex()
                        if(int(res) == 0x03):
                            if(self.EndSession == True):
                                break
                            self.EndSession = True
                            continue
                            
                            
                    if(self.EndSession == True):
                        self.EndSession == False
                        break
                    
    def end_product_session(self):
        self.beep_serial.send_Bytes(self.End_Session)
        while True:
            res = self.beep_serial.read_Bytes().hex()
            if(int(res) == 0x03):
                self.logFile.write("session ended\n")
                self.logFile.write("----------------------------")
                break
    
    def voidTransaction(self,invoiceNumber):
        msg = _1_Token_POS.makeVoidMessage(list(invoiceNumber))
        print(invoiceNumber)
        print(msg)
        _1_Token_POS.setSerialPort(True)
        if (_1_Token_POS.checkTerminalStatus() == True):
            time.sleep(1)
            _1_Token_POS.sendRequestCommand(msg)
            if (_1_Token_POS.isACKReceived() == True):
                if (_1_Token_POS.readMessageData() == True):
                    _1_Token_POS.sendAck()
                    self.logFile.write("Failed and Voided\n")
                    _1_Token_POS.setSerialPort(False)
                    _1_Token_POS.TransactionDetails.append("9")
                    _1_Token_POS.sendDataToDashBoard()
                    return True
                else:
                    self.logFile.write("either LRC Corrupted or account is empty or Cless error unable to void\n")
                    _1_Token_POS.sendAck()
                    _1_Token_POS.setSerialPort(False)
                    return False
            else:
                self.logFile.write("Terminal did not responded properly when void request was send unable to void \n")
                _1_Token_POS.setSerialPort(False)
                return False
        else:
            self.logFile.write("Terminal seems to be offline or not responding uable to void\n")
            _1_Token_POS.setSerialPort(False)
            return False
        
            
                        
    def process_response(self, code):
        self.product_details.clear()
        self.product_price = ""
        if(code == "begin_session"):
            while True:
                res = struct.unpack('b',self.beep_serial.read_Bytes())
                if (res[0] == 0x03):
                    break
        if(code == "select_product"):
            while True:
                res = self.beep_serial.read_Bytes().hex()
                if(res != ''):
                    self.product_details.append(res)
                    if(int(res) == 0x03):
                        break
                elif(res == ''):
                    self.product_details.clear()
                    #print("time out")
                    break
        if(len(self.product_details)> 4):
            for i in self.product_details[6:9]:
                self.product_price += chr(int(i,16))
            self.product_price = str(int(self.product_price,16)/100)
            payment_successful = self.process_payment(self.product_price)
            if(payment_successful):
                self.process_approval()
                if(len(self.dispense_details)==8):
                    void_res = self.voidTransaction(_1_Token_POS.getInvoiceNumber()[2])
                self.end_product_session()
                time.sleep(5)
            elif(payment_successful == False):
                self.process_denial()
                self.end_product_session()
                time.sleep(5)
        else:
            self.product_details.clear()

    def begin_session(self):
        self.beep_serial.send_Bytes(self.Begin_Session)
        self.process_response("begin_session")
        
    def initialize_system(self):
        #### Processing First Initialization
        self.processing_first_initialization = True
        self.beep_serial.send_Bytes(self.Initialize_VM_Msg1)
        self.process_response_Init()

        #### Processing Second Initialization
        self.processing_second_initialization = True
        self.beep_serial.send_Bytes(self.Initialize_VM_Msg2)
        self.process_response_Init()
    
    def getVMStatus(self):
        return self.isVendingMachineReady
    
    def resetVM(self):
        self.beep_serial.send_Bytes(self.Reset_Cmd)


Vm = Beep_Vending_Machine()
Vm.check_serial_port()
Vm.resetVM()
Vm.initialize_system()
if(Vm.getVMStatus()):
    while True:
        Vm.begin_session()
        Vm.logFile = open("logs.txt","a")
        Vm.logFile.write("----------------------------------------\n")
        Vm.logFile.write("Select Product\n")
        Vm.logFile.write((str(datetime.now())[:19]))
        Vm.logFile.write("\n")
        print("Select Product\n")
        Vm.process_response("select_product")
        Vm.logFile.close()

    


