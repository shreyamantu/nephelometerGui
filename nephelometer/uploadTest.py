import os.path, os
from ftplib import FTP, error_perm
import ftplib
import datetime
host = 'optind.in'

ftp = ftplib.FTP(host,'neph','optind123**')
filenameCV = "saveFiles/"
date=str(datetime.datetime.now().date())
filenameCV=filenameCV+date
print(filenameCV)
try:
	ftp.mkd(date)
except:
	print("cannot maake")
ftp.cwd(date)


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

placeFiles(ftp, filenameCV)

ftp.quit()
