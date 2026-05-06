import os 
import re 
import argparse
import requests
import random 

# GETTING INPUT FROM THE USER THROUGH THE CLI 
# LIKE : python file_name.py -f/-u file_name/url -w/-s/-ip searched_value
def user_input():
    # parser=argparse.ArgumentParser(description="LOG ANALYZER TOOL")
    
    # parser.add_argument('-f','--file', help="Specify the path of the file you want to analyze")
    # parser.add_argument('-ip','--address',help="Specify the ip address to be searched")
    # parser.add_argument('-s','--string',type=str.lower,nargs="+",help="Specify the string to be searched")
    # parser.add_argument('-w','--word',help="Specify the letter to be searched")
    # parser.add_argument('-u','--url',help="Specify the url to be searched")
    
    # args=parser.parse_args()
    # return args.file,args.address,args.string,args.word,args.url
    searched_file = None
    searched_ip = None
    searched_string = None
    searched_url = None
    
    choice=int(input("Do you want to analyze data from a \nFile(1) or a URL(2):"))
    if choice==1:
        try:
            searched_file=input(r"Enter the path of the file you want to anaylze: ").strip().strip('"').strip("'")
            if os.path.exists(searched_file):
                new=int(input("What do you want to search\n[1] String\n[2] ip address\n>"))
                if new==1:
                    searched_string=input("Enter the string to be searched: ")
                elif new==2:
                    searched_ip=input("Enter the IP address you want to search for: ")
            else:
                print("Incorrect Path!")
        except Exception as e:
            print(f"Error -> {e}")
    elif choice==2:
        searched_url=input("Enter the URL: ")
        new=int(input("What do you want to search\n[1] String\n[2] ip address\n>:"))
        if new==1:
            searched_string=input("Enter the string to be searched: ")
        elif new==2:
            searched_ip=input("Enter the IP address you want to search for: ")
    else:
        print("Enter Valid Choice!")
    return searched_file,searched_ip,searched_string,searched_url
        
# SEARCH FOR THE SPECIFIED FILE AND WILL RETURN THE CONTENTS OF THE FILE AFTER READING IT 
def open_file(file_path):
    try:
        if os.path.exists(file_path):
            if os.path.isfile(file_path):
                with open(file_path, "r") as f: 
                    output=f.readlines()
                return output
            else:
                print("Specified Path doesn't contain a suitable file")
        else:
            print("File not found!")
    except FileNotFoundError:
        print("File not found!")

# CHECKS FOR THE INPUT TYPE AND THEN PROCESSES IT 
def load_content(source, source_type):
    if source_type=="file":
        return source 
    elif source_type=="url":
        # USER_AGENTS = [
        # # Desktop
        # "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
        # "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
        # "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        # "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
        # "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",

        # # Mobile
        # "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
        # "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
        # "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.80 Mobile Safari/537.36",
        # "Mozilla/5.0 (Linux; Android 11; Mi 9T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",

        # # Older / WAF-friendly
        # "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
        # "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:78.0) Gecko/20100101 Firefox/78.0",
        # "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
        # "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
    
        # ]
        # user_agent=random.choice(USER_AGENTS)
        # header={"User-agent":user_agent}
        header = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                          "AppleWebKit/537.36 (KHTML, like Gecko) "
                          "Chrome/120.0 Safari/537.36"
        }
        response=requests.get(source,headers=header,timeout=10)
        response.raise_for_status()
        return response.text.splitlines()
   
# HIGHLIGHTS THE SEARCHED TEXT FROM THE SOURCE INPUT 
def highlight_match(line, pattern):
    return re.sub(
        pattern,
        lambda m: f"\033[31m{m.group(0)}\033[0m",
        line,
        flags=re.IGNORECASE
    )


   
# THIS FUNCTION WILL EXTRACT DATA AS PER YOUR CHOICE
def data_extraction(source,source_type, searched_values):
    if not searched_values:
        print("Nothing to search for!")
        return 
    if isinstance(searched_values, str):
        searched_values = [searched_values]
        
        
    content=load_content(source,source_type)
    if not content:
        print("NO file/URL selected to search from ")
        return
        
    pattern=[re.escape(value) for value in searched_values]
    # pattern=re.escape(searched_values)
    combined_pattern = "|".join(pattern)

    found=False
    
    for line in content:
        if re.search(combined_pattern,line,re.IGNORECASE):
            highlighted = highlight_match(line.rstrip(), combined_pattern)
            print(highlighted)
            # print(line.strip())
            found=True
    if not found:
        print("Match not found!")



# pattern=r"\b(?:(?:25[0-5]|2[0-4]\d|1?\d?\d)\.){3}(?:25[0-5]|2[0-4]\d|1?\d?\d)\b"

# MAIN FUNCTION 
def main():
    searched_file,searched_address, searched_string,searched_url=user_input()
    
    searched_values=searched_address or searched_string
    
    if searched_file:
        file_output=open_file(searched_file)
        if file_output:
            data_extraction(file_output, "file",searched_values)
    
    elif searched_url:
        data_extraction(searched_url,"url", searched_values)
    
       
if __name__=="__main__":
    main()
