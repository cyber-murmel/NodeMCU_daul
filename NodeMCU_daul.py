#! /usr/bin/env python2.7
import argparse
import serial
import time

def sendLine(outstring):
	ser.write(outstring+"\r\n")
def wfp():							# wait for prompt
	line=ser.read()
	while(line[-2:]!="> "):
		#print("\""+line+"\"")
		#print("\""+line[-2:]+"\"")
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

	try:	# to open file
		f=open(args.file, "rw")
		name=args.file.split("/")[-1].split("\\")[-1]	# extract name from file path (Linux and Windows compatible)
		print(name)
		content=f.read()								# read content to string
		length=len(content)								# get file length
	except:
		print("Can't open file."); exit()

	try:	# to open serial
		ser = serial.Serial(port=args.serial, baudrate=9600, bytesize=8, parity="N", stopbits=1)
	except:
		print("could not open serial"); exit()
	
	
	if(args.upload):
		sendLine("file.open(\""+name+"\", \"w\")")		# open file on ESP
		wfp()
		sendLine("foo=\"\"")
		wfp()
		sendLine("f = function(val) foo=foo..string.char(val) end")
		wfp()
		for c in content:
			sendLine("f("+str(ord(c))+")")
			wfp()
		sendLine("file.write(foo)")
		wfp()
		sendLine("file.flush();file.close()")			# flush and close file on ESP
		wfp()
		#print("file.flush();file.close()")
	#close everything
	sendLine("uart.setup( 0, 9600, 8, 0, 1, 1)")
	f.close()