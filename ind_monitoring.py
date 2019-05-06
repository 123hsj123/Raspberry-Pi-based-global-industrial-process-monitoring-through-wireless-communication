

import RPi.GPIO as GPIO
import time
from time import sleep
from array import array

import smtplib

import serial

import pygame

import spidev
import time
import os

GPIO.setmode(GPIO.BOARD)
GPIO.setwarnings(False)

usbport = '/dev/serial0'
ser = serial.Serial(usbport, 9600)

spi = spidev.SpiDev()
spi.open(0,0)
spi.max_speed_hz=1000000

##sys= systemstarts
Relay_bulb = 36
MOTOR1 = 38
MOTOR2 = 40
IR_Obstacle = 16
Coolant_Level = 37

GPIO.setup(Relay_bulb, GPIO.OUT)
GPIO.setup(MOTOR1, GPIO.OUT)
GPIO.setup(MOTOR2, GPIO.OUT)
GPIO.setup(IR_Obstacle, GPIO.IN)
GPIO.setup(Coolant_Level, GPIO.OUT)

GPIO.output(MOTOR1,GPIO.LOW)
GPIO.output(MOTOR2,GPIO.LOW)
GPIO.output(Coolant_Level,GPIO.LOW)
GPIO.output(Relay_bulb, GPIO.LOW)

UART_Rx_Str = ""
count = 0

Sample_Count = 0
Batch_Count = 0
Total_Count = 0

ser.write("AT\r")
print "GSM INITIALIZED"
sleep( 2 )
ser.flushInput()

ser.write("AT+CNMI=2,2,0,0,0\r")
print "GSM RX ENABLED"
sleep( 2 )
ser.flushInput()

def mail():
    smtpUser = 'batchb006@gmail.com'
    smtpPass = 'b6123456789'

    toAdd = 'sanjanarajanahalli97@gmail.com'
    fromAdd = smtpUser

    subject = 'industrial monitoring system'
    header = 'To: ' + toAdd + '\n' + 'From: ' + fromAdd + '\n' + 'Subject: ' + subject
##    body = 'temp exeeds'

    print header + '\n' + body

    s = smtplib.SMTP('smtp.gmail.com',587)

    s.ehlo()
    s.starttls()
    s.ehlo()

    s.login(smtpUser, smtpPass)
    s.sendmail(fromAdd, toAdd, header + '\n\n' + body)

    s.quit()
    
def ReadChannel(channel):
    adc = spi.xfer2([1,(8+channel)<<4,0])
    data = ((adc[1]&3) << 8) + adc[2]
    return data

def ConvertVolts(data,places):
    volts = (data * 3.3) / float(1023)
    volts = round(volts,places)
    volts = (int)(volts * 100)
    return volts
 
def GSM_Send_SMS( Mobile, SMS ):
    ser.write( "AT+CMGS=\"" )
    ser.write( Mobile )
    ser.write( "\"\r" )
    sleep( 2 )
    ser.write( SMS )
    ser.write( "\x1A" )
    sleep( 4 )

def SMS_Rx_Func( ):
    Rx_Mob_Num = ""
    UART_Rx_Str = ""
    while True:
        data = ser.read()
        if( data == "\"" ):
            data = ser.read()
            if( data == "," ):
                for i in range(0,27):
                    data = ser.read()

                while True:
                    data = ser.read()
                    if(data == "@"):
                        print "NUM:" + Rx_Mob_Num
                        print "SMS:" + UART_Rx_Str

                        if( (UART_Rx_Str[0] == 'C') and (UART_Rx_Str[1] == '1') ):
                            print "CONVEYOR STARTS"
                            GPIO.output(MOTOR1, GPIO.HIGH)
                            GPIO.output(MOTOR2, GPIO.LOW)
                            sleep(2)


                        elif( (UART_Rx_Str[0] == 'C') and (UART_Rx_Str[1] == '0') ):
                            print "CONVEYOR STOPS"
                            GPIO.output(MOTOR1, GPIO.LOW)
                            GPIO.output(MOTOR2, GPIO.LOW)
                            sleep(10)

                        elif( (UART_Rx_Str[0] == 'M') and (UART_Rx_Str[1] == '1') ):
                            GPIO.output(Relay_bulb, GPIO.HIGH)
                            print "MACHINE ON"
                            sleep(2)
                            

                        elif( (UART_Rx_Str[0] == 'M') and (UART_Rx_Str[1] == '0') ):
                            GPIO.output(Relay_bulb, GPIO.LOW)
                            print "MACHINE OFF"
                            sleep(2)
                            
                        
                        Rx_Mob_Num = ""
                        UART_Rx_Str = ""
                        break
       
                    else:
                        UART_Rx_Str = UART_Rx_Str + data
        else:
            Rx_Mob_Num = Rx_Mob_Num + data


        if(data == "@"):
            for i in range(0,2):
                data = ser.read()
            break


GSM_Send_SMS( "8892204856", "SYSTEM START" )
sleep(2)
ser.flushInput()
print "TEST SMS SENT"


GPIO.output(Relay_bulb, GPIO.HIGH)
print "MACHINE ON"
sleep(2)
GPIO.output(Relay_bulb, GPIO.LOW)
print "MACHINE OFF"
sleep(1)

