import ftplib
from ftplib import FTP
import os
import subprocess as s
import datetime
from datetime import timedelta
import pandas as pd
import shutil

#This code is trying to protect the Master log file. If a script is partially run this code copies
#the file and moves to a different spot since the log can be accidentally wiped.

#The master log is keeping track of all files being pulled and date.

src = 'path_to_file_with_file_name'
dst = 'path_to_new_folder'

#Copy log file to back up location
shutil.copy(src, dst)

src2 = 'path_to_file_with_file_name_2'
dst2 = 'path_to_new_folder_with_timestamp'
shutil.copy(src2, dst2)

#Getting modification date of master log file and turning it into string and taking out some symbols.
mastermodtime = os.path.getmtime(src2)
mastermodtime = str(datetime.datetime.fromtimestamp(mastermodtime))
mastermodtime = mastermodtime.replace("-", "")
mastermodtime = mastermodtime.replace(":", "")
mastermodtime = mastermodtime.replace(" ", "")
mastermodtime = mastermodtime.replace(".", "")


#Change working drive
os.chdir(dst2)

#Duplicated Master Log added timestamp in name
os.rename('Master_Log.txt', 'Master_Log' + mastermodtime + '.txt')




#Change here

#-----------------------------------------------------------------

#This project was to be used as a template and replicated for other insurance carriers. The goal was to change
# only these two variables.

carrier = 'carrier1'

destination = 'destination_folder'

#----------------------------------------------------------------






carriername = carrier


#Contained credientials that program would grab depending upon which carrier was selected above in the change section
ctl = pd.read_csv('path_to_control.csv')


#Combining lists into a massive dictionary

carrier_list = [carrier for carrier in ctl['Carrier']]
host_list = [carrier for carrier in ctl['Host Name']]
type_list = [carrier for carrier in ctl['SFTP or FTP']]
user_list = [carrier for carrier in ctl['Username']]
password_list = [password for password in ctl['Password']]

dict1 = dict((z[0], list(z[1:])) for z in zip(carrier_list, host_list, type_list, user_list, password_list))

#Pull in control csv parameters
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
print("Please review the FtpLogFile(located at: path..")
print("")

#Output to screen

print("Username: " + username)
print("")
print("This program is set to currently place files here: " + destination)

#Number of objects in variable destination folder before pull


#Connect to ftp using credentials.

FTP = FTP(host)


FTP.login(user=username, passwd=password)


# #Getting list of files in remote folder and local folder.

#Remote Directory

outbounddrive = FTP.nlst()


#Local Directory
outboundfiles = outbounddrive

#Files already in folder to ignore - increased speed of the program if you don't have to pull them again.
existingfiles = os.listdir(destination)


carrierfolderbefore = len(existingfiles)

#Output how many files before
print("------Starting with " + str(carrierfolderbefore) + " objects in destination folder------")

#Prepare logging to Master log on downloaded files

masterfile = open('path_to_Master_Log.txt', 'r+')

#Read file....now storing that information into a variable. When writing to a file, always wants to paste it at bottom
# of file so I used this to post new entries at top.

masteroldtext = masterfile.read()
masterfile.close()

#Reopened and preparing to write over it. The plus sign means if file doesn't exist create it.

masterfile = open('path_to_Master_Log.txt', 'w+')


# #For loop deciding if a file name exists.
# # If exists, move on.
# # If not, specifying where file and file name and then where file should go and file name
# # Preserve modification time is time file was last modified on carrier ftp and
# # will be used as last modified on local drive.

for file in outboundfiles:
    if file in existingfiles:
        print("Passing on " + file)
    else:
        print("Downloading " + file)

        #Pull file for FTP module
        FTP.retrbinary("RETR " + file, open(destination + file, 'wb').write)
        masterfile.write("Downloaded " + file + "\n")
FTP.close()


#After done writing new text, add old text

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

#Start logging information. File will be created if not existing at: path

#Change working drive for Master Logs

os.chdir('path_to_master_log')

masterfile = open('path_to_master_log\Master_Log.txt', 'r+')
masteroldtext = masterfile.read()
masterfile.close()
masterfile = open('path_to_master_log\Master_Log.txt', 'w+')
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

os.chdir('to_not_master_path')

#Reading log file or creating a new one and saving old text. Next, writes log information and uses defined variables above.

file = open('to_not_master_path_FtpLogFile.txt', 'r+')
oldtext = file.read()
file.close()
file = open('to_not_master_path_FtpLogFile.txt', 'w+')
file.write("**************************************************" + "\n")
file.write("**************************************************" + "\n")
file.write(todaysdate + "\n")
file.write("\n")
file.write(str(carriername) + "\n")
file.write("\n")
file.write("Number of Files Pulled: " + str(carrierfoldercount) + "\n")
file.write("Number of Files in folder before pull(" + destination + "): " + str(carrierfolderbefore) + "\n")
file.write("Number of Files in folder after pull(" + destination + "): " + str(carrierfolderafter) + "\n")

#This can be used to find files of certain names and give basically an alert or heads up in log.

file.write("ALERTS:" + "\n")

#Use in if statement...from todays day minus 14 days if you see anything with file names write in log.
seven = (datetime.datetime.today() + timedelta(days=-14))


Sub = 'FTP_Confirmation'
Sub2 = 'Test_FTP'

for text in existingfiles:
    if Sub in text or Sub2 in text:
        x = 'path_to_file\\' + text
        modTimesinceEpoc = os.path.getmtime(x)
        modificationTime = datetime.datetime.fromtimestamp(modTimesinceEpoc)
        #If any of files pull have the Sub or Sub2 in name, write in log.
        if modificationTime >= seven:
            file.write(text + '-' + str(modificationTime) + "\n")

file.write("WARNING:" + "\n")
file.write("(FILES BELOW NOT PULLED BECAUSE DUPLICATED FILE NAME. PLEASE REVIEW AND MANUALLY PULL IF NEED BE)." + "\n")
#file.write(duplicates + "\n")
for dup in duplicates:
    file.write(str(dup) + "\n")
#Add old text
file.write(oldtext + "\n")
file.close()


controlstamp = os.listdir('path_withtimestamp')
numberofcontrolstamps = len(os.listdir('path_withtimestamp'))

#Empty folder when 10 backups have been created...
if numberofcontrolstamps == 10:
    for file in controlstamp:
        file = str(file)
        stamp = 'path_withtimestamp' + file
        os.remove(stamp)
else:
    pass


print("Please review log file....")
input("Press Enter to exit")

#Open FtpLogFile for user at end for review.

s.Popen(['start', 'FtpLogFile.txt'], shell=True)
