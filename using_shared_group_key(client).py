from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import os 
import socket
import sys 
import threading 
import getpass
import argparse
import base64
import time 


# DEFAULT HOST AND PORT
# port=8080
# host="127.0.0.1"

stored_keys={}
session_keys={}

version=0
is_admin=False
stored_group_key={}

group_key=None
lock=threading.Lock()


# Parses command-line arguments to get the server IP address and port.
def connection():
    parser=argparse.ArgumentParser(description="CLIENT")
    parser.add_argument('-t',dest="target",default="127.0.0.1",help="specify the ip address")
    parser.add_argument('-p',dest="port",type=int,default=8080,help="specify the port number")
    
    args=parser.parse_args()
    
    return args.target,args.port

# Sends data over the socket with a 4-byte length prefix for proper framing.
def send_packet(client,packet):
    length=len(packet)
    if length>10000:
        raise ValueError("Packet too large!")
    client.sendall(length.to_bytes(4,'big') + packet)

# Receives exactly n bytes from the socket, ensuring complete packet reads.
def recv_exact(client,n):
    data=b""
    while len(data)<n:
        chunk=client.recv(n-len(data))
        if not chunk: 
            return None
        data+=chunk 
    return data

# Handles username-password authentication with the server and returns login status.
def authentication(client):
    try:
        # USERNAME
        sv_user=client.recv(1024).decode('utf-8')
        print(sv_user,end="")
        username=input()
        client.send(username.encode('utf-8'))
        # PASSWORD
        sv_password=client.recv(1024).decode('utf-8')
        password=getpass.getpass("password: ")
        # print()
        client.send(password.encode('utf-8'))
        # SERVER APPROVAL OR NOT 
        response=client.recv(1024).decode('utf-8')
        if response=="OK":
            return username,True
        else:
            return username, False
    except Exception as e:
        print(f"{e}")
        client.close()
        
# Processes incoming public keys, derives per-user session keys using ECDH, and stores them securely.
def receive_keys(client,client_private_key,data,my_username):
    global is_admin
    try:
        if not data.startswith(b"KEY|"):
            return 
        
        # if b'|' not in data:
        #     return 
        
        parts=data.split(b'|',2)
        if len(parts) != 3:
            return
        _, username, key_bytes = parts
        
    
        public_key = serialization.load_pem_public_key(key_bytes)
        
        user=username.decode('utf-8')
        
        if user==my_username:
            return 
        with lock:
            if user in session_keys:
                return 
            stored_keys[user] = public_key
        
        shared_secret=client_private_key.exchange(ec.ECDH(),public_key)
        
        derived_key=HKDF(
            algorithm=hashes.SHA256(),
            length=32,
            salt=b'hello secure world',
            info=b'handshake'
        ).derive(shared_secret)
        with lock:
            
            session_keys[user]=derived_key
        
        if is_admin:
            print("[+] New user joined → regenerating group key")
            generate_group_key(client, my_username)

    except Exception as e:
        print(f"Error--> {e}")

# Creates a new group key, encrypts it per user using session keys, and distributes it securely.
def generate_group_key(client,sender):
    global version,group_key
    version+=1
    
    group_key=os.urandom(32)
    
    stored_group_key[version]=group_key
    with lock:
        if not session_keys:
            return 
        users=list(session_keys.keys())
    for user in users:
        if user==sender:
            continue
        try:  
            aesgcm=AESGCM(session_keys[user])
            nonce=os.urandom(12)
            encrypted_group_key=aesgcm.encrypt(nonce,group_key,None)
            packet=b"|".join([
                b"GROUP_KEY",
                sender.encode('utf-8'),
                user.encode('utf-8'),
                str(version).encode('utf-8'),
                base64.b64encode(nonce),
                base64.b64encode(encrypted_group_key), 
            ])
            send_packet(client,packet)
        except Exception as e:
            print(f"Error --> {e}")

# Decrypts and stores the shared group key sent securely for this client using its session key.
def receive_group_key(username,data):
    try:
        if not data.startswith(b'GROUP_KEY'):
            return 
        _,sender,receiver,version,nonce,encrypted_group_key=data.split(b'|',5)
        
        sender = sender.decode('utf-8')
        receiver = receiver.decode('utf-8')
        version = int(version.decode('utf-8'))
        
        if receiver!=username:
            return 
        with lock:
            if sender not in session_keys:
                print("[!] Missing session key for sender")
                return 
        if version in stored_group_key:
            return 
        
        nonce = base64.b64decode(nonce)
        encrypted_group_key = base64.b64decode(encrypted_group_key)
    
    
        aesgcm=AESGCM(session_keys[sender])
        decrypted_group_key=aesgcm.decrypt(nonce,encrypted_group_key,None)
        stored_group_key[version]=decrypted_group_key
        
            
    except Exception as e:
        print(f"Error--> {e}")
            
