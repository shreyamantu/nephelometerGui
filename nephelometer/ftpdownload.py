import ftplib

ftpVar='optind.in'
ftpUserVar='neph'
ftpPassVar='optind123**'
ftp = ftplib.FTP(ftpVar,ftpUserVar,ftpPassVar)
ftp.cwd('/conf/')
filename='config.txt'
localfile=open(filename,'wb')
ftp.retrbinary('RETR ' + filename,localfile.write, 1024)
ftp.quit()
localfile.close()
ftpConnection=1



