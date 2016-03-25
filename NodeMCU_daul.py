#! /usr/bin/env python2.7
import argparse
import serial
import time

chunksize=48				# maximum chunk size possible

def getFileNameFrompath(path):
	return path.split("/")[-1].split("\\")[-1]

def sendLine(ser, outstring):
	ser.write(outstring + "\r\n")	# send string with carriage return and linefeed at the end

def waitForPrompt(ser):
	line=""
	while(line[-2:] != "> "):		# wait until returning line is promt symbol of Lua shell
		line += ser.read()

def changeBaud(ser, baud):
	sendLine(ser, "uart.setup( 0, " + str(baud) + ", 8, 0, 1, 1)")		# make ESP change to requested baud rate
	ser.close()								# close old connection
	ser.baudrate=baud							# change baud rate
	ser.open()								# reopen serial connection with requested baud rate
	time.sleep(0.1)								# wait a little

def getArguments():
	parser = argparse.ArgumentParser(description='Down and upload files from and to an ESP8266 running NodeMCU. Createt by MarBle.')
	parser.add_argument("-f", "--file"    , type=str           , help='filepath to read from or write to')
	parser.add_argument("-d", "--download", action="store_true", help='downloads file from the ESP to your computer')
	parser.add_argument("-u", "--upload"  , action="store_true", help='uploads file from your computer to the ESP')
	parser.add_argument("-l", "--list"    , action="store_true", help='list the files stored on the ESP')
	parser.add_argument("-r", "--remove"  , action="store_true", help='remove file from the ESP')
	parser.add_argument("-v", "--verbose" , action="store_true", help='print the serial communication to the terminal')
	parser.add_argument("-b", "--baud"    , type=int           , default = 9600	, help='change the baud rate')
	parser.add_argument("-s", "--serial"  , type=str           , help='path to serial device')
	return parser.parse_args()

def main():
	
	args = getArguments()							# get Command Line Arguments

	#only allow either up or downloading
	if (args.upload + args.download + args.list + args.remove) != 1:
		print("Don't know what to do. (Set either -u or -d)")
		exit()


	#### asserting ####
	try:    f=open(args.file, "rw")
	except: print("Can't open file."); exit()

	try:
		ser = serial.Serial(args.serial, 9600, 8, "N", 1)		# open connection to ESP with 9600 baud
		time.sleep(0.1)							# wait a little
		changeBaud(ser, args.baud)					# open new serial connection with requested baud rate
	except: print("could not open serial"); exit()


	#### uploading ####
	if(args.upload):
		name=getFileNameFrompath(args.file)				# extract name from file path (Linux and Windows compatible)
		content=f.read()						# read content to string
		ser.reset_input_buffer()					# delete old prompt sign
		sendLine(ser, "file.open(\""+name+"\", \"w\")")			# open file on ESP
		waitForPrompt(ser)
		while(len(content)>0):						# repeat until all of the string is been sent
			code=",".join(map(str,map(ord,list(content[:chunksize])))) # convert every char into string of ordinal
			sendLine(ser, "file.write(string.char("+code+"))")	# make ESP write code to file
			content=content[chunksize:]				# cut off remaining content string
			waitForPrompt(ser)
		sendLine(ser, "file.flush();file.close()")			# flush and close file on ESP
		waitForPrompt(ser)

	#close everything
	changeBaud(ser, 9600)							# reset UART speed
	sendLine(ser, "")
	waitForPrompt(ser)
	ser.close()
	f.close()


if __name__ == "__main__":
	main()
