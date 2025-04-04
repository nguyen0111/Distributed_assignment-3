import socket
import threading

HOST = '0.0.0.0'
PORT = 5555

clients = {}  
channels = {}  

def handle_client(sock):
    try:
        sock.send("Enter your nickname:".encode())
        nickname = sock.recv(1024).decode().strip()
        while not nickname or nickname in [c['nickname'] for c in clients.values()]:
            sock.send("Invalid or taken nickname. Try again:".encode())
            nickname = sock.recv(1024).decode().strip()

        sock.send("Enter channel to join:".encode())
        channel = sock.recv(1024).decode().strip()
        while not channel:
            sock.send("Channel cannot be empty. Try again:".encode())
            channel = sock.recv(1024).decode().strip()

        clients[sock] = {'nickname': nickname, 'channel': channel}
        channels.setdefault(channel, []).append(sock)
        sock.send(f"Welcome {nickname}! Joined channel '{channel}'".encode())
        broadcast(f"{nickname} joined the channel.", channel, sock)

        while True:
            msg = sock.recv(1024).decode().strip()
            if not msg:
                break

            if msg.startswith("/pm"):
                parts = msg.split(" ", 2)
                if len(parts) == 3:
                    target, message = parts[1], parts[2]
                    send_private_message(sock, target, message)
                else:
                    sock.send("Usage: /pm <nickname> <message>".encode())
            elif msg == "/quit":
                break
            else:
                broadcast(f"{nickname}: {msg}", channel, sock)

    except Exception as e:
        print(f"Client error: {e}")
    finally:
        remove_client(sock)
        sock.close()

def broadcast(message, channel, sender=None):
    for client in channels.get(channel, []):
        if client != sender:
            try:
                client.send(message.encode())
            except:
                remove_client(client)

def send_private_message(sender_sock, target_nick, message):
    sender_info = clients.get(sender_sock)
    if not sender_info:
        return

    for sock, info in clients.items():
        if info['nickname'] == target_nick:
            try:
                sock.send(f"[PM from {sender_info['nickname']}]: {message}".encode())
                sender_sock.send(f"[PM to {target_nick}]: {message}".encode())
                return
            except:
                remove_client(sock)
    
    sender_sock.send(f"User '{target_nick}' not found.".encode())

def remove_client(sock):
    if sock in clients:
        info = clients[sock]
        channel = info['channel']
        if channel in channels and sock in channels[channel]:
            channels[channel].remove(sock)
            if not channels[channel]:
                del channels[channel]
        del clients[sock]
        broadcast(f"{info['nickname']} left the channel.", channel)

def main():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind((HOST, PORT))
    server.listen()
    print(f"Server running on {HOST}:{PORT}")

    while True:
        client_sock, _ = server.accept()
        threading.Thread(target=handle_client, args=(client_sock,)).start()

if __name__ == '__main__':
    main()