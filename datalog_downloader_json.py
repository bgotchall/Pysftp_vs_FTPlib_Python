from decimal import ROUND_DOWN
from pickle import FALSE, TRUE
import sys
from ftplib import FTP
import os
import subprocess as s
import datetime
import time
from datetime import timedelta
from numpy import true_divide
import pandas as pd
import shutil
import json
import random

def setup():
    print ("Starting Custom FTP utility")


def main(args):
    # arguments
    if args[1]=='-v':
        verbose=True
    else:
        verbose=False
    # configuration variables:
    log_files_folder='C:/Users/bob.g/SigmaSense.com/SigmaSense Intranet - Production_Data/FTP_automation/Log Files/'
    control_files_folder='C:/Users/bob.g/SigmaSense.com/SigmaSense Intranet - Production_Data/FTP_automation/settings/'
    master_log_filename=log_files_folder + 'Master_Log.json'
    backup_log_files_folder=log_files_folder + 'backup_logs/'

    supplier = 'ISE'                #use this record in the Control.csv file
    destination_folder = 'C:/Users/bob.g/SigmaSense.com/SigmaSense Intranet - Production_Data/FTP_automation/Temp_dest_folder/'        #destination for downloaded files

    #end config variables

    #Copy log file to back up location in case this messes up.  the log file must never be deleted...
    #append a random string on the end of the last copy of the master file and save it off for manual recovery if needed.
    temp=random.randrange(1,1000000000)
    temp=str(temp)
    shutil.copy(master_log_filename, backup_log_files_folder + 'Master_Log_' + temp + '.json')


    # diagnostic section to verify master file is readible
    masterfile=open(master_log_filename,'r+')
    masterfile_data=json.load(masterfile)
    masterfile.close()                          


    # print("#################### echoing out the log file: ###########################################")
    # for this_item in masterfile_data:
    #     print (this_item)
    #     #print (this_item["source_file"])
    # print("##########################################################################################")



    #get credentials info from control file
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

    #open up the FTP source and get a listing:
    my_FTP = FTP(host)
    my_FTP.login(user=username, passwd=password)

    welcome_message=my_FTP.getwelcome()
    print("FTP server welcome message is: " + welcome_message)


    #try to get a list of all file names:
    #just iterate...
    files_already_downloaded=[]
    for this_item in masterfile_data:
        files_already_downloaded.append(this_item["source_file"])           #make a list of the "source_file" records.  I don't actually use anything else in the log file yet.

    if not verbose: print("checking files:")
    for name, fact in my_FTP.mlsd(remote_dir):
        if fact["type"]== 'file':                               # the first thing it lists is the current and parent directory.  So skip until you get to actual files.
            
            if not verbose: print(".", end ="")
            if name in files_already_downloaded:                                     #["source_file"]:
                if verbose: print("File Exists: Passing on " + name)
            else:
                if verbose: print(fact)
                if verbose: print("Downloading " + name)
                #decide what to do with this file.  Based on the file name, put it in the right subdir.
                #check for corr/setup/other kinds of trash files:
                summary=False
                text_file=False
                setup_file=False
                dest_subdir="sorted_good_stdf"

                
                #see if it is a text file:
                if ".txt" in name:
                    if verbose: print("this is a text file")
                    text_file=True
                    dest_subdir="text_datalogs"

                if int(fact["size"]) < 20000:
                    if verbose: print("This is a small 1-device file, probably a setup file")
                    setup_file=True
                    dest_subdir="rejected_trash_files"

                    #see if it is a summary file:
                if "summary" in name:
                    if verbose: print ("this is a summary file")
                    summary=True
                    dest_subdir="text_summaries"

                

                corr_strings={"CORR","SETUP","VERIFICATION","REPEATABILITY"}                  #3 consecutive underscores can mean they didn't do data entry, but shows up in good files too.
                for  this_string in corr_strings:
                    if this_string in name.upper():
                        if verbose: print ("this is a setup file")
                        setup_file=True
                        dest_subdir="rejected_trash_files"
                #done figuring out where to put the files
                #Pull file for FTP module
                #print("ftp command will be" + "RETR " + 'DATA/QUAL/' + file)
                if verbose: print("ftp command will be" + "RETR " + remote_dir + name)
                
                try:
                    FTP.retrbinary("RETR " + remote_dir + name, open(destination_folder + name, 'wb').write)
                except:
                    if verbose: print("################Error.  FTP get failed.")
                else:
                    #C:\Users\bob.g\SigmaSense.com\SigmaSense Intranet - Production_Data\FTP_automation\Temp_dest_folder
                    #fix the date of the newly downloaded file:
                    fileLocation = destination_folder + name
                    modify_date=fact["modify"]
                    f_year = modify_date[0:4]
                    f_month = modify_date[4:6]
                    f_day = modify_date[6:8]
                    f_hour = modify_date[8:10]
                    f_minute = modify_date[10:12]
                    f_second = modify_date[12:14]

                    date = datetime.datetime(year=int(f_year), month=int(f_month), day=int(f_day), hour=int(f_hour), minute=int(f_minute), second=int(f_second))
                    modTime = time.mktime(date.timetuple())
                    size_in_MB=int(fact["size"])/1000000
                    os.utime(fileLocation, (modTime, modTime))
                #done fixing the date
                #move it to the write sub dir:
                try:
                    shutil.move(fileLocation, destination_folder + dest_subdir)
                except:
                    if verbose: print("this file already exists-- deleting the temp version")
                    try:
                        os.remove(destination_folder + name)
                    except:
                        if verbose: print("removing the temp file didn't work, probably because the download itself failed")

                new_json_item=dict()
                new_json_item.update({"action": "Downloaded"})
                new_json_item.update({"download_date": str(datetime.datetime.today())})
                new_json_item.update({"source_file": name})
                new_json_item.update({"size_in_mb": str(size_in_MB)})
                new_json_item.update({"size_in_bytes": fact["size"]})
                new_json_item.update({"server_date": str(date)})

                masterfile_data.append(new_json_item)
                #write the log file after every download:
                json_object=json.dumps(masterfile_data,indent=4)

                masterfile=open(master_log_filename,'w')
                masterfile.write(json_object)
                masterfile.close() 
    my_FTP.close()
    print ("FTP utility closing normally")            




# If run this script directly, do:

	
   # print(f"Arguments count: {len(sys.argv)}")

   # for i, arg in enumerate(sys.argv):
   #     print(f"Argument {i:>6}: {arg}")

if __name__ == '__main__':
    setup()
    try:
        main(sys.argv)
    # When 'Ctrl+C' is pressed, the child program
    # destroy() will be  executed.
    except KeyboardInterrupt:
        destroy()

