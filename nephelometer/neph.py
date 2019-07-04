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
    global choice
    global uploadInterval
    uploadInterval=int(uploadInt.get())
    os.system("killall matchbox-keyboard");
    print("starting program");
    frame.grid_forget()
    choice=modeChoices.index(mode.get())
    if modeChoices.index(mode.get()):
        manual();
    else:
        automatic();

def manual():
    print("spectrometer flag  is");
    print(spectrometerFlag)
    durationValue=duration.get()
    print("manual mode is started")
    calibrateValue=calibration.get()
    var=tk.IntVar()
    var2=tk.IntVar()
    frame2=Frame(root,width=450,height=50);
    frame2.grid(row=0);
    devices=sb.list_devices()
    
    if(len(devices)>0):
        spec=sb.Spectrometer(devices[0])
        spec.integration_time_micros(int(integrationTime.get(),10))
    else:
        spec=0

    if calibrateValue:

        nitrogenButton = Button(frame2, text=" Begin Nitrogen Calibration", command=lambda:var.set(1));
        nitrogenButton.grid(row=1);
        w0=Label(frame2, text="Waiting for Nitrogen gas to be connected and ready ", font='Helvetica 14 bold')
        w0.grid(row=0, pady=6)

        print("waiting for Nitrogen gas to be connected and ready");
        nitrogenButton.wait_variable(var)
        print("Reading Values")
        w0.grid_forget()
        w0=Label(frame2, text="Getting Values for Nitrogen Please wait... ", font='Helvetica 14 bold')
        w0.grid(row=0, pady=6)
        nitrogenData=getdata(durationValue,spec);
        print(nitrogenData)

        w0.grid_forget();
        nitrogenButton.destroy();

        secondButton = Button(frame2, text=" Begin Second gas Calibration", command=lambda:var2.set(1));
        secondButton.grid(row=1);
        w0=Label(frame2, text="Waiting for The Second gas to be connected and ready ", font='Helvetica 14 bold')
        w0.grid(row=0, pady=6)

        print("waiting for Second gas to be connected and ready");
        secondButton.wait_variable(var2)
        print("Reading Values")
        w0.grid_forget()
        w0=Label(frame2, text="Getting Values for Second Please wait... ", font='Helvetica 14 bold')
        w0.grid(row=0, pady=6)
        
        secondData=getdata(durationValue,spec);
        print(secondData)
        alpha=alphaCalculation(nitrogenData,secondData);
        w0.grid_forget()
        secondButton.destroy();

   
    startButton = Button(frame2, text=" Begin reading ", command=lambda:var2.set(1));
    startButton.grid(row=1);
    w0=Label(frame2, text="Waiting for air to be measured...", font='Helvetica 14 bold')
    w0.grid(row=0, pady=6)

    print("waiting for air to be measured ...");
    startButton.wait_variable(var2)
    print("Reading Values")
    frame2.grid_forget()
    measurement(durationValue,spec)

def automatic():
    print("automatic mode here we go")
    print("spectrometer flag  is");
    print(spectrometerFlag)
    durationValue=duration.get()
    calibrateValue=calibration.get()
    fillValue=int(fillWait.get())
    devices=sb.list_devices()
    
    frame2=Frame(root,width=450,height=50);
    frame2.grid(row=0);
    if(len(devices)>0):
        spec=sb.Spectrometer(devices[0])
        spec.integration_time_micros(int(integrationTime.get(),10))
    else:
        spec=0

    if calibrateValue:

        #code to turn on nitrogen valve
        print("turning on valve for nitrogen")
        
        w0=Label(frame2, text="Opening valve for Nitrogen Please wait... ", font='Helvetica 14 bold')
        w0.grid(row=0, pady=6)
        root.update()
        time.sleep(fillValue)
        w0.grid_forget()
        print("Reading Values")
        nitrogenData=getdata(durationValue,spec);
        print(nitrogenData)
        #code to turn on CO2 valve
        print("turning on valve for CO2")
        w0=Label(frame2, text="Opening valve for CO2 Please wait... ", font='Helvetica 14 bold')
        w0.grid(row=0, pady=6)
        root.update()
        time.sleep(fillValue)
        w0.grid_forget()
        print("Reading Values")
        secondData=getdata(durationValue,spec);
        print(secondData)
        alpha=alphaCalculation(nitrogenData,secondData);

    #code to turn on air valve
    print("turning on valve for air")
    w0=Label(frame2, text="Opening valve for air Please wait... ", font='Helvetica 14 bold')
    w0.grid(row=0, pady=6)
    root.update()
    time.sleep(fillValue)
    frame2.grid_forget()
    print("Reading Values")        
    measurement(durationValue,spec)


    
def measurement(durationValue,spec):
    
    frame3=Frame(root);
    frame3.grid(row=0);
    with open ('constants.txt', 'r') as f:
        first_column = [row[0] for row in csv.reader(f,delimiter='\t')]
    with open ('constants.txt', 'r') as f:
        second_column=[row[1] for row in csv.reader(f,delimiter='\t')]
    stopButton = Button(frame3, text=" Stop ", command=stop);
    stopButton.grid(row=1,column=0);
    startButton = Button(frame3, text=" Start ", command=startscan);
    startButton.grid(row=1,column=1);

    calibrateButton = Button(frame3, text="Re-calibrate ", command=recalibrate);
    calibrateButton.grid(row=1,column=3);
        
    button = Button(frame3, text="QUIT", command=quit)
    button.grid(row=1,column=2)

    w0=Label(frame3, text="Reading in process", font='Helvetica 14 bold')
    w0.grid(row=0, pady=6)
    root.update()
    ftpVar=ftp.get()
    ftpUserVar=ftpUser.get()
    ftpPassVar=ftpPass.get()
    
    if ftpConnection:
    	session = ftplib.FTP(ftpVar,ftpUserVar,ftpPassVar)
    count=0
    while(1):
        if(running):
            scanning(durationValue,spec,first_column,second_column,session,count)  # After 1 second, call scanning
        root.update()
        count=count+1

