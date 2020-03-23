import socket
import pickle
import select


def users(client, clients):
    for i in clients:
        client.send_data(f"{clients[i].name} {clients[i].address[1]}")


COMMANDS = {"/users": users, }


class Room:

    def __init__(self, name, sockets_list, clients):
        self.name = name
        self.sockets_list = sockets_list
        self.clients = clients

    def update(self, new_sockets, new_clients):
        self.sockets_list.append(new_sockets)
        self.clients.update(new_clients)

    def in_room(self, client):
        data = client.get_data()
        if data is False:
            print(f"Клиент {client.name} отключился")
            client.send_to_all_except_self(f"{client.name} вышел из чата", self.sockets_list)
            self.sockets_list.remove(client.socket_)
            self.clients.pop(client.name)
            return False
        if data in COMMANDS:
            COMMANDS[data](client, self.clients)
        else:
            client.send_to_all_except_self(f"{client.name} [{client.address[1]}] > {data}", self.sockets_list)
        return True


class Client:
    def __init__(self, socket_, address):
        self.socket_ = socket_
        self.address = address
        self.name = self.get_data()
        self.room = self.get_data()

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

    def send_to_all_except_self(self, data, sockets_list):
        for socket_ in sockets_list:
            if self.socket_ != socket_ and socket_ != s_socket:
                client_to = clients[socket_]
                client_to.send_data(data)


HEADER_SIZE = 10

s_socket = socket.socket()

s_socket.bind((socket.gethostname(), 9091))

s_socket.listen(5)

sockets_list = [s_socket]
clients = {}
rooms = {}

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
            print(f"Новый клиент подключился {client.address}, имя {client.name}, комната {client.room}")

            if client.room not in rooms:
                rooms[client.room] = Room(client.room, [s_socket, client.socket_], {client.name: client})
            else:
                rooms[client.room].update(client.socket_, {client.name: client})

        else:
            client = clients[n_socket]
            room = rooms[client.room]
            if not room.in_room(client):
                sockets_list.remove(client.socket_)
                clients.pop(client.socket_)
                if room.clients == {}:
                    rooms.pop(room.name)
