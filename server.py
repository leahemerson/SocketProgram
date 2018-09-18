import socket
import sys
import select
from datetime import datetime

""" Leah Emerson - COSC 264 Socket Program
server recieves a DT_Request packet, determines contents, and send DT_Response 
packet with coresponding message"""

def main():
    #Port 1- English  Port-2 Te reo Maori  Port-3 German
    port_1 = sys.argv[1]
    port_2 = sys.argv[2]
    port_3 = sys.argv[3]
    #Check validity of port numbers
    try:
        port_1 = int(port_1)
        port_2 = int(port_2)
        port_3 = int(port_3)
    except ValueError:
        print("Port value entered is not a number")
        sys.exit

    if (port_1 <1024 or port_1>64000):
        print("Port 1 entered is not between 1024 and 64000")
        sys.exit

    if (port_2 <1024 or port_2>64000):
        print("Port 2 entered is not between 1024 and 64000")
        sys.exit

    if (port_3 <1024 or port_3>64000):
        print("Port 3 entered is not between 1024 and 64000")
        sys.exit

    if (port_1 == port_2 or port_1 ==port_3 or port_2 == port_3):
        print("Port numbers cannot be of the same value")
        sys.exit

    #bind ports to host IP, creating 3 sockets
    sock_1, sock_2, sock_3 = bindPorts(port_1, port_2, port_3)
    
    
    inputs = [sock_1,sock_2,sock_3]
    dt = datetime.now().date()

    #processes inputs, which create requested response packets
    DT_Response, sender, sock = processInputs(inputs, dt, port_1, port_2, port_3)
    sock.sendto(DT_Response, sender)

def bindPorts(port_1, port_2, port_3):

    #gets IP of host
    IP = socket.gethostbyname(socket.gethostname())
   
    try:
        sock_1 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock_2 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
        sock_3 = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)

        sock_1.bind((IP, port_1))
        sock_2.bind((IP, port_2))
        sock_3.bind((IP, port_3))

    except IOError:
        print("Socket failed to be created and bind")
        sys.exit

    return sock_1, sock_2, sock_3

def processInputs(inputs, dt, port_1, port_2, port_3):
    
    while True:
        #CPU Usage?
        ready, _,_ = select.select(inputs, [], [],1)

        for s in ready:
            #buffer size of 7- should be 6 logn but make one longer to catch unwanted packets
            
            data, sender = s.recvfrom(7)

            #Checks if incoming packet is valid
            if (len(data) != 6):
                print('Packet less than 6 bytes long')
                continue

            magicNo= data[0]<<8 | data[1]
            packetType = data[2]<<8 | data[3]
            requestType =  data[4]<<8 | data[5]

            if (magicNo != 0x497E):
                print('MagicNo incorrect value')
                continue

            if (packetType != 0x0001):
                print('Packet Type incorrect value')
                continue

            if (requestType != 0x0001 and requestType != 0x0002):
                print('Request Type incorrect')
                continue

           #finds language code from port client selected
           #sets the socket to send the response packet through

            input_port = s.getsockname()[1]
            if (input_port == port_1):
                languageCode = 0x0001
                socketSender = inputs[0]
            elif (input_port == port_2):
                languageCode = 0x0002
                socketSender = inputs[0]
            elif (input_port == port_3):
                languageCode = 0x0003
                socketSender = inputs[0]

            date = datetime.now().date()
            time = datetime.now().time()
            #creates packet based on current day/time, language, and request time
            DT_Response = ResponsePacket(languageCode, date.year, date.month, date.day,time.hour,time.minute, requestType)

            return DT_Response, sender, socketSender
            
def ResponsePacket (LanguageCode,Year, Month, Day, Hour, Minute, RequestType):
   
    englishMonths = ['January', 'Februrary', 'March', 'April', 'May', 'June', 'July', 'August', 'September', 'October', 'November', 'December']
    maoriMonths = ['Kohitātea','Huitānguru', 'Poutūterangi', 'Paengawhāwhā', 'Haratua', 'Pipiri', 'Hōngongoi', 'Hereturikōkā', 'Mahuru', 'Whiringa-ā-nuku', 'Whiringa-ā-rangi','Hakihea']
    germanMonths = ['Januar', 'Februar', 'Marz', 'April', 'Mai', 'Juni', 'Juli', 'August', 'September', 'Oktober', 'November', 'Dezember']

    #determines the requested text based on language and request type
    if (LanguageCode == 0x0001 and RequestType == 0x001):
        text = "Today's date is " + str(englishMonths[Month - 1]) + " " + str(Day) + ", " + str(Year)
    elif (LanguageCode == 0x0002 and RequestType == 0x001):
        text = "Ko te ra o tenei ra ko " + str(maoriMonths[Month - 1])  + " " + str(Day) + ", " + str(Year)
    elif (LanguageCode == 0x0003 and RequestType == 0x001):
        text = "Heute ist der " + str(Day) + ". " + str(germanMonths[Month - 1]) + " " + str(Year)
    elif (LanguageCode ==0x0001 and RequestType == 0x0002):
        text = "The current time is " + str(Hour) + ":" + str(Minute)
    elif (LanguageCode ==0x0002 and RequestType == 0x0002):
        text = "Ko te wa o tenei wa " + str(Hour) + ":" + str(Minute)
    elif (LanguageCode ==0x0003 and RequestType == 0x0002): #else
        text = "Die Uhrzeit ist " + str(Hour) + ":" + str(Minute)

    #creates big-edian bytes for packet contents when more than 2 bytes
    magic_bits = (0x497E).to_bytes(2,'big')
    packet_bits = (0x0002).to_bytes(2, 'big')
    language_bits = LanguageCode.to_bytes(2, 'big')
    year_bits = Year.to_bytes(2, 'big')
    textBytes = text.encode('utf-8')
    length = len(textBytes)
    pkt = bytearray([magic_bits[0], magic_bits[1], packet_bits[0], packet_bits[1], language_bits[0], language_bits[1], year_bits[0],year_bits[1], Month, Day, Hour, Minute,length]) + textBytes

    return pkt
    
if __name__ == "__main__":
    main()


