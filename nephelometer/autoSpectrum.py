#!/usr/bin/python3
import RPi.GPIO as GPIO
from tkinter import *
import datetime
import time
from tkinter.ttk import *
import tkinter as tk
import numpy as np
import time as time
from struct import  *
import seabreeze.spectrometers as sb
from tkinter import messagebox
import csv
import os
import ftplib

running =True
choice=0
spectrometerFlag=0
ftpConnection=0
uploadTime=0
uploadInterval=60
def spectrometerConnect():
        devices=sb.list_devices()
        print(devices)
        global spectrometerFlag
        if(len(devices)>0):
                spectrometerFlag=1
                print("Something is connected")
                messagebox.showinfo("Detected", "Spectrometer detected :"+str(devices[0]))
                return 1
        else:
                messagebox.showinfo("Error", "No spectrometer detected")
                spectrometerFlag=0
                return 0

def start():
    os.system("killall matchbox-keyboard");
    global uploadInterval
    f=open('config.txt',"r");
    conf = [row[0] for row in csv.reader(f,delimiter='\t')]
    f.close()
    sessionBegin=timeToMinutes(conf[4])
    sessionEnd=timeToMinutes(conf[5])
    print(sessionBegin)
    print(sessionEnd)
    
    uploadInterval=int(conf[6],10)
    print("spectrometer flag  is");
    print(spectrometerFlag)
    durationValue=conf[3]
    devices=sb.list_devices()
    frame.grid_forget()
    if(len(devices)>0):
        spec=sb.Spectrometer(devices[0])
        spec.integration_time_micros(int(conf[2],10))
    else:
        spec=0
    uploadText=tk.StringVar()
    frame3=Frame(root);
    frame3.grid(row=0);
    stopButton = Button(frame3, text=" Stop ", command=stop);
    stopButton.grid(row=1,column=0);
    startButton = Button(frame3, text=" Start ", command=startscan);
    startButton.grid(row=1,column=1);
    button = Button(frame3, text="QUIT", command=quit)
    button.grid(row=1,column=2)
    uploadLabel=Label(frame3, textvariable=uploadText)
    uploadLabel.grid(row=0,column=4, pady=6)
    w0=Label(frame3, text="Reading in process", font='Helvetica 14 bold')
    w0.grid(row=0, pady=6)
    root.update()
    ftpVar=ftp.get()
    ftpUserVar=ftpUser.get()
    ftpPassVar=ftpPass.get()
    waitTime=10
    print("going into the while loop")
    count=0
    
    while(1):
        currentTime=time.localtime().tm_min + time.localtime().tm_hour * 60
        print(currentTime)
        if(currentTime>= sessionBegin and currentTime<=sessionEnd):
            print(" it is looping though")
            print(currentTime)
            uploadText.set('Time from last upload:'+str(currentTime-uploadTime))
            print(uploadText.get())
            scanning(durationValue,spec,currentTime,ftpVar,ftpUserVar,ftpPassVar)  # After 1 second, call scanning
            time.sleep(waitTime)
        else:
            time.sleep(20)
        root.update()
        
def timeToMinutes(time):
    a=int(time[0:2],10)
    b=int(time[3:5],10)
    return  a*60+b
def stop():
    global running
    running = False

    
def startscan():
    global running
    running = True
    
def scanning(durationValue,spec,currentTime,ftpVar,ftpUserVar,ftpPassVar):
    global running 
    global ftpConnection
    global uploadTime
    global uploadInterval
    print("just before get data");
    print(durationValue)
    x=getdata(durationValue,spec)
    print("this is right after get data")
    print(x)
    y=x[1]
    x=x[0]
    date=str(datetime.datetime.now().date())
    dateFolder=date
    time=str(datetime.datetime.now().time())
    os.system('mkdir -p saveFiles/'+date)
    time=time[0:7]
    dateFile='saveFiles/'+date+'/'+time+'_spectrum.txt'
    f=open(dateFile,"a");
#    f.write(time+'\t')
    print('folder and file created')
    for i in range(22):
        f.write("* \n")
    for i in range(len(x)):
        f.write(str(y[i])+'\t'+str(x[i])+'\n')
     
    f.close()
    print(" reached till upload verification")
    if (currentTime-uploadTime>=uploadInterval  and ftpConnection==1):
    	session = ftplib.FTP(ftpVar,ftpUserVar,ftpPassVar)
    	print("uploading  now")
    	file = open(dateFile,'rb')                  # file to send
    	try:
    		session.storbinary('STOR '+dateFile, file)     # send the file
    	except IOERROR:
    		print(sys.exe_info()[0])
    	file.close()
    	session.quit()
    	uploadTime=currentTime
    print(x)
        
   

def getdata(durationValue,spec):
    #get data here from spectrometer i guess
    print( "also wait for ")
    print(durationValue );
    start=time.time()
    c=0;
    x=[1,2,3,4,5]
    devices=[]
    global spectrometerFlag
    
    if(spectrometerFlag==1):
            x=spec.intensities()
            while((time.time()-start)<int(durationValue,10)*60):
                    y=spec.intensities()
                    c=c+1
                    for i in range(0,len(y)):
                            x[i]=x[i]+y[i]
            y=spec.wavelengths()
    else:
            c=c+1;
            y=x
    for j in range(0,len(x)):
            x[j]=x[j]/c;

    return [x,y]


def ftpConnect():
	global ftpConnection
	ftpVar=ftp.get()
	ftpUserVar=ftpUser.get()
	ftpPassVar=ftpPass.get()
	try:
		ftp = ftplib.FTP(ftpVar,ftpUserVar,ftpPassVar)
		ftp.cwd('/conf/')
		filename='config.txt'
		localfile=open(filename,'wb')
		ftp.retrbinary('RETR ' + filename,localfile.write, 1024)
		ftp.quit()
		localfile.close()
		ftpConnection=1
		
		messagebox.showinfo('Connected','connected to the ftp:'+ftpVar);
	except:
		messagebox.showinfo('Failed to connect','Failed to connect to ftp:'+ftpVar);
	
	session.quit()
	return session



root = Tk()
root.attributes('-zoomed', True)
root.title('Optind Nephelometer Interface')
frame=Frame(root);
frame.grid(row=0);

font_value='Times 14'

spectrometerConnect()

w2=Label(frame, text="FTP url",font=font_value).grid(row=1, column=3)
ftp = Entry(frame)
ftp.grid(row=1, column=4)
ftp.insert(END, "optind.in")


w3=Label(frame, text="FTP username",font=font_value).grid(row=2, column=3)
ftpUser = Entry(frame)
ftpUser.grid(row=2, column=4)
ftpUser.insert(END, "neph")


w3=Label(frame, text="FTP password",font=font_value).grid(row=3, column=3)
ftpPass = Entry(frame)
ftpPass.grid(row=3, column=4)
ftpPass.insert(END, "optind123**")

button = Button(frame, text="QUIT", command=quit)
button.grid(row=0,column=3, pady=10)

startButton = Button(frame, text="Start program", command=start)
startButton.grid(row=0,column=2, pady=10)

spectrometerButton = Button(frame, text="Connect spectrometer", command= spectrometerConnect)
spectrometerButton.grid(row=0,column=1, pady=10)

ftpButton = Button(frame, text="Connect ftp ", command= ftpConnect)
ftpButton.grid(row=0,column=4, pady=10)

os.system("matchbox-keyboard &")

tk.mainloop()

