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
import schedule

running =False
choice=0
spectrometerFlag=0
ftpConnection=0
uploadTime=0
uploadInterval=60
spec=0
durationValue=10
integrationTime=100



def placeFiles(ftp, path):
    for name in os.listdir(path):
        localpath = os.path.join(path, name)
        print(localpath)
        if os.path.isfile(localpath):
            print("STOR", name, localpath)
            ftp.storbinary('STOR ' + os.path.basename(name), open(localpath,'rb'))
        elif os.path.isdir(localpath):
            print("MKD", name)

            try:
                ftp.mkd(name)

            # ignore "directory already exists"
            except error_perm as e:
                if not e.args[0].startswith('550'):
                    raise

            print("CWD", name)
            ftp.cwd(name)
            placeFiles(ftp, localpath)
            print("CWD", "..")
            ftp.cwd("..")


def spectrometerCheck():
	if(spectrometerFlag==0):
		spectrometerConnect()
	else:
		print("spectrometer already Connected")
	
def spectrometerConnect():
        global spec
        devices=sb.list_devices()
        print(devices)
        global spectrometerFlag
        print("this is inside spectrometer connect")
        if(len(devices)>0):
                spectrometerFlag=1
                print("Something is connected")
#                messagebox.showinfo("Detected", "Spectrometer detected :"+str(devices[0]))
                spec = sb.Spectrometer(devices[0])
                spec.integration_time_micros(integrationTime)
                log("Spectrometer "+str(devices[0])+" is now connected.");
                return 1
        else:
#                messagebox.showinfo("Error", "No spectrometer detected")
                print("no spectrometer detected")
                log("No spectrometer could be connected");
                spectrometerFlag=0
                return 0
    

def spectrometerSetup():
    print("spectrum setup here");
    print(str(time.localtime().tm_hour) +':'+ str(time.localtime().tm_min))    
    global uploadInterval
    global spec
    global durationValue
    global integrationTime
    f=open('config.txt',"r");
    conf = [row[0] for row in csv.reader(f,delimiter='\t')]
    f.close()
    log("inside spectrum setup")
    print(conf)
    if(integrationTime!=int(conf[2],10)):
    	integrationTime=int(conf[2],10)
    	spectrometerConnect();
    sessionBegin=timeToMinutes(conf[4])
    sessionEnd=timeToMinutes(conf[5])
    now=time.localtime().tm_hour * 60 + time.localtime().tm_min
    if( now>=sessionBegin and now<sessionEnd):
    	startscan()
    schedule.clear('startStop')
    schedule.every().day.at(conf[4]).do(startscan).tag('startStop');
    schedule.every().day.at(conf[5]).do(stop).tag('startStop');
    if(uploadInterval!=int(conf[6],10)):
    	uploadInterval=int(conf[6],10)
    	schedule.every(uploadInterval).minutes.do(uploadFtp).tag('upload');
    	print("upload interval did change")
    	log("upload interval updated to "+str(uploadInterval))
    else:
    	print("no change in upload interval so moving on"); 
     
    print("every start at "+conf[4]+"stop at"+conf[5]);
    durationValue=conf[3]
#    devices=sb.list_devices()
    
    


def timeToMinutes(time):
    a=int(time[0:2],10)
    b=int(time[3:5],10)
    return  a*60+b

def stop():
    global running
    running = False
    print(" program stopped")
    log("Scanning is stopped")
    
def startscan():
    global running
    running = True
    print("started")
    log("Scanning is started")
    
def scanning(durationValue,spec,currentTime,ftpVar,ftpUserVar,ftpPassVar):
    global running 
    global ftpConnection
    global uploadTime
    global uploadInterval
    print("just before get data");
    print(durationValue)
    x=getdata(durationValue,spec)
    y=x[1]
    x=x[0]
    date=str(datetime.datetime.now().date())
    dateFolder=date
    time=str(datetime.datetime.now().time())
    timeName=time[0:2]+time[3:5]+time[6:7]
    os.system('mkdir -p saveFiles/'+date)
    time=time[0:7]
    dateFile='saveFiles/'+date+'/'+timeName+'_spectrum.txt'
    f=open(dateFile,"a");
#   f.write(time+'\t')
    print('folder and file created')
    for i in range(21):
        f.write("* \n")
    f.write("*"+time+"\n")
    for i in range(len(x)):
        f.write(str(y[i])+'\t'+str(x[i])+'\n')
     
    f.close()


def log(logMessage):
    date=str(datetime.datetime.now().date())
    dateFolder=date
    time=str(datetime.datetime.now().time())
    timeName=time[0:2]+time[3:5]+time[6:7]
    os.system('mkdir -p saveFiles')
    time=time[0:7]
    dateFile='saveFiles/log.txt'
    f=open(dateFile,"a");
    f.write(time+':\t'+logMessage);
    f.write("\n")
    f.close()
	


def uploadLog():
    print("uloading log")
    if (ftpConnection==1):
        log("Uploading log")
        date=str(datetime.datetime.now().date())
        session = ftplib.FTP(ftpVar,ftpUserVar,ftpPassVar)
        filenameCV = "saveFiles/log.txt"
        name="log.txt"
        print("STOR", name, filenameCV)
        session.storbinary('STOR ' + os.path.basename(name), open(filenameCV,'rb'))
        session.quit()



