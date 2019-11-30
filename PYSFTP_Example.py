import os
import pysftp
import subprocess as s
import datetime
from datetime import timedelta
import pandas as pd
import shutil

#This is needed for pysftp or you have to specify your host keys which isn't fun. This accepts the host keys provided
# by your connection and can be somewhat risky I've read.
cnopts = pysftp.CnOpts()
cnopts.hostkeys = None

#This code is trying to protect the Master log file. If a script is partially run this code copies
#the file and moves to a different spot since the log can be accidentally wiped.

src = 'J:\Master_Log.txt'
dst = 'J:\Master_Backup'

#Copy log file to back up location

shutil.copy(src, dst)

src2 = 'J:\Master_Log.txt'
dst2 = 'J:\With_Timestamp'
shutil.copy(src2, dst2)


#Getting modification date of master log file and turning it into string and taking out some symbols.

mastermodtime = os.path.getmtime(src2)
mastermodtime = str(datetime.datetime.fromtimestamp(mastermodtime))
mastermodtime = mastermodtime.replace("-", "")
mastermodtime = mastermodtime.replace(":", "")
mastermodtime = mastermodtime.replace(" ", "")
mastermodtime = mastermodtime.replace(".", "")

#Change working drive
os.chdir('J:\With_Timestamp')
os.rename('Master_Log.txt', 'Master_Log' + mastermodtime + '.txt')



#Change here


#-----------------------------------------------------------------

carrier = 'AnthemEfx'

destination = 'J:\HoldFolder\\'

outbounddrive = ''

#----------------------------------------------------------------


#Take data from excel file and put into data frame and then make into lists and combine lists.

carriername = carrier

ctl = pd.read_csv('J:\Control.csv')

carrier_list = [carrier for carrier in ctl['Carrier']]
host_list = [carrier for carrier in ctl['Host Name']]
type_list = [carrier for carrier in ctl['SFTP or FTP']]
user_list = [carrier for carrier in ctl['Username']]
password_list = [password for password in ctl['Password']]

dict1 = dict((z[0], list(z[1:])) for z in zip(carrier_list, host_list, type_list, user_list, password_list))

#Pull in control csv parameters into variables
host = dict1[carrier][0]
username = dict1[carrier][2]
password = dict1[carrier][3]

#Getting todays date and restructing it
date = datetime.datetime.today()
month = str(date.month)
day = str(date.day)
year = str(date.year)
todaysdate = str(month + "/" + day + "/" + year)


#Output to screen
print("")
print("This program pulls files from a carrier sftp or ftp site.")
print("")
print("Please review the FtpLogFile(located at: J:\FTP when finished..")
print("")

#Output to screen

print("Username: " + username)
print("")
print("This program is set to currently place files here: " + destination)

#Number of objects in variable destination folder before pull


#Connect to sftp using credentials.
#Cnopts is defined. It is defaulted to accept the hostkey provided by the server.


srv = pysftp.Connection(host=host, username=username, password=password, cnopts=cnopts)

#Getting list of files in remote folder and local folder.

outboundfiles = srv.listdir(outbounddrive)

existingfiles = os.listdir(destination)

carrierfolderbefore = len(existingfiles)


print("------Starting with " + str(carrierfolderbefore) + " objects in destination folder------")


#Prepare logging to Master log on downloaded files

masterfile = open('J:\Master_Log.txt', 'r+')
masteroldtext = masterfile.read()
masterfile.close()
masterfile = open('J:\Master_Log.txt', 'w+')


#For loop deciding if a file name exists.
# If exists, move on.
# If not, specifying where file and file name and then where file should go and file name
# Preserve modification time is time file was last modified on carrier ftp and
# will be used as last modified on local drive.

for f in outboundfiles:
    file = f
    if file in existingfiles:
        print("Passing on " + file)
    else:
        print("Downloading " + file)

        #Download files with pysftp is a little different
        srv.get(outbounddrive + file, destination + file, preserve_mtime=True)
        masterfile.write("Downloaded " + file + "\n")


