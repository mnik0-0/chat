import socket
import pickle
import select


def users(client):
    for i in clients:
        client.send_data(f"{clients[i].name} {clients[i].address[1]}")


COMMANDS = {"/users": users, }



class Client:
    def __init__(self, socket_, address):
        self.socket_ = socket_
        self.address = address
        self.name = self.get_data()

    def get_data(self):
        try:
            len_message = int(self.socket_.recv(HEADER_SIZE).decode("utf-8"))
            data = self.socket_.recv(len_message)
            data = pickle.loads(data)
            return data
        except:
            return False

    def send_data(self, data):
        data = pickle.dumps(data)
        data = bytes(f"{len(data):<{HEADER_SIZE}}", "utf-8") + data
        self.socket_.send(data)

    def send_to_all_except_self(self, data):
        for socket_ in sockets_list:
            if client.socket_ != socket_ and socket_ != s_socket:
                client_to = clients[socket_]
                client_to.send_data(data)


HEADER_SIZE = 10

s_socket = socket.socket()

s_socket.bind((socket.gethostname(), 9091))

s_socket.listen(5)

sockets_list = [s_socket]
clients = {}


while True:
    read_sockets, _, _ = select.select(sockets_list, [], [])
    for n_socket in read_sockets:
        if n_socket == s_socket:
            c_socket, c_address = s_socket.accept()
            client = Client(c_socket, c_address)

            if client.name is False:
                continue

            sockets_list.append(client.socket_)

            clients[client.socket_] = client
            print(f"Новый клиент подключился {client.address}, имя {client.name}")
            client.send_to_all_except_self(f"{client.name} присоединился к чату")
        else:
            client = clients[n_socket]
            data = client.get_data()
            if data is False:
                print(f"Клиент {client.name} отключился")
                client.send_to_all_except_self(f"{client.name} вышел из чата")
                sockets_list.remove(client.socket_)
                del clients[client.socket_]
                continue
            if data in COMMANDS:
                COMMANDS[data](client)
            else:
                client.send_to_all_except_self(f"{client.name} [{client.address[1]}] > {data}")

