#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 00:06:50 2024

@author: riccardobalzani
"""


import socket
import threading
import time
import sys


MAX_ATTEMPTS = 3
DELAY = 0.1
BACKLOG = 5

# Gestione dei client
clientList = []
clientListLock = threading.Lock()

# Rimuove il client
def remove_client(client):
    client.close()
    clientList.remove(client)
    print("Client removed: ", client.peer())

# Invia il messaggio a tutti i client connessi
def send_to_all_clients(message, peer):
    message = peer + ": " + message
    
    # Accesso in mutua esclusione alla lista dei client
    with clientListLock:
        for client in clientList:
            
            if client.fileno() != -1:  # Verifica se la connessione è ancora attiva
                attempts = 0
                send = True
                
                while attempts < MAX_ATTEMPTS and send:
                    attempts = attempts + 1
                    
                    try:
                        client.send(message.encode())
                        print("Message sent succesfully to: ", client.getpeername())
                        send = False
                        
                    except BrokenPipeError as b:
                        print("Client disconnected: ", b)
                        remove_client(client)   # Se il client non è connesso rimuove il client
                        
                    except Exception as e:
                        print("Error sending message to client: ", e)
                        time.sleep(DELAY)   # Dopo un DELAY si ritenta la connessione
                        
                        if attempts == MAX_ATTEMPTS:    # Dopo tre tentativi falliti il client è rimosso
                            remove_client(client)
                            
            else:   
                print("Client closed the connection.")
                remove_client(client)   # Se la connessione non è attiva rimuove il client
                      
# Gestione del client
def handle_client(connectionSocket):
    while True:
        try:
            message = connectionSocket.recv(1024).decode() # Dimensione massima messaggio 1 Kb
            peer = str(connectionSocket.getpeername()) 
            print(peer + ": " + message)
        
            send_to_all_clients(message, peer) # Il messaggio è inviato a tutti i client
            
        except Exception as e:
            print("Exception: ", e)
            
            with clientListLock:
                remove_client(connectionSocket) # Rimozione client dopo eccezione nella ricezione di messaggi
            break
            
# Chiude le connessioni con i client
def close_connections():
    with clientListLock:
        for client in clientList:
            remove_client(client)
        
        print("All client removed...")
        

# Chiusura del server
def close_server(serverSocket):
    while True:
        message = input("\n")
        
        if message == 'close':
            serverSocket.close()

            close_connections()
            print("Server has been closed...")
            sys.exit()
        
# main function      
def main():
    # Inizializzazione socket del server
    serverSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # Creazione socket
    serverSocket.bind(('localhost', 8080)) # Associone IP e porta
    serverSocket.listen(BACKLOG) # Coda di Backlog a 5 client
    
    threading.Thread(target=close_server, args=(serverSocket, )).start()    # Thread per chiudere la connessione 
    
    print("Server created...")
    print("---Type 'close' to brutally close the server---")
    
    while True:
        print("Waiting for connections...")
        connectionSocket, addr = serverSocket.accept()
        
        with clientListLock:    
            clientList.append(connectionSocket) # Client aggiunto alla clientList
             
        threading.Thread(target=handle_client, args=(connectionSocket, )).start()   # Associazione di un thread al client
        
        print("Connected: ", addr)
    
if __name__ == "__main__":
    main()