masterfile.write(masteroldtext + "\n")
masterfile.close()


#How many files in folder after pull.
pull = os.listdir(destination)
carrierfolderafter = len(pull)

print("------Ending with " + str(carrierfolderafter) + " objects in destination folder------")

carrierfoldercount = carrierfolderafter - carrierfolderbefore

print("------Number of files pulled was " + str(carrierfoldercount) + ".------")

#Looking at remote drive and deciding if in a list if their are duplicate values

duplicates = [x for x in outboundfiles if outboundfiles.count(x) > 1]

print("Files reviewed. Moving to log information.")

#Start logging information. File will be created if not existing at: J:\FTP

#Change working drive for Master Logs

os.chdir('J:\Control Files')

masterfile = open('J:\Master_Log.txt', 'r+')
masteroldtext = masterfile.read()
masterfile.close()
masterfile = open('J:\Master_Log.txt', 'w+')
masterfile.write("**************************************************" + "\n")
masterfile.write("**************************************************" + "\n")
masterfile.write(todaysdate + "\n")
masterfile.write("\n")
masterfile.write(str(carriername) + "\n")
masterfile.write("\n")
masterfile.write("Number of Files Pulled: " + str(carrierfoldercount) + "\n")
masterfile.write("Number of Files in folder before pull(" + destination + "): " + str(carrierfolderbefore) + "\n")
masterfile.write("Number of Files in folder after pull(" + destination + "): " + str(carrierfolderafter) + "\n")
masterfile.write("\n")
masterfile.write("Files Downloaded:" + "\n")
masterfile.write(masteroldtext + "\n")
masterfile.close()


#Change working drive

os.chdir('J:\FTP')

#Reading log file or creating a new one and saving old text. Next, writes log information and uses defined variables above.

file = open('J:\FtpLogFile.txt', 'r+')
oldtext = file.read()
file.close()
file = open('J:\FtpLogFile.txt', 'w+')
file.write("**************************************************" + "\n")
file.write("**************************************************" + "\n")
file.write(todaysdate + "\n")
file.write("\n")
file.write(str(carriername) + "\n")
file.write("\n")
file.write("Number of Files Pulled: " + str(carrierfoldercount) + "\n")
file.write("Number of Files in folder before pull(" + destination + "): " + str(carrierfolderbefore) + "\n")
file.write("Number of Files in folder after pull(" + destination + "): " + str(carrierfolderafter) + "\n")

#This can be used to find files of certain names.

file.write("ALERTS:" + "\n")
seven = (datetime.datetime.today() + timedelta(days=-20))

Sub = 'FTP_Confirmation'
Sub2 = 'Test_FTP'

for text in existingfiles:
    if Sub in text or Sub2 in text:
        x = 'J:\HoldFolder\\' + text
        modTimesinceEpoc = os.path.getmtime(x)
        modificationTime = datetime.datetime.fromtimestamp(modTimesinceEpoc)
        if modificationTime >= seven:
            file.write(text + '-' + str(modificationTime) + "\n")

#User duplicates list defined above and prints out for user.

file.write("WARNING:" + "\n")
file.write("(FILES BELOW NOT PULLED BECAUSE DUPLICATED FILE NAME. PLEASE REVIEW AND MANUALLY PULL IF NEED BE)." + "\n")
#file.write(duplicates + "\n")
for dup in duplicates:
    file.write(str(dup) + "\n")
#Add old text
file.write(oldtext + "\n")
file.close()

#Clear With_Timestamp folder once it reaches 10 files

controlstamp = os.listdir('J:\With_Timestamp')
numberofcontrolstamps = len(os.listdir('J:\With_Timestamp'))

if numberofcontrolstamps == 10:
    for file in controlstamp:
        file = str(file)
        stamp = 'J:\With_Timestamp\\' + file
        os.remove(stamp)
else:
    pass

print("Please review log file....")
input("Press Enter to exit")

#Open FtpLogFile for user

s.Popen(['start', 'FtpLogFile.txt'], shell=True)

