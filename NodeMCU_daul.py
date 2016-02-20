#! /usr/bin/env python2.7
import argparse
import serial
import time

chunksize = 56;                                                        # maximum chunk size possible

def sendLine(outstring):
	ser.write(outstring+"\r\n")                                        # send string with carriage return and linefeed at the end

def waitForPrompt():
	line=""
	while(line[-2:]!="> "):                                            # wait until returning line is promt symbol of Lua shell
		line+=ser.read()

if __name__ == "__main__":

	#get Command Line Arguments
	parser = argparse.ArgumentParser(description='Down and upload files from and to an ESP8266 running NodeMCU. Createt by MarBle.')
	parser.add_argument("-f", "--file"    , type=str           , help='filepath to read from or write to')
	parser.add_argument("-d", "--download", action="store_true", help='downloads file from the ESP to your computer')
	parser.add_argument("-u", "--upload"  , action="store_true", help='uploads file from your computer to the ESP')
	parser.add_argument("-v", "--verbose" , action="store_true", help='print the serial communication to the terminal')
	parser.add_argument("-b", "--baud"    , type=int           , default = 9600	, help='change the baud rate')
	parser.add_argument("-s", "--serial"  , type=str           , help='path to serial device')
	args = parser.parse_args()


	#only allow either up or downloading
	if not (args.upload^args.download):
		print("Don't know what to do. (Set either -u oder -d)")
		exit()


	#### asserting ####
	try:    f=open(args.file, "rw")
	except: print("Can't open file."); exit()

	try:    ser = serial.Serial(args.serial, 9600, 8, "N", 1)          # open connection to ESP with 9600 baud
		    time.sleep(0.1)                                            # wait a little
		    sendLine("uart.setup( 0, "+str(args.baud)+", 8, 0, 1, 1)") # make ESP change to requested baud rate
		    ser.close()                                                # close old serial connection
		    ser = serial.Serial(args.serial, args.baud, 8, "N", 1)     # open new serial connection with requested baud rate
		    time.sleep(0.1)                                            # wait a little
	except: print("could not open serial"); exit()
	

	#### uploading ####
	if(args.upload):
		name=args.file.split("/")[-1].split("\\")[-1]                  # extract name from file path (Linux and Windows compatible)
		content=f.read()                                               # read content to string
		ser.reset_input_buffer()                                       # delete old prompt sign
		sendLine("file.open(\""+name+"\", \"w\")")                     # open file on ESP
		waitForPrompt()
		while(len(content)>0):                                         # repeat until all of the string is been sent
			code=",".join(map(str,map(ord,list(content[:chunksize])))) # convert every char into string of ordinal
			sendLine("file.write(string.char("+code+"))")              # make ESP write code to file
			content=content[chunksize:]                                # cut off remaining content string
			waitForPrompt()
		sendLine("file.flush();file.close()")                          # flush and close file on ESP
		waitForPrompt()

	#close everything
	sendLine("uart.setup( 0, 9600, 8, 0, 1, 1)")                       # reset UART speed
	ser.close()
	f.close()