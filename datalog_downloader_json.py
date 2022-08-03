import ftplib
from ftplib import FTP
import os
import subprocess as s
import datetime
import time
from datetime import timedelta
import pandas as pd
import shutil
import json

#This code is trying to protect the Master log file. If a script is partially run this code copies
#the file and moves to a different spot since the log can be accidentally wiped.

control_files_folder='C:/Users/bob.g/SigmaSense.com/SigmaSense Intranet - Production_Data/FTP_automation/settings/'
log_files_folder='C:/Users/bob.g/SigmaSense.com/SigmaSense Intranet - Production_Data/FTP_automation/Log Files/'
backup_log_files_folder=log_files_folder + 'backup_logs/'

#The master log is keeping track of all files being pulled and date.

src = log_files_folder + 'Master_Log.txt'
master_log_file=log_files_folder + 'Master_Log.txt'
master_log_file_json=log_files_folder + 'Master_Log.json'
diag_log_file=log_files_folder + 'diagnostic_log.txt'
dst = backup_log_files_folder

#Copy log file to back up location
shutil.copy(master_log_file, backup_log_files_folder)

#src2 = log_files_folder + 'Master_Log.txt'
#dst2 = log_files_folder + 'backup_logs/'
#shutil.copy(src2, dst2)   #bg:  I can't figure out what this is trying to do.

#Getting modification date of master log file and turning it into string and taking out some symbols.
mastermodtime = os.path.getmtime(master_log_file)
mastermodtime = str(datetime.datetime.fromtimestamp(mastermodtime))
mastermodtime = mastermodtime.replace("-", "")
mastermodtime = mastermodtime.replace(":", "")
mastermodtime = mastermodtime.replace(" ", "")
mastermodtime = mastermodtime.replace(".", "")


#Change working drive
os.chdir(backup_log_files_folder)

#Duplicated Master Log added timestamp in name
timestamped_log_name= 'Master_Log' + mastermodtime + '.txt'
os.rename('Master_Log.txt', timestamped_log_name)




#Change here

#-----------------------------------------------------------------

#This project was to be used as a template and replicated for other insurance carriers. The goal was to change
# only these two variables.

supplier = 'ISE'                #use this record in the Control.csv file

destination = 'C:/Users/bob.g/SigmaSense.com/SigmaSense Intranet - Production_Data/FTP_automation/Temp_dest_folder/'        #destination for downloaded files

#----------------------------------------------------------------

#carriername = carrier

#Contained credientials that program would grab depending upon which carrier was selected above in the change section
ctl = pd.read_csv(control_files_folder + 'Control.csv')


#Combining lists into a  dictionary

supplier_list = [supplier for supplier in ctl['Supplier']]
host_list = [supplier for supplier in ctl['Host Name']]
type_list = [supplier for supplier in ctl['SFTP or FTP']]
user_list = [supplier for supplier in ctl['Username']]
password_list = [password for password in ctl['Password']]
remote_dir_list = [supplier for supplier in ctl['Remote_dir']]

dict1 = dict((z[0], list(z[1:])) for z in zip(supplier_list, host_list, type_list, user_list, password_list,remote_dir_list))

#Pull in control csv parameters
host = dict1[supplier][0]
username = dict1[supplier][2]
password = dict1[supplier][3]
remote_dir = dict1[supplier][4]
#print ("remote dir is", remote_dir)
#Getting todays date and restructing it
date = datetime.datetime.today()
month = str(date.month).zfill(2)
day = str(date.day).zfill(2)
year = str(date.year).zfill(2)
hour=str(date.hour).zfill(2)
minute=str(date.minute).zfill(2)
todaysdate = str(month + "/" + day + "/" + year + " " + hour +":"+ minute)
print ("today's date is: " + todaysdate)
#Output to screen
print("")
print("This program pulls files from a supplier sftp or ftp site.")
print("")
print("Please review the FtpLogFile(located at: " + log_files_folder)
print("")

#Output to screen

print("Username: " + username)
print("")
print("This program is set to currently place files here: " + destination)

#Number of objects in variable destination folder before pull


#Connect to ftp using credentials.

FTP = FTP(host)


FTP.login(user=username, passwd=password)

welcome_message=FTP.getwelcome()
print("FTP server welcome message is: " + welcome_message)

# #Getting list of files in remote folder and local folder.

#Remote Directory

