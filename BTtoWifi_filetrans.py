import socket
import threading
import random
import os
import time
import bluetooth

#default global vars
TCP_IP = 'None'
#TCP_IP = '127.0.0.1'
TCP_PORT = 5001
connected = False
traded = False
server = False
client = False

s = None
sock = None
conn = None
addr = None
userinputAddr = None
btconnected = False

def menu():
    global traded

    print_lock = threading.Lock()

    t0 = threading.Thread(target = connectBT)
    t0.start()
    t0.join()
    
    t1 = threading.Thread(target = connectW)
    t1.setDaemon(True)
    t1.start()
    t1.join()

    if connected == True:
        print("CONNECTED!")
        t2 = threading.Thread(target=receiveFile)
        t2.setDaemon(True)
        t2.start()
    else:
        print("Connection Failed")
    while True:
        with print_lock:
            print("=================================================================")
            print("\t\t\tMain Menu")
            print("=================================================================")
            print "1) Trade Directories\n2) Send File\n0) EXIT\n"
            print("=================================================================")
            try:
                y = int(raw_input("Please enter a menu option (0, 1, 2, or Enter to Refresh):\n> "))
                
            except:
                y = 9
            if y==1:
                sendDir()
            elif y==2:
                sendFile()

            elif y==0:
                if connected == True:
                    if server:
                        conn.close()
                    elif client:
                        sock.close()
                    exit()
                else:
                    exit()
                break
            else:
                continue


def connectW():
    global TCP_IP
    global TCP_PORT
    global conn
    global addr
    global connected
    global sock
    global server
    global client
    global s

    attempts = 10
    while (attempts !=0):       #for attempts in range 10,0
        randnum = random.randint(0,1)
        if randnum == 0:
            try:    #Server
                s = socket.socket( socket.AF_INET, socket.SOCK_STREAM)
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)     #Refreshes Socket for use immediately
                s.bind(('', TCP_PORT))
                s.listen(1)
                s.settimeout(8)
                conn, addr = s.accept()
                server = True
                print("Connected as Server")
                connected = True
                attempts = 0
                break
            except Exception, e:
                print ("Could not create Server Socket!")
                attempts = attempts-1

        elif randnum == 1:
            try:    #Client
                sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                sock.connect((TCP_IP, TCP_PORT))
                connected = True
                client = True
                print("Connected as Client")
                attempts = 0
                break
            except Exception, e:
                print "Could not connect"
                attempts=attempts-1
    return

def sendDir():
    global server
    global client
    global conn
    global sock

    cwd = os.getcwd()
    dirlist = os.listdir(cwd)
    if server == True:
        for filename in dirlist:
            conn.send(filename)     #If server, send via conn
            time.sleep(.2)
    elif client == True:
        for filename in dirlist:
            sock.send(filename)     #If Client, send via sock
            time.sleep(.2)
    return

# def receiveDir(data):
#     global server
#     global client
#     global conn
#     global sock
#     print_lock = threading.Lock()
    
#     print("Files in directory: ")
#     if server == True:
#         with print_lock:
#             print(data)

#     elif client == True:
#         with print_lock:
#             print(data)

#     return

def receiveFile():
    BUFFER_SIZE = 1024

    global conn
    global addr
    global sock
    global server
    global client
    trigger = "FILEisBeingSent"
    print_lock = threading.Lock()

    while True:
        try:
            if server == True:
                Rpacket = conn.recv(BUFFER_SIZE)
                conn.settimeout(2)
                if Rpacket != trigger:
##                    receiveDir(Rpacket)
                    with print_lock:
                        print(Rpacket)
                    conn.settimeout(99)
                    continue

                else:
                    Name = raw_input("Save File as?: \n")     #If Server, receive from conn
                    fout = open(Name, 'wb')
                    while Rpacket:
                        try:
                            Rpacket = conn.recv(BUFFER_SIZE)
                            time.sleep(.2)
                            if Rpacket != trigger:
                                fout.write(Rpacket)
                                time.sleep(.2)
                        except:
                            conn.settimeout(99)
                            break
                    fout.close()
                    print "received file\n"

            elif client == True:
                Rpacket = sock.recv(BUFFER_SIZE)
                sock.settimeout(2)
                if Rpacket != trigger:
##                    receiveDir(Rpacket)
                    with print_lock:
                        print(Rpacket)
                    sock.settimeout(99)
                    continue
                else:
                    Name = raw_input("Save File as?: \n")     #If Client, receive from sock
                    fout = open(Name, 'wb')
                    while Rpacket:
                        try:
                            Rpacket = sock.recv(BUFFER_SIZE)
                            if Rpacket != trigger:
                                time.sleep(.2)
                                fout.write(Rpacket)
                                time.sleep(.2)
                        except:
                            sock.settimeout(99)
                            break
                    fout.close()
                    print "received file\n"

        except Exception, e:
            continue

def sendFile():
    global sock
    trigger = "FILEisBeingSent"

    #bind is server
    BUFFER_SIZE = 1024
    MESSAGE = raw_input("Send Which File?: ie. filename.ext\n")

    if server == True:
        try: f = open(MESSAGE,'rb')
        except IOError:
            print "File Not Found"
            return
        packet = trigger    #Encode and send trigger packet
        conn.send(packet)
        packet = f.read(BUFFER_SIZE)    #Encode packet for file
        while (packet):
            conn.send(packet)       #If server, send via conn
            packet = f.read(BUFFER_SIZE)
        f.close()
        print("Sent data")

    elif client == True:
        try: f = open(MESSAGE,'rb')
        except IOError:
            print "File Not Found"
            return
        packet = trigger
        sock.send(packet)
        packet = f.read(BUFFER_SIZE)    #Encode first packet
        while (packet):
            sock.send(packet)       #If client, send via sock
            packet = f.read(BUFFER_SIZE)
        f.close()
        print("Sent data")
    else:
        print "No Connection"
    return

def connectBT():
    global btconnected
    for attempts in range (0,10):
        randnum = random.randint(0,1)       #RNG to randomize server/client job
        if btconnected == True:
            break
        elif randnum == 0:
            bt_server()                     #call server job
        elif randnum == 1:
            BT_findNearbyDevices()          #function to discover nearby devices
            bt_client()                     #call client job

def bt_server():
    global btconnected
    global TCP_IP
    bt_s_sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
    bt_s_port = 3
    print("Waiting for connections from BT Client")
    while True:
        bt_s_sock.bind(('', bt_s_port))
        bt_s_sock.listen(1)

        client_sock, address = bt_s_sock.accept()
        print("Accepted connection from BT Client: %s" % str(address))

        print("Waiting for data from BT Client...")
        total  = 0
        try:
            data = client_sock.recv(1024)
            TCP_IP = data
            print data
        except bluetooth.BluetoothError as e:
            print("bt_server inner 'Try' failed")
            break
    return

def bt_client():
    global btconnected
    global userinputAddr
    bt_c_port = 3
    ipaddr = [l for l in ([ip for ip in socket.gethostbyname_ex(socket.gethostname())[2] if not ip.startswith("127.")][:1], [[(s.connect(('8.8.8.8', 53)), s.getsockname()[0], s.close()) for s in [socket.socket(socket.AF_INET, socket.SOCK_DGRAM)]][0][1]]) if l][0][0]
    print("userinputAddr: "), userinputAddr
    try:
        bt_c_sock=bluetooth.BluetoothSocket(bluetooth.RFCOMM)
        bt_c_sock.connect((userinputAddr, bt_c_port))
        btconnected = True
        bt_c_sock.send(ipaddr)
        bt_c_sock.close()
    except Exception, e:
        print("Could not connect as BT client")
    return

def BT_findNearbyDevices():
    global userinputAddr
    print("=================================================================")
    print("Scanning for nearby devices...")
    nearby_devices = bluetooth.discover_devices()
    i = 0
    bd_addrList = []
    bd_nameList = []
    print("=================================================================")
    print("Found Nearby Devices:")
    for bdaddr in nearby_devices:
        target_name = bluetooth.lookup_name(bdaddr)
        target_address = bdaddr
        bd_addrList.append(target_address)
        bd_nameList.append(target_name)
        print("\n"), target_name,("\twith addresses:\t"), target_address
    try:
        userinputAddr = raw_input("\nPlease enter one of the MAC addresses discovered\nALL-CAPS Format: XX:XX:XX:XX:XX:XX:\n> ")
        print("You have entered: "), userinputAddr
    except:
        print("Try again")
    return

def main():
    menu()

if __name__== "__main__":
    main()