print "CONVEYOR STARTS"
GPIO.output(MOTOR1, GPIO.HIGH)
GPIO.output(MOTOR2, GPIO.LOW)
sleep(5)
print "CONVEYOR STOPS"
GPIO.output(MOTOR1, GPIO.LOW)
GPIO.output(MOTOR2, GPIO.LOW)

GPIO.output(Coolant_Level,GPIO.HIGH)
sleep(9)
GPIO.output(Coolant_Level,GPIO.LOW)
sleep(1)

pygame.mixer.init()
pygame.mixer.music.load('project_start.mp3')
pygame.mixer.music.play()
sleep(10)
pygame.mixer.music.stop()

Sample_Count = 0
Batch_Count = 0
Total_Count = 0


##while True:
##        while True:
##                data = ser.read()
##                if(data == "\r"):
##                    print "Received from LAPTOP:" + line
##                    line = ""
##                    break
##                else:
##                    line = line + data

 
while True:
    print "------------------------------------"
    print"START COUNTING"
    
    while True:            
        temp_level = ReadChannel(0)
        temp_volts = ConvertVolts(temp_level,2)
        print temp_volts
        sleep(1)

        Overload_level = ReadChannel(1)
        Overload_volts = ConvertVolts(Overload_level,2)
        print Overload_volts
        sleep(1)

        if (Overload_volts<10):
            print "NORMAL CONDITION"
            sleep(1)

        elif ((Overload_volts>=10) and (Overload_volts<=17)):
            print "LOAD HAS INCREASED"
            sleep(1)
            pygame.mixer.init()
            pygame.mixer.music.load('load_increased.mp3')
            pygame.mixer.music.play()
            sleep(10)
            pygame.mixer.music.stop()

        elif (Overload_volts>17):
            print "OVERLOAD DETECTED"
            sleep(1)
            pygame.mixer.init()
            pygame.mixer.music.load('overload_detected.mp3')
            pygame.mixer.music.play()
            sleep(10)
            pygame.mixer.music.stop()

            body = 'OVERLOAD DETECTED'
            mail()
            
            GSM_Send_SMS( "8892204856", "OVERLOAD DETECTED" )
            sleep(6)
            print "SMS SENT"
            ser.flushInput()

            GPIO.output(Relay_bulb, GPIO.LOW)
            print "MACHINE OFF"
            sleep(1)

            GPIO.output(MOTOR1, GPIO.LOW)
            GPIO.output(MOTOR2, GPIO.LOW)
            print "CONVEYOR STOPS"
            sleep(1)

            GPIO.output(Coolant_Level,GPIO.HIGH)
            print "COOLANT IS ON"
            sleep(1)
            break
        
        if ((temp_volts>40) and (temp_volts<60)):
            print "TEMPERATURE HAS INCREASED"
            sleep(1)
            pygame.mixer.init()
            pygame.mixer.music.load('temp_increased.mp3')
            pygame.mixer.music.play()
            sleep(10)
            pygame.mixer.music.stop()
            
        elif(temp_volts>=60):
            print "HIGH TEMPERATURE"
            sleep(1)
            pygame.mixer.init()
            pygame.mixer.music.load('high_temp.mp3')
            pygame.mixer.music.play()
            sleep(10)
            pygame.mixer.music.stop()
            body = 'HIGH TEMPERATURE'
            mail()
            
            GSM_Send_SMS( "8892204856", "HIGH TEMPERATURE" )
            sleep(6)
            print "SMS SENT"
            ser.flushInput()

            GPIO.output(Relay_bulb, GPIO.LOW)
            print "MACHINE OFF"
            sleep(1)

            GPIO.output(MOTOR1, GPIO.LOW)
            GPIO.output(MOTOR2, GPIO.LOW)
            print "CONVEYOR STOPS"
            sleep(1)

            GPIO.output(Coolant_Level,GPIO.HIGH)
            print "COOLANT IS ON"
            sleep(1)
            break
        else:                
    ##              print "CONVEYOR STARTS"
            GPIO.output(MOTOR1, GPIO.HIGH)
            GPIO.output(MOTOR2, GPIO.LOW)
            
            GPIO.output(Relay_bulb, GPIO.HIGH)
##            print "MACHINE ON"
##            sleep(2)
            
            if(GPIO.input(IR_Obstacle) == False):
                Sample_Count = Sample_Count + 1
                Total_Count = Total_Count + 1
                    
                print 'SAMPLE COUNT = ' + str(Sample_Count)
                print 'BATCH COUNT = ' + str(Batch_Count)
                print 'TOTAL COUNT = ' + str(Total_Count)
                sleep(1)
                if( Sample_Count >= 5 ):
                    Sample_Count = 0;
                    Batch_Count = Batch_Count + 1

                    Send_Data_SMS = 'S' +  str(Sample_Count) + 'B' + str(Batch_Count) + 'T' + str(Total_Count)
                    GSM_Send_SMS( "8892204856", Send_Data_SMS )
                    sleep(6)
                    print "SMS SENT"
                    ser.flushInput()
                    break;
       
    print "waiting for command"
    sleep(3)
    ser.flushInput()

    data = ser.read()
    for i in range(0,8):
            data = ser.read()

    if( data == "\"" ):
            data = ser.read()
            if( data == "+" ):
                    SMS_Rx_Func( )


   
    