def recalibrate():
    calibration.set(1)
    if choice:
        manual();
    else:
        automatic();

def stop():
    global running
    running = False

    
def startscan():
    global running
    running = True
    
def scanning(durationValue,spec,first_column,second_column,session,count):
    global running 
    global ftpConnection
    global uploadTime
    global uploadInterval
    ftpPassVar=ftpPass.get()
    if running:
        x=getdata(durationValue,spec)
        out=[]
        date=str(datetime.datetime.now().date())
        dateFile=date+'.txt'
        f=open(dateFile,"a");
        for i in range(len(x)):
            if(float(first_column[i])!=0):
                out.insert(i,(x[i]-float(second_column[i]))/float(first_column[i]))
            else:
                out.insert(i,-1)
        time=str(datetime.datetime.now().time())
        f.write(time+'\t')
        for i in out:
            f.write(str(i)+'\t')
        f.write('\n')
        f.close()
        #print(time.localtime().tm_min)
#        print(uploadInterval)
        if (count%5==0  and ftpConnection==1):
        	print("uploading  now")
        	file = open(dateFile,'rb')                  # file to send
        	session.storbinary('STOR '+dateFile, file)     # send the file
        	file.close()
   #     	uploadTime=time.localtime().tm_min                                   # close file and FTP
        
        print(out)
        
   

def getdata(durationValue,spec):
    #get data here from spectrometer i guess
    print( "also wait for " + durationValue );
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
    else:
            c=c+1;
    for j in range(0,len(x)):
            x[j]=x[j]/c;
    return x

def alphaCalculation(x,y):
    z=[];
    z2=[]
    alphaN2=[]
    alphaCO2=[]
    with open ('N2.txt', 'r') as f:
        a = [row for row in csv.reader(f,delimiter='\t')]
        for i in range(len(a)):

                alphaN2.insert(i,float(a[i][0]))
        f.close()

    with open ('CO2.txt', 'r') as f:
        a = [row for row in csv.reader(f,delimiter='\t')]
        for i in range(len(a)):
                alphaCO2.insert(i,float(a[i][0]))

    for i in range(0,len(x)):
        z.insert(i,((x[i]-y[i])/(alphaN2[i]-alphaCO2[i])))
        z2.insert(i,((x[i]+y[i]-z[i]*(-alphaN2[i]-alphaCO2[i]))/2))
    print("this is before opening the file")
    f=open("constants.txt","w");
    for i in range(len(z)):
        f.write(str(z[i])+'\t'+str(z2[i])+'\n');
    f.close();
    return [z,z2];




def ftpConnect():
	global ftpConnection
	ftpVar=ftp.get()
	ftpUserVar=ftpUser.get()
	ftpPassVar=ftpPass.get()
	session = ftplib.FTP(ftpVar,ftpUserVar,ftpPassVar)
	if(session):
		ftpConnection=1
		messagebox.showinfo('Connected','connected to the ftp:'+ftpVar);
	else:
		 messagebox.showinfo('Failed to connect','Failed to connect to ftp:'+ftpVar);
	session.quit()
	return session



#ftpVar=ftp.get()
#ftpUserVar=ftpUser.get()
#ftpPassVar=ftpPass.get()
#session = ftplib.FTP(ftpVar,ftpUserVar,ftpPassVar)
#file = open('hello.txt','rb')                  # file to send
#session.storbinary('STOR hello.txt', file)     # send the file
#file.close()                                    # close file and FTP
#session.quit()


root = Tk()
#root.configure(background='black')
#root.style=Style()
#root.style.theme_use("vista")
root.attributes('-zoomed', True)
root.title('Optind Nephelometer Interface')
frame=Frame(root);
frame.grid(row=0);

font_value='Times 14'

#w0=Label(frame, text=" Optind Nephelometer Interface ", font='Times 15  bold').grid(row=0,column=0, pady=6)

w1=Label(frame, text="Session runtime(min) ",font=font_value).grid(row=3, pady=6)
duration = Entry(frame)
duration.grid(row=3, column=1)
duration.insert(END, "1")

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


w3=Label(frame, text="Upload interval(min)",font=font_value).grid(row=4, column=3)
uploadInt = Entry(frame)
uploadInt.grid(row=4, column=4)
uploadInt.insert(END, "5")

w2=Label(frame, text="Calibration Mode", font=font_value).grid(row=1,column=0)
mode = StringVar(frame)
modeChoices= [ 'Automatic', 'Manual'];
mode.set('Automatic') # set the default option
popupMenu = OptionMenu(frame, mode, *modeChoices)
popupMenu.grid(row = 1, column =1)

w3=Label(frame, text="Calibration?", font=font_value).grid(row=2,column=0)
calibration = IntVar()
Checkbutton(frame, text="Calibrate?", variable=calibration).grid(row=2,column=1)

w4=Label(frame, text="Auto recalibration time(min) ", font=font_value).grid(row=5)
scans = Entry(frame)
scans.grid(row=5, column=1)
scans.insert(END, "1")


w5=Label(frame, text="Gas interchange waiting time(sec)",font=font_value).grid(row=6)
fillWait = Entry(frame)
fillWait.grid(row=6, column=1)
fillWait.insert(END, "10")


w6=Label(frame, text="Integration time (ms)",font=font_value).grid(row=4)
integrationTime = Entry(frame)
integrationTime.grid(row=4, column=1)
integrationTime.insert(END, "100")



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

