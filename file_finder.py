# PLATFORM INDEPENDENT FILE FINDER

import os 
import subprocess
import argparse
import time
import re
import platform 

name=subprocess.getoutput("whoami").split('\\')[-1]
system_name=platform.system()

# THIS FUNCTION ENSURES THAT THE PROGRAM GETS A USER INPUT THROUGH CLI
# EX: python name_of_the_file.py -s "filename to be searched"
def search():
    # parser=argparse.ArgumentParser(description="Search any file with this")
    # parser.add_argument('-s','--search',required=True,help="specify the file name you want to search ")
    # # parser.add_argument('-e','--ext',required=False,help="specify the extension of the file you want to search")
    
    # args=parser.parse_args()
    # return args.search
    choice=input("Enter the file/keyword you want to search :").strip().strip('"')
    return choice


# HIGHLIGHTS THE SEARCHED INPUT WITH RED COLOR
def highlighted(path,filename):
    return re.sub(
        re.escape(filename),
        lambda m: f"\033[31m{m.group(0)}\033[0m",
        path,
        flags=re.IGNORECASE
    )
    
    
# THIS FUNCTION TRAVERSES ALL THE FILES MATCHING WITH THE USER INPUT AND WILL RETURN THEIR PATH AS SOON AS THEY ARE FOUND
def check_file(path, filename):
    count=0
    found=False
    for root, dirs, files in os.walk(path):
        for file in files:
            if filename.casefold() in file.casefold():
                full_path=os.path.join(root,file)
                print(f"├──{highlighted(full_path,filename)}")
                count+=1
                found= True
    return found,count


# OPEN FILES IF A USER WANTS TO .
def open_file():
    choice=input("Do you want to open any of these files: ")
    if choice.strip() in ['y','yes','Y',"YES"]:
        chosen_path=input("Enter the path of the file you want to open: " )
        if system_name=="Windows":
            try:
                os.startfile(chosen_path)
            except FileNotFoundError:
                print("File not found!!")
        elif system_name=="Linux":
            try:
                subprocess.call(["xdg-open",chosen_path])
            except FileNotFoundError:
                print("File Not Found!")
        elif system_name=="Darwin":  # MAC OS
            try:
                subprocess.call(["open",chosen_path])
            except FileNotFoundError:
                print("File Not Found!")
    else:
        pass

# MAIN FUNCTION 
def main():
    # SEARCHED FILE
    target_file=search()
    
    # DETERMINING THE PLATFORM 
    if system_name=="Windows":
        path=fr"C:/"
    elif system_name=="Linux":
        path=fr"/"
    elif system_name=="Darwin": # MAC OS
        path=fr"/"
    
    # FOR ANIMATION 
    print("\033[?25l", flush=True)
    for i in range(1,20):
        dots="." * (i%4)
        print(f"\r[+] searching file{dots}   ",end="",flush=True)
        time.sleep(0.3)
    print("\033[?25h", flush=True)
    
    # CHECKS IF THE TARGET FILE IS PATH OR A FILE
    if '/' in target_file or '\\' in target_file:
        c=0
        if os.path.exists(target_file):
            c+=1
            if os.path.isfile(target_file):
                print(f"├──{highlighted(target_file,target_file)}")
                print(f"{c} file found")  
                open_file() 
            else:
                print("Searched input is a not a file")
    else:
        
        try:
            result,count=check_file(path,target_file)
        
            print(f"{count} files found")
            
            if result:
                open_file()
            else:
                print("Search item not found")
        except KeyboardInterrupt:
            open_file()
            # print("Stopped by the user!")
        
if __name__=="__main__":
    main()
