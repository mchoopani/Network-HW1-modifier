import socket
import sys

tcp_socket: socket.socket = None
udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
host_addr = ('127.0.0.1', 10001)


def init_tcp():
    global tcp_socket
    tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp_socket.connect(host_addr)


def tcp_out():
    global tcp_socket
    if not tcp_socket:
        init_tcp()
    output = input("enter your sentence to transform: ")
    if output == 'exit':
        exit_server()
    tcp_socket.send(output.encode('utf-8'))
    print(tcp_socket.recv(2048).decode('utf-8'))


def exit_server():
    global tcp_socket
    if not tcp_socket:
        init_tcp()
    tcp_socket.send(b'exit server')
    tcp_socket.close()
    udp_socket.sendto(b'exit server', host_addr)
    udp_socket.close()

    sys.exit(0)


def udp_out():
    global udp_socket
    output = input("enter your sentence to transform: ")
    if output == 'exit':
        exit_server()
    udp_socket.sendto(output.encode('utf-8'), host_addr)
    print(udp_socket.recv(2048).decode('utf-8'))


if __name__ == '__main__':
    while True:
        conn_type = input("udp or tcp? ")
        if conn_type == 'tcp':
            tcp_out()
        elif conn_type == 'udp':
            udp_out()
        elif conn_type == 'exit':
            exit_server()
