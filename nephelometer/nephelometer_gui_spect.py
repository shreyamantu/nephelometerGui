import RPi.GPIO as GPIO            
from tkinter import *
from tkinter.ttk import *
import tkinter as tk
import numpy as np
import time as time
from struct import  * 
import seabreeze.spectrometers as sb
from tkinter import messagebox
import csv

def spectrometerConnect():
	devices=sb.list_devices()
	print(devices)
	if(len(devices)>0):
		spectrometerFlag=1
		print("Something is connected")
		messagebox.showinfo("Detected", "Spectrometer detected :"+str(devices[0]))
		return 1
	else:
		messagebox.showinfo("Error", "No spectrometer detected")
		return 0
	
def start():
    print("starting program");
    frame.grid_forget()
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
        print(alpha);
        f=open("constants.txt","w");
        for i in alpha:
            f.write(str(i)+'\n');
        f.close();
        w0.grid_forget()
        secondButton.destroy();

    startButton = Button(frame2, text=" Begin reading ", command=lambda:var2.set(1));
    startButton.grid(row=1);
    w0=Label(frame2, text="Waiting for air to be measured...", font='Helvetica 14 bold')
    w0.grid(row=0, pady=6)

    print("waiting for air to be measured ...");
    startButton.wait_variable(var2)
    print("Reading Values")
    measurement(spec)
    



def automatic():
    print("automatic mode here we go")
        
def measurement(spec):
	with open ('constants.txt', 'r') as f:
		first_column = [row[0] for row in csv.reader(f,delimiter='\t')]
		

def getdata(durationValue,spec):
    #get data here from spectrometer i guess
    print( "also wait for" + durationValue );
    start=time.time()
    c=0;
    x=[1,2,3,4,5]
    devices=sb.list_devices()

    if(len(devices)>0):
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
    return [z,z2];


spectrometerFlag=0
root = Tk()
#root.configure(background='black')
#root.style=Style()
#root.style.theme_use("vista")
frame=Frame(root);
frame.grid(row=0);

w0=Label(frame, text=" Nephelometer Interface ", font='Helvetica 14 bold').grid(row=0, pady=6)

w1=Label(frame, text="Session runtime(min) ").grid(row=3, pady=6)
duration = Entry(frame)
duration.grid(row=3, column=1)
duration.insert(END, "1")


w2=Label(frame, text="Calibration Mode").grid(row=1,column=0, pady=6)
mode = StringVar(frame)
modeChoices= [ 'Automatic', 'Manual'];
mode.set('Automatic') # set the default option
popupMenu = OptionMenu(frame, mode, *modeChoices)
popupMenu.grid(row = 1, column =1)

w6=Label(frame, text="Calibration?").grid(row=2,column=0, pady=6)
calibration = IntVar()
Checkbutton(frame, text="Calibrate?", variable=calibration).grid(row=2,column=1)


w3=Label(frame, text="Scan to average ").grid(row=5, pady=6)
scans = Entry(frame)
scans.grid(row=5, column=1)
scans.insert(END, "1")

w4=Label(frame, text="Integration time ").grid(row=4, pady=6)
integrationTime = Entry(frame)
integrationTime.grid(row=4, column=1)
integrationTime.insert(END, "100")



button = Button(frame, text="QUIT", command=quit)
button.grid(row=4,column=3, pady=10)

startButton = Button(frame, text="Start program", command=start)
startButton.grid(row=3,column=3, pady=10)

spectrometerButton = Button(frame, text="Connect spectrometer", command= spectrometerConnect)
spectrometerButton.grid(row=2,column=3, pady=10)


tk.mainloop()


