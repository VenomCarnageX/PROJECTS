import requests
import argparse
import random 


#USER INPUT THROUGH CLI SPECIFYING THE PATH OF THE WORDLIST AND TARGET DOMAIN/URL
# EX: python name_of_the_file -t target_url/domain -w path_of_the_wordlist 
def getting_input():
    parser=argparse.ArgumentParser(description="Tool for directory brute forcing")
    parser.add_argument("-t", dest="target", required=True, help="specify the domain/target")
    parser.add_argument("-w", dest="wordlists_path", required=True, help="specify for path of the wordlist")
    args=parser.parse_args()
    
    return args.target,args.wordlists_path


# READS THE WORDLISTS FROM THE SPECIFIED PATH 
def word_list(path):
    with open(f"{path}","r",encoding='utf-8') as f:
        return f.read().splitlines()
 
 
 
#BRUTE FORCES THE DIRECTORY IN THE TARGET URL/DOMAIN
def brute_force(url,wordlists):
    print("TRYING; ")
    # RANDOM USER AGENTS
    USER_AGENTS = [
    # Desktop
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:122.0) Gecko/20100101 Firefox/122.0",
    "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
    "Mozilla/5.0 (X11; Linux x86_64; rv:115.0) Gecko/20100101 Firefox/115.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_5) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Safari/605.1.15",

    # Mobile
    "Mozilla/5.0 (iPhone; CPU iPhone OS 17_2 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1",
    "Mozilla/5.0 (Linux; Android 14; Pixel 7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 12; SM-G991B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/118.0.5993.80 Mobile Safari/537.36",
    "Mozilla/5.0 (Linux; Android 11; Mi 9T) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Mobile Safari/537.36",

    # Older / WAF-friendly
    "Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36",
    "Mozilla/5.0 (Windows NT 6.1; WOW64; rv:78.0) Gecko/20100101 Firefox/78.0",
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36",
    "Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:102.0) Gecko/20100101 Firefox/102.0",
   
    ]
    for word in wordlists:
        user_agent=random.choice(USER_AGENTS)
        header={"User-agent":user_agent}
        target=f"{url}/{word}"
        try:
            
            r=requests.get(target,headers=header,timeout=5)
            
            if r.status_code in [200,301,302,403]:
                print(f"/{word} -------> {r.status_code}")
            else:
                pass
        except requests.RequestException:
            pass           
        
#MAIN FUNCTION WHICH WILL RUN ALL THE FUNCTIONS
def main():
    url,wordlist_path=getting_input()
    words=word_list(wordlist_path)
    brute_force(url, words)

if __name__=="__main__":
    main()