outbounddrive = FTP.nlst(remote_dir)
# print ("remote dir is: ")
# print (outbounddrive)           #bg:  this is a little odd.  it doesn't attempt to go to a certain dir.  hardcode for now.

# print ("printing out the struct returned by mlsd")
# for name, fact in FTP.mlsd(remote_dir):

#     print(name);
#     this_name=name
#     print("////");
#     print(fact);


#Local Directory
outboundfiles = outbounddrive

#Files already in folder to ignore - increased speed of the program if you don't have to pull them again.
existingfiles = os.listdir(destination)
#print ("existing files are: " )
#print (existingfiles)

carrierfolderbefore = len(existingfiles)

#Output how many files before
print("------Starting with " + str(carrierfolderbefore) + " objects in destination folder------")

#Prepare logging to Master log on downloaded files

masterfile = open(master_log_file, 'r+')
masterfile_lines=masterfile.readlines()
masterfile.close()

masterfile_json=open(master_log_file_json,'r+')
masterfile_json_data=json.load(masterfile_json)
#list_of_downloaded_files_json=masterfile_json_data('source_file')  #i guess this doesn't work.

for this_item in masterfile_json_data:
    print (this_item)
    print (this_item["source_file"])

#########################################
#########################################
#leaving off notes:  I want to switch the log file to json.  I need to add file IO to add new records to it, and sub out the list that I check against to xxx_json_data.
#########################################
########################################

masterfile = open(master_log_file, 'r+')        #each read seems to consume the data
masteroldtext = masterfile.read()
masterfile.close()

diagfile= open(diag_log_file, 'r+')
#Action,download_date,file_name,size_in_MB,size,mod_date
 #Read file....now storing that information into a variable. When writing to a file, always wants to paste it at bottom
 # of file so I used this to post new entries at top.

#masterfile_lines=masterfile.readlines()
#masteroldtext = masterfile.read()

diagoldtext=diagfile.read()
#masterfile.close()
diagfile.close()

 #Reopened and preparing to write over it. The plus sign means if file doesn't exist create it.

masterfile = open(master_log_file, 'w+')

diagfile= open(diag_log_file, 'w+')


diagfile.write("**************************************************" + "\n")
diagfile.write("**************************************************" + "\n")
diagfile.write(todaysdate + "\n")
diagfile.write("\n")
diagfile.write(str(supplier) + "\n")
diagfile.write("\n")

# Kill be used as last modified on local drive.

#confirm how to access the masterfile struct:
for line in masterfile_lines:
    print (line)
#end masterfile struct experiment

existingfiles=masterfile_lines          #refer to the log file instead of the dir for what has been downloaded

# for file in outboundfiles:
for name, fact in FTP.mlsd(remote_dir):
    if fact["type"]== 'file':                               # the first thing it lists is the current and parent directory 
        
        if name in existingfiles:
            print("File Exists: Passing on " + name)
        else:
            print(fact)
            print("Downloading " + name)


            #decide what to do with this file.  Based on the file name, put it in the right subdir.
            #check for corr/setup/other kinds of trash files:
           # this_name=str(name)             #make sure its a string
            summary=False
            text_file=False
            setup_file=False
            dest_subdir="sorted_good_stdf"

            

            #see if it is a text file:
            if ".txt" in name:
                print("this is a text file")
                text_file=True
                dest_subdir="text_datalogs"

                #see if it is a summary file:
            if "summary" in name:
                print ("this is a summary file")
                summary=True
                dest_subdir="text_summaries"

            corr_strings={"CORR","SETUP","VERIFICATION","REPEATABILITY"}
            for  this_string in corr_strings:
                if this_string in name.upper():
                    print ("this is a setup file")
                    setup_file=True
                    dest_subdir="rejected_trash_files"
            #done figuring out where to put the files
            #Pull file for FTP module
            #print("ftp command will be" + "RETR " + 'DATA/QUAL/' + file)
            
            FTP.retrbinary("RETR " + remote_dir + name, open(destination + name, 'wb').write)
            #fix the date of the newly downloaded file:
            fileLocation = destination + name
            modify_date=fact["modify"]
            f_year = modify_date[0:4]
            f_month = modify_date[4:6]
            f_day = modify_date[6:8]
            f_hour = modify_date[8:10]
            f_minute = modify_date[10:12]
            f_second = modify_date[12:14]

            date = datetime.datetime(year=int(f_year), month=int(f_month), day=int(f_day), hour=int(f_hour), minute=int(f_minute), second=int(f_second))
            print (date)
            modTime = time.mktime(date.timetuple())
            size_in_MB=int(fact["size"])/1000000
            os.utime(fileLocation, (modTime, modTime))
            #done fixing the date
            #move it to the write sub dir:
            shutil.move(fileLocation, destination + dest_subdir)
            masterfile.write("Downloaded," + todaysdate + ", " + remote_dir + name + ", " + str(size_in_MB)+ "MB, " + fact["size"]+ ", " + str(date) +"\n")
            diagfile.write("Downloaded " + remote_dir + name + " " + str(size_in_MB)+ "MB " + fact["size"]+ " " + str(date) +"\n")
