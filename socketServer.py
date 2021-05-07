# coding=utf-8
import socket
import select
import sys
import ssl

#生成证书
#openssl req -new -x509 -days 365 -nodes -out cert.pem -keyout key.pem

class Proxy:
    def __init__(self, listen_addr, to_addr):
        '''
        :param listen_addr: 本地监听地址
        :param to_addr: 转发地址
        '''
        self.proxy = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.proxy.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.proxy.bind(listen_addr)
        self.proxy.listen(10)
        self.inputs = [self.proxy]
        self.route = {}
        self.to_addr = to_addr

    def serve_forever(self):
        print('proxy listen...')
        while 1:
            readable, _, _ = select.select(self.inputs, [], [])
            for self.sock in readable:
                if self.sock == self.proxy:
                    self.on_join()
                else:
                    data = self.sock.recv(8096)
                    if not data:
                        self.on_quit()
                    else:
                        self.route[self.sock].send(data)

    def on_join(self):
        newsocket, addr = self.proxy.accept()
        client = ssl.wrap_socket(newsocket, "key.pem", "cert.pem", server_side=True, ssl_version=ssl.PROTOCOL_TLSv1)
        print(addr, 'connect')
        forward = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        forward.connect(self.to_addr)
        self.inputs += [client, forward]
        self.route[client] = forward
        self.route[forward] = client
    def on_quit(self):
        for s in self.sock, self.route[self.sock]:
            self.inputs.remove(s)
            del self.route[s]
            s.close()


if __name__ == '__main__':
    try:
        Proxy(('0.0.0.0', 3308),('127.0.0.1', 3307)).serve_forever()  # 代理服务器监听的地址
    except KeyboardInterrupt:
        sys.exit(1)