# ECDH KEY GENERATOR
def key_generator():
    client_private_key=ec.generate_private_key(ec.SECP256R1())
    public_key=client_private_key.public_key()

    client_public_key_bytes=public_key.public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    )
    
    return client_private_key,client_public_key_bytes

# Encrypts user messages using the group key and sends them to the server.
def message_sender(client,username):
    while True:
        try:
            message=input("You:")
            if message.lower()=="disconnect":
                client.close()
                sys.exit(0)
            if version not in stored_group_key:
                print("[!] Waiting for group key...")
                continue
            aesgcm=AESGCM(stored_group_key[version])
            nonce=os.urandom(12)
            ciphertext=aesgcm.encrypt(nonce,message.encode('utf-8'),None)
            
            packet=b"|".join([
                b"MSG",
                username.encode('utf-8'),
                str(version).encode('utf-8'),
                base64.b64encode(nonce),
                base64.b64encode(ciphertext)
            ])
            send_packet(client,packet)
        except Exception as e:
            print(f"Error-> {e}")
            break
        
# Decrypts incoming messages using the group key and displays them.           
def receive_messages(data):
    try:
        if not data.startswith(b'MSG|'):
            return 
        _,sender,version,nonce,ciphertext=data.split(b'|',4)
        
        sender=sender.decode('utf-8')
        version=int(version.decode('utf-8'))
        
        if version not in stored_group_key:
            print("[!] Missing key, skipping message")
            return 
            
        nonce = base64.b64decode(nonce)
        ciphertext=base64.b64decode(ciphertext)
        aesgcm=AESGCM(stored_group_key[version])
        
        decrypted_message=aesgcm.decrypt(nonce,ciphertext,None)
  
        sys.stdout.write("\r" + " " * 80 + "\r")
        # Reprint prompt
        print(f"{sender}: {decrypted_message.decode('utf-8')}", end="", flush=True)
        print("You: ",end="",flush=True)
    except Exception as e:
        print(f"Error--> {e}")
        return 
      
# Continuously receives framed packets and routes them to appropriate handlers.  
def receive_loop(client,client_private_key,username):
    global is_admin
    while True:
        try:
            length_bytes=recv_exact(client,4)
            if not length_bytes:
                break 
            length=int.from_bytes(length_bytes,"big")
            
            if length>10000:
                print("[!] Packet too large")
                break
            data=recv_exact(client,length)
            if not data:
                break
            
            if data.startswith(b'MSG|'):
                receive_messages(data)
            elif data.startswith(b'KEY|'):
                receive_keys(client,client_private_key,data,username)
            elif data.startswith(b'GROUP_KEY|'):
                receive_group_key(username,data)
            elif data.startswith(b'ROLE|'):
                _, role = data.split(b'|', 1)
                role = role.decode('utf-8')

                if role == "admin" and not is_admin:
                    is_admin = True
                    # print("[+] You are the admin")
                    while len(session_keys) < 1:
                        time.sleep(0.5)
                    time.sleep(1)
                    generate_group_key(client,username)
            else:
                print("invalid format")
        except Exception as e:
            print(f"Error --> {e}")

# Initializes the client, performs authentication, key exchange, and starts communication threads.  
def main():
    
    host,port=connection()
    
    client_private_key,client_public_key_bytes=key_generator()
    
    client=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    client.connect((host,port))
    
    
    
    username,response=authentication(client)
    
    try:
        if response:
            send_packet(client,b"KEY|" + username.encode('utf-8') + b'|' + client_public_key_bytes)
            # server_public_key_bytes=client.recv(4096)
            # server_public_key=serialization.load_pem_public_key(server_public_key_bytes)


            threading.Thread(target=receive_loop,args=(client,client_private_key,username),daemon=True).start()
            threading.Thread(target=message_sender, args=(client, username), daemon=True).start()
        else:
            print(f"Incorrect password!")
            client.close()
    except Exception as e:
        print(f"Error--> {e}")
    
        
if __name__ == "__main__":
    main()        
    