def uploadFtp():
    print("uloading")
    if (ftpConnection==1):
    	log("Uploading files")
    	date=str(datetime.datetime.now().date()) 	
    	session = ftplib.FTP(ftpVar,ftpUserVar,ftpPassVar)
    	filenameCV = "saveFiles/"
    	filenameCV=filenameCV+date
    	print(filenameCV)
    	try:
    		session.mkd(date)
    	except:
    		print("cannot maake")
    	session.cwd(date)    	
    	placeFiles(session, filenameCV)
    	session.quit()
    	
        
   

def getdata(durationValue,spec):
    #get data here from spectrometer i guess
    print( "also wait for ")
    print(durationValue );
    start=time.time()
    c=0;
    x=[1,2,3,4,5]
    y=[1,2,3,4,5]
 
    devices=[]
    global spectrometerFlag

    if(spectrometerFlag==1):
            try:
            	x=spec.intensities()
            	z=spec.wavelengths()
            except:
            	log("Spectrometer Error. ( might me disconnected")
            	print("spectrometer Error")
            	return [x,y]
            	spectrometerConnect()
            while((time.time()-start)<int(durationValue,10)*60):
                    try:
                    	y=spec.intensities()
                    	c=c+1
                    	for i in range(0,len(y)):
                    	        x[i]=x[i]+y[i]

                    except:
                    	log("Spectrometer Error. ( might me disconnected")
                    	print("spectrometer Error")
                    	spectrometerConnect()
                    	return [x,y]
            y=z
    else:
            c=c+1;
            y=x
    for j in range(0,len(x)):
            x[j]=x[j]/c;

    return [x,y]


def ftpConnect():
	global ftpConnection
	print("checking connection to ftp")
	print(str(time.localtime().tm_hour) +':'+ str(time.localtime().tm_min))

	try:
		ftp = ftplib.FTP(ftpVar,ftpUserVar,ftpPassVar)
		print("ftp connection is here")
		ftp.cwd('/conf/')
		print("after cwd")
		ftp.quit()
		ftpConnection=1
		print("connected")
		log("connected to ftp and the config file donwloaded")
#		messagebox.showinfo('Connected','connected to the ftp:'+ftpVar);
	except:
#		messagebox.showinfo('Failed to connect','Failed to connect to ftp:'+ftpVar);
		print(" could not be  connected")
		log("failed to connect to the ftp")
			
	if ftpConnection:
		ftp = ftplib.FTP(ftpVar,ftpUserVar,ftpPassVar)
		ftp.cwd('/conf/')
		print("this is after cwd")
		filename='config.txt'
		localfile=open(filename,'wb')
		ftp.retrbinary('RETR ' + filename,localfile.write, 1024)
		print("this is after writing to file")
		ftp.quit()
		localfile.close()
	spectrometerSetup()
	
"""
root = Tk()
root.attributes('-zoomed', True)
root.title('Optind Nephelometer Interface')
frame=Frame(root);
frame.grid(row=0);

font_value='Times 14'



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

spectrometerButton = Button(frame, text="Connect spectrometer", command= spectrometerConnect)
spectrometerButton.grid(row=0,column=1, pady=10)

ftpButton = Button(frame, text="Connect ftp ", command= ftpConnect)
ftpButton.grid(row=0,column=4, pady=10)

os.system("matchbox-keyboard &")
uploadText=tk.StringVar()

stopButton = Button(frame, text=" Stop ", command=stop);
stopButton.grid(row=3,column=0);
startButton = Button(frame, text=" Start ", command=startscan);
startButton.grid(row=3,column=1);
button = Button(frame, text="QUIT", command=quit)
button.grid(row=3,column=2)
uploadLabel=Label(frame, textvariable=uploadText)
uploadLabel.grid(row=5,column=4, pady=6)
w0=Label(frame, text="Reading in process", font='Helvetica 14 bold')
w0.grid(row=2, pady=6)
#root.update()

ftpVar=ftp.get()
ftpUserVar=ftpUser.get()
ftpPassVar=ftpPass.get()
"""


f=open('configuration.txt',"r");
config = [row[0] for row in csv.reader(f,delimiter='\t')]
f.close()

ftpVar=config[1]
ftpUserVar=config[2]
ftpPassVar=config[3]
waitTime=10
count=0
spectrometerConnect()

ftpConnect()
time.sleep(20)
print("going into the while loop")
schedule.every(3).minutes.do(ftpConnect);
schedule.every(2).minutes.do(spectrometerCheck);
log("Program Started")
schedule.every(2).minutes.do(spectrometerCheck);
schedule.every(3).minutes.do(uploadLog);
while(1):
	schedule.run_pending()
	currentTime=time.localtime().tm_min + time.localtime().tm_hour * 60

	if running:
		print(" it is looping though")
		print(currentTime)
		#uploadText.set('Time from last upload:'+str(currentTime-uploadTime))	
		scanning(durationValue,spec,currentTime,ftpVar,ftpUserVar,ftpPassVar)  # After 1 second, call scanning
#		time.sleep(waitTime)
#		root.update()

