import socket
import ssl
import time
import threading


class IrcBewt():

    def __init__(self, server, port, use_ssl, cmd_prefix, nickname, altnickname, user, realname, channels, quitmsg, callback):
        self.server = server
        self.port = port
        self.use_ssl = True if use_ssl == 'True' else False
        self.nickname = nickname
        self.altnickname = altnickname
        self.user = user
        self.realname = realname
        self.channels = channels
        self.quitmsg = quitmsg
        self.callback = callback

        self.cmd_prefix = f':{cmd_prefix}'

        self.is_connected = False
        self.thread_is_started = False

        self.lastrecv = int(time.time())

    def connect(self):
        self.socket = socket.socket()
        try:
            self.socket.connect((self.server, self.port))
            if self.use_ssl:
                self.socket = ssl.wrap_socket(self.socket)
        except (OSError, TimeoutError, socket.herror, socket.gaierror) as e:
            print(f'[!] {self.server}:{self.port} (ssl:{str(self.use_ssl)}) - FAILED: {e}')
        else:
            print(f'[+] Connected to {self.server}:{self.port}')
            self.send(f'NICK {self.nickname}')
            self.send(f'USER {self.user} 0 * :{self.realname}')

            if not self.thread_is_started:
                t = threading.Thread(target=self._check_lastrecv, daemon=True).start()
                self.thread_is_started = True
    
    def die(self):
        if self.socket:
            self.send(f'QUIT :{self.quitmsg}')
            self.socket.shutdown(2)
            self.socket.close()
            self.socket = None
            self.is_connected = False

    def main(self):
        buff = b''
        
        while True:

            buff += self.socket.recv(1024)

            while b'\r\n' in buff:
                line, buff = buff.split(b'\r\n', 1)

                self.lastrecv = int(time.time())
                
                try:
                    line = line.decode('utf-8')
                except UnicodeDecodeError:
                    line = line.decode('iso-8859-1')

                print(f'<== {line}')

                split = line.split(' ')

                if split[0] == 'PING':
                    self.send(f"PONG {split[1].split(':')[1]}")

                if split[1] == '376' or split[1] == '422':
                    self.is_connected = True
                    for c in self.channels:
                        self.send(f'JOIN {c}')
                
                if split[1] == '433':
                    self.send(f'NICK {self.altnickname}')

                if split[1] == 'PRIVMSG':
                    if split[2] != self.nickname:
                        channel = split[2]
                        if len(split) >= 5 and split[3] == self.cmd_prefix:
                            t = threading.Thread(target=self.callback, args=(channel, split[3:]), daemon=True).start()

    def _check_lastrecv(self, sleeptime=60):
        while True:
            time_ago = int(time.time()) - self.lastrecv
            if time_ago > 1800:
                print(f'[!] last recv was {time_ago} seconds ago..')
                print(f'[!] Reconnecting..')
                self.die()
                self.connect()

            time.sleep(sleeptime)

    def send(self, data):
        try:
            self.socket.send(data.encode('utf-8') + b'\r\n')
            print(f'==> {data}')
        except (OSError, socket.herror, socket.gaierror) as e:
            print(f'[FAIL] ==> {data}')