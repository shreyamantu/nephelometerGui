import csv 

x=[1,2,3,4,5] 
y=[2,3,4,5,6] 
z=[]
z2=[] 
alphaN2=[] 
alphaCO2=[] 

with open ('N2.txt', 'r') as f:
	a = [row for row in csv.reader(f,delimiter='\t')]
	for i in range(len(a)):
		alphaN2.insert(i,float(a[i][0]))


with open ('CO2.txt', 'r') as f:
	a=[]
	a = [row for row in csv.reader(f,delimiter='\t')]
	for i in range(len(a)):
		alphaCO2.insert(i,float(a[i][0]))
print(len(x))	
for i in range(0,len(x)):
	print(z)
	z.insert(i,(x[i]-y[i])/(alphaN2[i]-alphaCO2[i]))
	z2.insert(i,(x[i]+y[i]-z[i]*(-alphaN2[i]-alphaCO2[i]))/2)
z=[z,z2]
print(z)

