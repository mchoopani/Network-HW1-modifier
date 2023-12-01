import socket
import select
from collections import Counter

tcp_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
tcp_socket.bind(('0.0.0.0', 10001))
tcp_socket.listen(4)
tcp_socket.setblocking(False)

udp_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
udp_socket.bind(('0.0.0.0', 10001))
udp_socket.setblocking(False)

inputs = [tcp_socket, udp_socket]
outputs = []
output_queue = {}


def transform_udp_input(data: bytes):
    str_data = data.decode('utf-8')
    transformed = str_data[::-1].upper()
    frequency = Counter(transformed)

    return (transformed + ', ' + max(frequency, key=frequency.get)).encode('utf-8')


magic_table = {
    'a': 0, 'b': 0,
    'c': 1, 'd': 1,
    'e': 2, 'f': 2,
    'g': 3, 'h': 3,
    'i': 4, 'j': 4,
    'k': 5, 'l': 5,
    'm': 6, 'n': 6,
    'o': 7, 'p': 7,
    'q': 8, 'r': 8,
    's': 9, 't': 9,
    'u': 10, 'v': 10,
    'w': 11, 'x': 11,
    'y': 12, 'z': 12,
}


def magic_number(c: str):
    return magic_table.get(c, c)


def transform_tcp_input(data: bytes):
    str_data = data.decode('utf-8').lower()

    output = ""
    for c in str_data:
        output += str(magic_number(c))

    frequency = Counter(str_data)
    min_freq = min(frequency.values())
    max_magic = -1

    for char, freq in frequency.items():
        if freq != min_freq:
            continue
        magic = magic_number(char)
        if isinstance(magic, str):
            continue
        max_magic = max(magic, max_magic)

    return (output + ', ' + str(max_magic)).encode('utf-8')


def get_inputs():
    while inputs:
        readable, writable, exceptional = select.select(inputs, outputs, inputs + outputs)

        for r in readable:
            if r is tcp_socket:
                client, _ = tcp_socket.accept()
                client.setblocking(False)
                inputs.append(client)
            elif r is udp_socket:
                udp_input, addr = udp_socket.recvfrom(2048)
                if udp_input and udp_input.decode('utf-8') != "exit server":
                    udp_socket.sendto(transform_udp_input(udp_input), addr)
            else:
                tcp_input = r.recv(2048)
                if tcp_input and tcp_input.decode('utf-8') != 'exit server':
                    output_queue[r] = transform_tcp_input(tcp_input)
                    outputs.append(r)
                else:
                    r.close()
                    if r in outputs:
                        outputs.remove(r)
                    if r in inputs:
                        inputs.remove(r)

        for w in writable:
            if w in output_queue:
                w.send(output_queue[w])
                outputs.remove(w)
                del output_queue[w]
            else:
                outputs.remove(w)

        for e in exceptional:
            if e in inputs:
                inputs.remove(e)
            if e in outputs:
                outputs.remove(e)
            e.close()

            del output_queue[e]


if __name__ == '__main__':
    try:
        get_inputs()
    except Exception as e:
        print(e)
    finally:
        tcp_socket.close()
        udp_socket.close()
