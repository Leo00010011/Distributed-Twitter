import socket
# Localhost (pc local) en el puerto 12345
server_addr = ('127.0.0.1', 12345)
# Crea un socket TCP
client_sock = socket.socket(family=socket.AF_INET, type=socket.SOCK_STREAM)
# Establece una conexión con el servidor
client_sock.connect(server_addr)
# Envia un mensaje al servidor
client_sock.send(bytes(f"Hello Server {server_addr}!","utf-8"))
# Espera por un mensaje del servidor
message = client_sock.recv(1024).decode()
print(message)
# Cierra la conexión
client_sock.close()