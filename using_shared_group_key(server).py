from cryptography.hazmat.primitives.asymmetric import ec
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.ciphers.aead import AESGCM
from cryptography.hazmat.primitives.kdf.hkdf import HKDF
import os 
import socket
import threading

port=8080
host="127.0.0.1"

users={}
clients=[]

stored_keys={}
session_keys={}

password="new world"

lock=threading.lock()

 
def authentication(conn,addr):
    try:   
        global password
        conn.send("Enter your username: ".encode('utf-8'))
        username=conn.recv(1024).decode('utf-8')
        
        conn.send("Password: ".encode('utf-8'))
        entered_password=conn.recv(1024).decode('utf-8')
        if entered_password==password:
            conn.send("OK".encode('utf-8'))
            print(f"{username} joined the chat")
            return username
        else:
            print("Incorrect Password!")
            print(f"{username} tried to join but couldn't connect")
            conn.close()
            return username
    except Exception as e:
        print(f"{e}")
        conn.close()

def send_packet(conn, packet):
    length = len(packet).to_bytes(4, 'big')
    conn.sendall(length + packet)

def broadcast_keys(user,public_key_bytes):
    for client in clients[:]:
        try:
            packet = b"KEY|" + user.encode('utf-8') + b"|" + public_key_bytes + b'||END||'
            client.sendall(packet)
        except:
            clients.remove(client)
  
  
  
def recv_exact(conn,n):
    data=b''
    while len(data)<n:
        chunk=conn.recv(n-len(data)) 
        if not chunk:
            return None
        data+=chunk         
    return data

def receive_packet(conn,packet):
    length=
    data=b''
    while 
            

def send_client_public_keys(conn,addr):
    for peer_user,key in stored_keys.items():
        packet=b'KEY|' + peer_user.encode('utf-8') + b'|' + key.public_bytes(
            encoding=serialization.Encoding.PEM,
            format=serialization.PublicFormat.SubjectPublicKeyInfo
        ) + b'||END||'
        conn.sendall(packet)
    
 
def handle_client(conn,addr,user,public_key_bytes,aesgcm):
    try:    
        clients.append(conn)
        users[user]=conn
        broadcast_keys(user,public_key_bytes)
        while True:
            try :
                message=conn.recv(1024)
                if not message:
                    break
                if message.decode().lower()=="disconnect":
                    print(f"Connection with {user} ended!")
                    conn.close()
                    clients.remove(conn)
                    break
            except:
                print(f"Connection with {user} ended!")
                if conn in clients:
                    clients.remove(conn)
                    conn.close()
                    break
                
    except Exception as e:
        print(f"{e}")
        conn.close()


def main():
    global host,port
    # server_private_key,server_public_key_bytes=key_generator()
    sv=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    sv.bind((host,port))
    sv.listen(3)
    while True:
        try:
            conn,addr=sv.accept()
            # AUTHENTICATION 
            user=authentication(conn,addr)
            
            client_public_key_bytes=conn.recv(4096)
            client_public_key=serialization.load_pem_public_key(client_public_key_bytes)
            
            stored_keys[user]=client_public_key
            threading.Thread(target=send_client_public_keys, args=(conn,addr),daemon=True).start()
            
            threading.Thread(target=handle_client,args=(conn,addr,user),daemon=True).start()
            


        except Exception as e:
            print(f"server error--> {e}")
            conn.close()
        
if __name__ == "__main__":
    main()        