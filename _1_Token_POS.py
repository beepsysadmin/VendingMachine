import serial
import struct
import time
import threading
from datetime import datetime
import _3_Token_Payment
STX = 0x02
ETX = 0x03
ACK = 0x06
NCK = 0X15
LRC = 0x00
Seperator = 0x1C
TransactionDetails = []
transactionPass = False
clessError = False
ser = ""
    
def setSerialPort(serialStatus):
    global ser
    if (serialStatus == True):
        try:
            ser = serial.Serial(port='/dev/ttyACM0',
                                baudrate=115200,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS)
        except:
            ser = serial.Serial(port='/dev/ttyACM1',
                                baudrate=115200,
                                parity=serial.PARITY_NONE,
                                stopbits=serial.STOPBITS_ONE,
                                bytesize=serial.EIGHTBITS)
    elif (serialStatus == False):
        ser.close()


def sendSettlement():
    settlementDone = False
    settlementMsg = [
        0x02, 0x00, 0x18, 0x38, 0x38, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
        0x30, 0x30, 0x30, 0x43, 0x35, 0x30, 0x30, 0x30, 0x1C, 0x03, 0x41
    ]
    while True:
        time = str(datetime.now())[11:19]
        if ((time == "08:00:00") and (settlementDone == False)):
            fileData = open("logs.txt","a")
            setSerialPort(True)
            print("settlement")
            sendRequestCommand(settlementMsg)
            settlementDone = True
            fileData.write("settlement done at "+time)
            fileData.close()
            print("Settlement Message send")
            if (isACKReceived()):
                if (readSettlementData()):
                    sendAck()
                    setSerialPort(False)
        if (time != "08:00:00"):
            settlementDone = False

def sendDataToDashBoard():
    global TransactionDetails
    global clessError
    if (clessError != True):
        _3_Token_Payment.jsonData(TransactionDetails)

def makeVoidMessage(invoiceNumberList):
    LRC = 0x00
    Message = [0x00,0x54,0x38,0x38,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x43,0x32,0x30,0x30,0x30,0x1C,0x30,0x34,0x00,0x06,
               int(invoiceNumberList[0])+48,int(invoiceNumberList[1])+48,int(invoiceNumberList[2])+48,int(invoiceNumberList[3])+48,int(invoiceNumberList[4])+48,
               int(invoiceNumberList[5])+48,0x1C,0x50,0x31,0x00,0x20,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x1C,ETX]
    for i in Message:
        LRC = i ^ LRC
    Message = [STX,0x00,0x54,0x38,0x38,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x43,0x32,0x30,0x30,0x30,0x1C,0x30,0x34,0x00,0x06,
               int(invoiceNumberList[0])+48,int(invoiceNumberList[1])+48,int(invoiceNumberList[2])+48,int(invoiceNumberList[3])+48,int(invoiceNumberList[4])+48,
               int(invoiceNumberList[5])+48,0x1C,0x50,0x31,0x00,0x20,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x30,0x1C,ETX,LRC]
    return Message
    
    
def getInvoiceNumber():
    global TransactionDetails
    return TransactionDetails

def sendRequestCommand(msg):
    global ser
    ser.write(msg)