FTP.close()

#ftp times are defined here: https://datatracker.ietf.org/doc/html/rfc3659#page-6  
# basically they are 14 text digits.


# #After done writing new text, add old text
masterfile.write(masteroldtext)
#print(masteroldtext)
masterfile.close()

#


# #How many files in folder after pull.

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

os.chdir(log_files_folder)

# masterfile = open('Master_Log.txt', 'r+')
# masteroldtext = masterfile.read()
# masterfile.close()
# masterfile = open('Master_Log.txt', 'w+')
# masterfile.write("**************************************************" + "\n")
# masterfile.write("**************************************************" + "\n")
# masterfile.write(todaysdate + "\n")
# masterfile.write("\n")
# masterfile.write(str(supplier) + "\n")
# masterfile.write("\n")
diagfile.write("Number of Files Pulled: " + str(carrierfoldercount) + "\n")
diagfile.write("Number of Files in folder before pull(" + destination + "): " + str(carrierfolderbefore) + "\n")
diagfile.write("Number of Files in folder after pull(" + destination + "): " + str(carrierfolderafter) + "\n")
diagfile.write("\n")
diagfile.write("Files Downloaded:" + "\n")
# masterfile.write(masteroldtext + "\n")
diagfile.write(diagoldtext + "\n")
diagfile.close()
# #Change working drive

os.chdir(log_files_folder)

#Reading log file or creating a new one and saving old text. Next, writes log information and uses defined variables above.

file = open('FtpLogFile.txt', 'r+')
oldtext = file.read()
file.close()
file = open('FtpLogFile.txt', 'w+')
file.write("**************************************************" + "\n")
file.write("**************************************************" + "\n")
file.write(todaysdate + "\n")
file.write("\n")
file.write(str(supplier) + "\n")
file.write("\n")
file.write("Number of Files Pulled: " + str(carrierfoldercount) + "\n")
file.write("Number of Files in folder before pull(" + destination + "): " + str(carrierfolderbefore) + "\n")
file.write("Number of Files in folder after pull(" + destination + "): " + str(carrierfolderafter) + "\n")

#This can be used to find files of certain names and give basically an alert or heads up in log.

file.write("ALERTS:" + "\n")

# #Use in if statement...from todays day minus 14 days if you see anything with file names write in log.
# seven = (datetime.datetime.today() + timedelta(days=-14))


# Sub = 'FTP_Confirmation'
# Sub2 = 'Test_FTP'

# for text in existingfiles:
#     if Sub in text or Sub2 in text:
#         x = 'path_to_file\\' + text
#         modTimesinceEpoc = os.path.getmtime(x)
#         modificationTime = datetime.datetime.fromtimestamp(modTimesinceEpoc)
#         #If any of files pull have the Sub or Sub2 in name, write in log.
#         if modificationTime >= seven:
#             file.write(text + '-' + str(modificationTime) + "\n")

# file.write("WARNING:" + "\n")
# file.write("(FILES BELOW NOT PULLED BECAUSE DUPLICATED FILE NAME. PLEASE REVIEW AND MANUALLY PULL IF NEED BE)." + "\n")
# #file.write(duplicates + "\n")
# for dup in duplicates:
#     file.write(str(dup) + "\n")
# #Add old text
# file.write(oldtext + "\n")
# file.close()


# controlstamp = os.listdir('path_withtimestamp')
# numberofcontrolstamps = len(os.listdir('path_withtimestamp'))

# #Empty folder when 10 backups have been created...
# if numberofcontrolstamps == 10:
#     for file in controlstamp:
#         file = str(file)
#         stamp = 'path_withtimestamp' + file
#         os.remove(stamp)
# else:
#     pass


print("completed successfully")
#input("Press Enter to exit")

#Open FtpLogFile for user at end for review.

#s.Popen(['start', 'FtpLogFile.txt'], shell=True)
