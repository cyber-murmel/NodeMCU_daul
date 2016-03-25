#! /usr/bin/env python2.7
import argparse
import serial
import time

chunksize=48                                                            # maximum chunk size possible

def main():
    a =     getArguments()
    f =     open(a.file, "rw")
    name =  a.file.split("/")[-1].split("\\")[-1]
    ser =   serial.Serial(a.serial, 9600, 8, "N", 1)
    changeBaud(ser, a.baud)
    if(a.upload):
        content = f.read()
        execLua(ser, "file.open(\""+name+"\", \"w\")")
        while(len(content)>0):                                          # repeat until all of the string is been sent
            code=",".join(map(str,map(ord,list(content[:chunksize]))))  # convert every char into string of ordinal
            execLua(ser, "file.write(string.char("+code+"))")           # make ESP write code to file
            content=content[chunksize:]                                 # cut off remaining content string
        execLua(ser, "file.flush();file.close()")
    changeBaud(ser, 9600)
    ser.close()
    f.close()

################################

def getArguments():
    parser = argparse.ArgumentParser(description='Down and upload files from and to an ESP8266 running NodeMCU. Createt by MarBle.')
    parser.add_argument("-f", "--file"    , type=str           ,    required=True,  help='filepath to read from or write to')
    parser.add_argument("-d", "--download", action="store_true",                    help='downloads file from the ESP to your computer')
    parser.add_argument("-u", "--upload"  , action="store_true",                    help='uploads file from your computer to the ESP')
    parser.add_argument("-l", "--list"    , action="store_true",                    help='list the files stored on the ESP')
    parser.add_argument("-r", "--remove"  , action="store_true",                    help='remove file from the ESP')
    parser.add_argument("-v", "--verbose" , action="store_true",                    help='print the serial communication to the terminal')
    parser.add_argument("-b", "--baud"    , type=int           ,    default=9600,   help='change the baud rate')
    parser.add_argument("-s", "--serial"  , type=str           ,    required=True,  help='path to serial device')
    return parser.parse_args()

def execLua(ser, command):
    ser.write(command)
    echo=""
    while(not (command in echo)):
        echo+=ser.read()
    print(echo)
    ser.write("\r\n")
    echo=""
    while(not ("\r\n> " in echo)):
        echo+=ser.read()
    #print(echo)

def changeBaud(ser, baud):
    ser.write("uart.setup(0," + str(baud) + ",8,0,1,1)\r\n")        # make ESP change to requested baud rate
    ser.close()                                                     # close old connection
    ser.baudrate=baud                                               # change baud rate
    time.sleep(0.5)
    ser.open()                                                      # reopen serial connection with requested baud rate
    execLua(ser, "")

if __name__ == "__main__":
    main()