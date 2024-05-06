#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Tue Apr 30 00:06:50 2024

@author: riccardobalzani
0001090902
"""


import socket
import threading 
import sys
import time


MAX_ATTEMPTS = 3
DELAY = 0.1

# Chiusura connessione con il server ed uscita dal programma
def close_connection(client_socket):
    print("Disconnected...")
    client_socket.close()
    sys.exit()
    
# Attesa tra tentativi
def wait():
    print("New attempt...")
    time.delay(DELAY)

# Ricezione messaggi dal server
def receive_messages(client_socket):
    try:
        while True:
            message = client_socket.recv(1024).decode()
            if message:
                print("\n")
                print(message)
                print("\n")
            else:
                break
    except Exception as e:
        print("Error receiving message:", e)    # Chiusura connessione in caso di errore di ricezione
        client_socket.close()
        
# Invio dei messaggi
def send_messages(client_socket):
    # Ciclo per inviare messaggi al server
    while True:
        message = input("\n")
        
        if message == 'exit':
            close_connection(client_socket)
            
        else:
            attempts_sending_message = 1
            while attempts_sending_message <= MAX_ATTEMPTS:  # Aggiunto il controllo del numero massimo di tentativi
                try: 
                    client_socket.send(message.encode())
                    break  # Esci dal ciclo while se l'invio è riuscito
                except BrokenPipeError as b:
                    print("Server disconnected: ", b)
                    close_connection(client_socket)
                except Exception as e:
                    print("Exception: ", e)
                    if attempts_sending_message >= MAX_ATTEMPTS:
                        print("Max attempts reached...")
                        close_connection(client_socket)
                    else:
                        attempts_sending_message += 1  # Incrementa il numero di tentativi
                        wait()



# main function
def main():
    # Indirizzo e porta del server
    server_address = ('localhost', 8080)

    # Creazione del socket TCP/IP
    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    connection_attempts = 1
   
    while True:
        try:
            # Connessione al server
            client_socket.connect(server_address)
            print("Connected to server.")
    
            # Thread per ricevere messaggi dal server
            threading.Thread(target=receive_messages, args=(client_socket,)).start()
            
            print("\n\t---Enter message to send (or type 'exit' to quit)---") # Istruzioni di utilizzo
            
            send_messages(client_socket)
            
            
        except ConnectionRefusedError:
            print("Server is full. Connection rejected.")
            if connection_attempts >= 3:
                print("Max attempts reached...")
                close_connection(client_socket)
            else: 
                connection_attempts = connection_attempts + 1    
                wait()
                
        except Exception as e:
            print("Error:", e)
            close_connection(client_socket)
            
        finally:
            close_connection(client_socket) # Chiusura della connessione

if __name__ == "__main__":
    main()

