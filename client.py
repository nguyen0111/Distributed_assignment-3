import socket
import threading

PORT = 5555  

def receive_messages(sock):
    while True:
        try:
            msg = sock.recv(1024).decode()
            if not msg:
                print("Disconnected from server.")
                break
            print(msg)
        except:
            print("Disconnected from server.")
            break

def main():
    ip = input("Enter server IP: ")
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect((ip, PORT))  

    threading.Thread(target=receive_messages, args=(sock,), daemon=True).start()

    try:
        while True:
            msg = input()
            if msg.lower() == "/quit":
                sock.send("/quit".encode())
                break
            sock.send(msg.encode())
    except:
        pass
    finally:
        sock.close()

if __name__ == '__main__':
    main()