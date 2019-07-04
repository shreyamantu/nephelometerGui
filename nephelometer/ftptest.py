import ftplib
session = ftplib.FTP('optind.in','neph','optind123**')
file = open('hello.txt','rb')                  # file to send
session.storbinary('STOR hello.txt', file)     # send the file
file.close()                                    # close file and FTP
session.quit()



