import socket
import pickle
import threading
import sys

HEADER_SIZE = 10
RUN = True


def stop():
    global RUN
    RUN = False


def help():
    print("Комманды")
    for i in COMMANDS:
        print(i)


def users():
    print("Список пользователей")
    send_data_to(c_socket, "/users")


COMMANDS = {"/help": help, "/exit": stop, "/users": users}


def send_data_to(to_socket, data):
    data = pickle.dumps(data)
    data = bytes(f"{len(data):<{HEADER_SIZE}}", "utf-8") + data
    to_socket.send(data)


def get_data():
    try:
        len_message = int(c_socket.recv(HEADER_SIZE).decode("utf-8"))
        data = c_socket.recv(len_message)
        data = pickle.loads(data)
        return data
    except:
        return False


def output_thread():
    while RUN:
        data = get_data()
        if data:
            print(data)


def input_thread():
    while RUN:
        data = input()
        if data in COMMANDS:
            COMMANDS[data]()
        else:
            send_data_to(c_socket, data)


while True:
    username = input("Введите имя, чтобы продолжить: ")
    if username != "":
        break
    print("Введите корректное имя")

c_socket = socket.socket()

c_socket.connect((socket.gethostname(), 9091))

c_socket.setblocking(False)

send_data_to(c_socket, username)
send_data_to(c_socket, False)


threading.Thread(target=output_thread).start()
threading.Thread(target=input_thread).start()

