#! /usr/bin/env python2.7
import argparse
import serial
import time

chunksize = 56;	# maximum chunk size possible

def sendLine(outstring):
	ser.write(outstring+"\r\n")

def waitForPrompt():
	line=ser.read()
	while(line[-2:]!="> "):
		line+=ser.read()

if __name__ == "__main__":

	#get Command Line Arguments
	parser = argparse.ArgumentParser(description='Down and upload files from and to an ESP8266 running NodeMCU. Createt by MarBle.')
	parser.add_argument("-f", "--file", type=str, help='filepath to read from or write to')
	parser.add_argument("-d", "--download", action="store_true", help='downloads file from the ESP to your computer')
	parser.add_argument("-u", "--upload", action="store_true", help='uploads file from your computer to the ESP')
	parser.add_argument("-v", "--verbose", action="store_true", help='print the serial communication to the terminal')
	parser.add_argument("-b", "--baud", type=int, default = 9600	, help='change the baud rate')
	parser.add_argument("-s", "--serial", type=str, help='path to serial device')
	args = parser.parse_args()


	#only allow either up or downloading
	if not (args.upload^args.download):
		print("Don't know what to do. (Set either -u oder -d)")
		exit()


	#### asserting ####
	try: # to open file
		f=open(args.file, "rw")
	except:
		print("Can't open file."); exit()

	try: # to open serial
		ser = serial.Serial(port=args.serial, baudrate=9600, bytesize=8, parity="N", stopbits=1)
		time.sleep(0.1)
		sendLine("uart.setup( 0, "+str(args.baud)+", 8, 0, 1, 1)")
		ser.close()
		ser = serial.Serial(port=args.serial, baudrate=args.baud, bytesize=8, parity="N", stopbits=1)
		time.sleep(0.1)
	except:
		print("could not open serial"); exit()
	

	#### uploading ####
	if(args.upload):
		name=args.file.split("/")[-1].split("\\")[-1]   # extract name from file path (Linux and Windows compatible)
		content=f.read()                                # read content to string
		ser.reset_input_buffer()                        # delete old prompt sign
		sendLine("file.open(\""+name+"\", \"w\")")      # open file on ESP
		waitForPrompt()
		while(len(content)>0):
			code=",".join(map(str,map(ord,list(content[:chunksize]))))
			content=content[chunksize:]
			sendLine("file.write(string.char("+code+"))")
			waitForPrompt()
		sendLine("file.flush();file.close()")           # flush and close file on ESP
		waitForPrompt()

	#close everything
	sendLine("uart.setup( 0, 9600, 8, 0, 1, 1)")
	ser.close()
	f.close()