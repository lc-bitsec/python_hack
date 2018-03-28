import sys
import socket
import threading

#接收连接并开启proxy_handler函数来处理连接
def server_loop(local_host,local_port,remote_host,remote_port,receive_first):
    server = socket.socket(socket.AF_INET,socket.SOCK_STREAM)

    try:
        server.bind(local_host,local_port)
    except:
        print "[!!] Failed to listen on %s:%d" % (local_host,local_port)
        print "[!!] Check for other listening sockets or correct permissions"
        sys.exit(0)

    print "[*] Listening on %s:%d" % (local_host,local_port)

    server.listen(5)

    while True:
        client_socket, addr = server.accept()
        print "[==>] Received incoming connection from %s:%d" % (addr[0],addr[1])

        #开启一个线程与远程主机通信
        proxy_thread = threading.Thread(target=proxy_handler,args=(client_socket,remote_host,remote_port,receive_first))
        proxy_thread.start()


def proxy_handler(client_socket,remote_host,remote_port,receive_first):

    #连接远程主机
    remote_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    remote_socket.connect((remote_host,remote_port))

    #如果必要从远程主机收取数据
    if receive_first:
        remote_buffer = receive_from(remote_socket)
        hexdump(remote_buffer)

        #发送给我们的响应处理
        remote_buffer = response_handler(remote_buffer)

        #如果我们有数据传递给本地客户端，发送它
        if len(remote_buffer):
            print "[<==] Sending %d bytes to localhost." % len(remote_buffer)
            client_socket.send(remote_buffer)
        #现在循环从本地读取数据，发送给远程主机和本地主机
        while True:
            #从本地读取数据
            local_buffer = receive_from(client_socket)

            if len(local_buffer):

                print "[==>] Received %d bytes from localhost." % len(local_buffer)
                hexdump(local_buffer)

            #发送给本地请求
            local_buffer = request_handler(local_buffer)

def main():
    if len(sys.argv[1:]) != 5:
        print "Usage: ./"+ sys.argv[0]+" [localhost] [localport] [remotehost] [remoteport] [receive_first]"
        print "Example: ./"+sys.argv[0]+" 127.0.0.1 9000 10.12.132.1 9000 True"
        sys.exit(0)

    #设置本地监听参数
    local_host = sys.argv[1]
    local_port = int(sys.argv[2])

    #设置远程目标
    remote_host = sys.argv[3]
    remote_port = int(sys.argv[4])

    #告诉代理在发送给远程主机之前连接和接受数据
    receive_first = sys.argv[5]

    if "True" in receive_first:
        receive_first = True
    else:
        receive_first = False

    #现在设置好监听socket
    server_loop(local_host,local_port,remote_host,remote_port,receive_first)


#执行
main()