def makeMessage(amount):
    TransactionDetails.append(amount)
    LRC = 0x00
    if (amount < 1):
        amount = str(amount)
        if (len(amount) == 3):
            amount1 = amount[2]
            amount2 = 0
            amount1 = int(amount1) + 48
            amount2 = int(amount2) + 48
        else:
            amount1 = amount[2]
            amount2 = amount[3]
            amount1 = int(amount1) + 48
            amount2 = int(amount2) + 48
        Message = [
            0x00, 0x60, 0x38, 0x38, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
            0x30, 0x30, 0x30, 0x43, 0x31, 0x30, 0x30, 0x30, 0x1C, 0x30, 0x37,
            0x00, 0x12, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
            0x30, amount1, amount2, 0x1C, 0x50, 0x31, 0x00, 0x20, 0x30, 0x30,
            0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
            0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x1C, ETX
        ]
        for i in Message:
            LRC = i ^ LRC
        Message = [
            STX, 0x00, 0x60, 0x38, 0x38, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
            0x30, 0x30, 0x30, 0x30, 0x43, 0x31, 0x30, 0x30, 0x30, 0x1C, 0x30,
            0x37, 0x00, 0x12, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
            0x30, 0x30, amount1, amount2, 0x1C, 0x50, 0x31, 0x00, 0x20, 0x30,
            0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
            0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x1C, ETX, LRC
        ]
    elif (amount >= 1 and amount < 10):
        amount = str(amount)
        if (len(amount) == 3):
            amount1 = amount[0]
            amount2 = amount[2]
            amount1 = int(amount1) + 48
            amount2 = int(amount2) + 48
            Message = [
                0x00, 0x60, 0x38, 0x38, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x43, 0x31, 0x30, 0x30, 0x30, 0x1C,
                0x30, 0x37, 0x00, 0x12, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, amount1, amount2, 0x30, 0x1C, 0x50, 0x31,
                0x00, 0x20, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x1C, ETX
            ]
            for i in Message:
                LRC = i ^ LRC
            Message = [
                STX, 0x00, 0x60, 0x38, 0x38, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x30, 0x43, 0x31, 0x30, 0x30, 0x30,
                0x1C, 0x30, 0x37, 0x00, 0x12, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, amount1, amount2, 0x30, 0x1C, 0x50,
                0x31, 0x00, 0x20, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x1C, ETX, LRC
            ]
        elif (len(amount) == 4):
            amount1 = amount[0]
            amount2 = amount[2]
            amount3 = amount[3]
            amount1 = int(amount1) + 48
            amount2 = int(amount2) + 48
            amount3 = int(amount3) + 48
            Message = [
                0x00, 0x60, 0x38, 0x38, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x43, 0x31, 0x30, 0x30, 0x30, 0x1C,
                0x30, 0x37, 0x00, 0x12, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, amount1, amount2, amount3, 0x1C, 0x50, 0x31,
                0x00, 0x20, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x1C, ETX
            ]
            for i in Message:
                LRC = i ^ LRC
            Message = [
                STX, 0x00, 0x60, 0x38, 0x38, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x30, 0x43, 0x31, 0x30, 0x30, 0x30,
                0x1C, 0x30, 0x37, 0x00, 0x12, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, amount1, amount2, amount3, 0x1C, 0x50,
                0x31, 0x00, 0x20, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x1C, ETX, LRC
            ]
    elif (amount >= 10 and amount < 100):
        amount = str(amount)
        if (len(amount) == 4):
            amount1 = amount[0]
            amount2 = amount[1]
            amount3 = amount[3]
            amount1 = int(amount1) + 48
            amount2 = int(amount2) + 48
            amount3 = int(amount3) + 48
            Message = [
                0x00, 0x60, 0x38, 0x38, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x43, 0x31, 0x30, 0x30, 0x30, 0x1C,
                0x30, 0x37, 0x00, 0x12, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, amount1, amount2, amount3, 0x30, 0x1C, 0x50, 0x31,
                0x00, 0x20, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x1C, ETX
            ]
            for i in Message:
                LRC = i ^ LRC
            Message = [
                STX, 0x00, 0x60, 0x38, 0x38, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x30, 0x43, 0x31, 0x30, 0x30, 0x30,
                0x1C, 0x30, 0x37, 0x00, 0x12, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, amount1, amount2, amount3, 0x30, 0x1C, 0x50,
                0x31, 0x00, 0x20, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x1C, ETX, LRC
            ]
        else:
            amount1 = amount[0]
            amount2 = amount[1]
            amount3 = amount[3]
            amount4 = amount[4]
            amount1 = int(amount1) + 48
            amount2 = int(amount2) + 48
            amount3 = int(amount3) + 48
            amount4 = int(amount4) + 48
            Message = [
                0x00, 0x60, 0x38, 0x38, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x43, 0x31, 0x30, 0x30, 0x30, 0x1C,
                0x30, 0x37, 0x00, 0x12, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, amount1, amount2, amount3, amount4, 0x1C, 0x50,
                0x31, 0x00, 0x20, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x1C, ETX
            ]
            for i in Message:
                LRC = i ^ LRC
            Message = [
                STX, 0x00, 0x60, 0x38, 0x38, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x30, 0x43, 0x31, 0x30, 0x30, 0x30,
                0x1C, 0x30, 0x37, 0x00, 0x12, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, amount1, amount2, amount3, amount4, 0x1C,
                0x50, 0x31, 0x00, 0x20, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
                0x30, 0x30, 0x30, 0x30, 0x1C, ETX, LRC
            ]
    return Message


