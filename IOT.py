import RPi.GPIO as GPIO
import time
import spidev
import signal
import sys
import MySQLdb
import Adafruit_DHT
from numpy import interp
from time import sleep
import datetime
from datetime import date


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
DHT_SENSOR = Adafruit_DHT.DHT22
DHT_PIN = 25                                   #DHT_22_GPIO_PIN
humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
GPIO.setup(21, GPIO.OUT)                       #Solenoid Valve-1
GPIO.setup(16, GPIO.OUT)                       #Solenoid Valve-3
GPIO.setup(20, GPIO.OUT)                       #Solenoid Valve-4
GPIO.setup(23, GPIO.OUT)                       #UV led
GPIO.setup(24, GPIO.OUT)                       #Red and Blue Led
GPIO.setup(26,GPIO.IN)
GPIO.setup(15,GPIO.OUT)                        #Solenoid Valve-2
GPIO.setup(13,GPIO.IN)
GPIO.setup(15,GPIO.OUT)                        #Solenoid Valve-2
GPIO.setup(22,GPIO.IN)
GPIO.setup(27,GPIO.OUT)                	       #Sump Motor
GPIO.setup(18,GPIO.IN)
GPIO.setup(3,GPIO.OUT)                         #bubbler pin
GPIO.setup(14, GPIO.OUT)                       #E Fan 
GPIO.setup(19,GPIO.IN)     		       #bucket float sensor


spi = spidev.SpiDev()
spi.open(0,0)
GPIO.output(16,0)
GPIO.output(3,1)
GPIO.output(27,0)
GPIO.output(15,0)
GPIO.output(20,0)
GPIO.output(21,0)
GPIO.output(23,1)
GPIO.output(24,1)

var = datetime.datetime.now().strftime("%H:%M")
def analogInput(channel):
	spi.max_speed_hz = 1350000
	adc = spi.xfer2([1,(8+channel)<<4, 0])
	data = ((adc[1]&3) << 8) + adc[2]
	return data

def close(signal, frame):
	GPIO.cleanup()
	sys.exit(0)
	signal.signal(signal.SIGINT, close)


while True:
	var = datetime.datetime.now().strftime("%H:%M")

# Overhead tank float sensor  and sump motor
	if GPIO.input(22) == 0:
		if GPIO.input(18) == 0:
			GPIO.output(27,True)

	if GPIO.input(22) == 1:
		if GPIO.input(18) == 1:
                	GPIO.output(27,False)
	if GPIO.input(19) == 0:
		GPIO.output(27,False)
#bubbler float sensor and  bubbler valve 
	if GPIO.input(26) == 0:
		if GPIO.input(13) == 0:
	                GPIO.output(15,True)
        if GPIO.input(26) == 1:
		if GPIO.input(13) == 1:
                	GPIO.output(15,False)

        if var >= "06:30":
		GPIO.output(23,False)
		GPIO.output(24,False)

		if var >= "17:00":
			GPIO.output(23,True)
			GPIO.output(24,True)

	o = analogInput(0)
	o_map = interp(o, [0, 1023], [100, 0])
	o_res = int(o_map)

	o1 = analogInput(1)
	o_map1 = interp(o1, [0, 1023], [100, 0])
	o_res1 = int(o_map1)

	o2 = analogInput(7)
	o_map2 = interp(o2, [0, 1023], [100, 0])
	o_res2 = int(o_map2)

        o3 = analogInput(5)
        o_map3 = interp(o3, [0, 1023], [0, 100])
        o_res3 = int(o_map3)

	if(o_res>=80):
		GPIO.output(21,GPIO.HIGH)
       	if(o_res1>=80):
		GPIO.output(20,GPIO.HIGH)
        if(o_res2>=80):
		GPIO.output(16,GPIO.HIGH)
        if(o_res<=80):
		GPIO.output(21,GPIO.LOW)

       	if(o_res1<=80):
		GPIO.output(20,GPIO.LOW)

	if(o_res2<=80):
                GPIO.output(16,GPIO.LOW)

	humidity, temperature = Adafruit_DHT.read(DHT_SENSOR, DHT_PIN)
	if humidity is not None and temperature is not None:
    		print("Temp={0:0.2f}C Humidity={1:0.0f}%".format(temperature, humidity))
		time.sleep(5)
	if humidity is None and temperature is None:
		#time.sleep(5)
		print "Sensor failure"
	if humidity > 75.0:
		GPIO.output(3,True)
	if humidity < 75.0:
		GPIO.output(3,False)
	if temperature > 26.0:
		GPIO.output(14,True)
	if temperature < 26.0:
                GPIO.output(14,False)


		#Establishing Connection to the Database
	dbConn = MySQLdb.connect("localhost","ADMIN","ABC","GREENHOUSE") or die ("could not connect to database")
	with dbConn:
        	#open a cursor to the database

        	cursor = dbConn.cursor()
		now=datetime.datetime.now()
    		today=now.strftime('%Y-%m-%d %H:%M:%S')
		Sl_No=0
		cursor.execute("INSERT INTO Current_Data VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (Sl_No, today, temperature, humidity, o_res, o_res1, o_res2, o_res3))

	dbConn.commit() #commit the insert
	cursor.close()  #close the cursor
