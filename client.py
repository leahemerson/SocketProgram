import socket
import sys
import select
""" Leah Emerson - COSC 264 Socket Program
client send a DT_Request Packet to server, requesting the current date or time"""

def main():
    #user inputs either 'date' or 'time', IP and port number to request from
    dt = str(sys.argv[1])
    IP = sys.argv[2]
    port = int(sys.argv[3])

    #checks validity of inputs
    if len(sys.argv) != 4:
        print("More than 3 inputs")
        sys.exit

    if(dt != 'time' and dt !='date'):
        print("Value entered is not equal to 'date' or 'time'")
        sys.exit

    if (port<1024 or port>64000):
        print("Port entered is not between 1024 and 64000")
        sys.exit
    
    try:
        socket.getaddrinfo(IP, port)
    except socket.gaierror:
        print("Host name does not exist")
        sys.exit
    if (dt == 'time'):
        RequestType = 0x0002
    else:
        RequestType = 0x0001
    #creates request packet
    DT_Request = createPacket(0x497E,0x0001, RequestType)
    #create socket and send packet 
    sock = socket.socket(socket.AF_INET,socket.SOCK_DGRAM)
    sock.sendto(DT_Request, (IP, port))
    #wait for response and print results and quit
    getResponse(sock)

def createPacket(MagicNo, PacketType, RequestType):
    #creates request packet using big- edian format
    magic_bits= MagicNo.to_bytes(2,'big')
    packet_bits = PacketType.to_bytes(2, 'big')
    request_bits = RequestType.to_bytes(2, 'big')
    pkt = bytearray([magic_bits[0],magic_bits[1],packet_bits[0], packet_bits[1],request_bits[0], request_bits[1]])
    return pkt

def getResponse(sock):

    #wait one second for responce packet
    wait = select.select([sock], [], [], 1)

    if wait[0]:
        #packet should be less than 100 bytes
        data,address = sock.recvfrom(100) 

        #checks validity of recieved packet
        if (len(data) < 13):
            print('Packet less than 13 bytes long')
            sys.exit

        magicNo= data[0]<<8 | data[1]
        packetType = data[2]<<8 | data[3]
        languageCode =  data[4]<<8 | data[5]
        year = data[6]<<8 | data[7]

        if (magicNo != 0x497E):
            print('MagicNo incorrect value')
            sys.exit
        elif (packetType != 0x0002):
            print('Packet Type incorrect value')
            sys.exit
        elif(languageCode != 0x0001 and languageCode!= 0x0002 and languageCode!= 0x0003):
            print('Language Code incorrect value')
            sys.exit 
        elif(year > 2100):
            print('Year greater than 2100')
            sys.exit
        elif (int(data[8])<=0 or int(data[8])>12):
            print('Month number not valid')
            sys.exit

        elif (data[9]<=0 or data[9] >31):
            print('Day not valid number')
            sys.exit
        elif(data[10]<0 or data[10]>23):
            print('Hour not valid number')
            sys.exit
        elif(data[11]<0 or data[11]>59):
            print('Minute not valid number')
            sys.exit
        elif(len(data)!= 13 + data[12]):
            print('Actual length does not equal calculated length')
            sys.exit
            
        #if all checks are correct print contents and quit
        else:
            print("Magic Number: " + str(hex(magicNo)))
            print("Packet Type: " + str(packetType))
            print("Language Code: " + str(languageCode))
            print("Year: " + str(year))
            print("Month: " + str(data[8]))
            print("Day: " + str(data[9]))
            print("Hour: " + str(data[10]))
            print("Minute: "+ str(data[11]))
            print("Text: " + str((data[12: ].decode("utf-8"))))
            sys.exit

if __name__ == "__main__":
    main()


