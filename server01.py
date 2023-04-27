import socket
server_addr = ('127.0.0.1', 12345) # Dirección IP
server_sock = socket.socket(family=socket.AF_INET,
                            type=socket.SOCK_STREAM)
server_sock.bind(server_addr) # Enlaza el puerto
server_sock.listen(1) # Espera por un cliente
while True:    
    conn, client_addr = server_sock.accept()
    client_message = conn.recv(1024).decode()
    print(client_message)
    conn.send(bytes(f"Hello client {client_addr}", 'UTF-8'))
    conn.close()