def getDetails(detailedMsg):
    global TransactionDetails
    sizeofMsg = len(detailedMsg)
    idx_list = [
        idx + 1 for idx, val in enumerate(detailedMsg) if val == Seperator
    ]
    res = [
        detailedMsg[i:j]
        for i, j in zip([0] + idx_list, idx_list +
                        ([sizeofMsg] if idx_list[-1] != sizeofMsg else []))
    ]
    TransactionDetails = []
    AcquirerName = []
    InvoiceNumber = []
    TerminalID = []
    TransactionAmount = []
    acquirerName = ""
    invoiceNumber = ""
    terminalID = ""
    transactionAmount = ""
    for data in res:
        if (data[0] == 48 and data[1] == 49):
            AcquirerName.append(data[4:])
        if (data[0] == 48 and data[1] == 50):
            TerminalID.append(data[4:])
        if (data[0] == 48 and data[1] == 52):
            InvoiceNumber.append(data[4:])
        if (data[0] == 48 and data[1] == 55):
            TransactionAmount.append(data[4:])
    for char in AcquirerName[0]:
        if int(char) != 0x1C:
            acquirerName = acquirerName + chr(char)
    for char in TerminalID[0]:
        if int(char) != 0x1C:
            terminalID = terminalID + chr(char)
    for char in InvoiceNumber[0]:
        if int(char) != 0x1C:
            invoiceNumber = invoiceNumber + chr(char)
    for char in TransactionAmount[0]:
        if int(char) != 0x1C:
            transactionAmount = transactionAmount + chr(char)
    transactionAmount = int(transactionAmount) / 100
    TransactionDetails.append(str(transactionAmount))
    TransactionDetails.append(acquirerName)
    TransactionDetails.append(invoiceNumber)
    TransactionDetails.append(terminalID)


def sendAck():
    global ser
    ser.write([ACK])


def checkTransactionStatus(recvMsg):
    global transactionPass
    # Transaction successful
    if (recvMsg[0] == 0x07):
        transactionPass = True
    # Transaction Failed
    elif (recvMsg[0] == 0x02):
        transactionPass = False
    getDetails(recvMsg)

    return transactionPass


def checkLRC(recvMessage, recvLRC, terminalStatus):
    LRC = 0x00
    sep = False
    acname = []
    for i in recvMessage:
        LRC = i ^ LRC
    # Receive data is not corrupted
    if (recvLRC == LRC):
        if (terminalStatus == True):
            return True
        elif (terminalStatus == False):
            return (checkTransactionStatus(recvMessage))
    else:
        return False


def readSettlementData():
    global ser
    message = []
    PosResponse = ser.read()
    PosResponse = struct.unpack('b', PosResponse)
    if PosResponse[0] == STX:
        while True:
            PosResponse = ser.read()
            PosResponse = struct.unpack('b', PosResponse)
            if PosResponse[0] == ETX:
                message.append(PosResponse[0])
                break
            message.append(PosResponse[0])
    recvLRC = ser.read()
    recvLRC = struct.unpack('b', recvLRC)
    return True


def readMessageData():
    global clessError
    global ser
    clessError = False
    message = []
    PosResponse = ser.read()
    PosResponse = struct.unpack('b', PosResponse)
    if PosResponse[0] == STX:
        while True:
            PosResponse = ser.read()
            PosResponse = struct.unpack('b', PosResponse)
            if PosResponse[0] == ETX:
                message.append(PosResponse[0])
                break
            message.append(PosResponse[0])
    recvLRC = ser.read()
    recvLRC = struct.unpack('b', recvLRC)
    if (message[0] == 0):  #cless error
        clessError = True
        return False
    elif (checkLRC(message, recvLRC[0], False)):
        clessError = False
        return True
    else:
        return False


def readResponse():
    global ser
    AckReceived = False
    STXReceived = False
    LRCCorrect = False
    TerminalMessage = []
    PosResponse = ser.read()
    PosResponse = struct.unpack('b', PosResponse)
    if PosResponse[0] == ACK:
        AckReceived = True
        STXReceived = False
        return (AckReceived, STXReceived, LRCCorrect)
    elif PosResponse[0] == STX:
        AckReceived = False
        STXReceived = True
        while True:
            PosResponse = ser.read()
            PosResponse = struct.unpack('b', PosResponse)
            if PosResponse[0] == ETX:
                TerminalMessage.append(PosResponse[0])
                break
            TerminalMessage.append(PosResponse[0])
        TerminalLRCrecv = ser.read()
        TerminalLRCrecv = struct.unpack('b', TerminalLRCrecv)
        if (checkLRC(TerminalMessage, TerminalLRCrecv[0], True)):
            LRCCorrect = True
            return (AckReceived, STXReceived, LRCCorrect)
        else:
            LRCCorrect = False
            return (AckReceived, STXReceived, LRCCorrect)


def isACKReceived():
    recvResponse = readResponse()
    if recvResponse[0] == True:  #Ack received successful
        return True
    elif recvResponse[1] == False:  #STX received
        return False


def checkTerminalStatus():
    global ser
    TerminalMessage = []
    message = [
        0x02, 0x00, 0x18, 0x38, 0x38, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30, 0x30,
        0x30, 0x30, 0x30, 0x38, 0x30, 0x30, 0x30, 0x30, 0x1C, 0x03, 0x3F
    ]
    ser.write(message)
    if (isACKReceived()):
        sendAck()
        if (readResponse()[2]):
            return True
        else:
            return False
    elif (isACKReceived() == False):
        # This to be implemented in case terimal gives STX again and again
        '''while True:
            readResponse()'''
        return False


thread = threading.Thread(target=sendSettlement)
thread.start()