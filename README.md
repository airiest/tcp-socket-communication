# TCP socket client and server
PythonによるTCPソケット通信のサンプルです。  
実装に組み込むには、

- host : サーバアドレス
- port : サーバのポート番号
- send_q: 送信用キュー
- recv_q: 受信用キュー

とし、サーバサイドでは、

```
host = 'localhost'
port = 5000
    
send_q = queue.Queue()
recv_q = queue.Queue()

tcp_server = TcpSocketServer(host, port, send_q, recv_q)
```

クライアントサイドでは、

```
host = 'localhost'
port = 5000
    
send_q = queue.Queue()
recv_q = queue.Queue()

tcp_client = TcpSocketClient(host, port, send_q, recv_q)
```

と起動します。  
データの送受信はそれぞれのキューを通して行います。

## サンプルアプリケーション実行
キーボード入力した文字列をクライアントサーバ間で送受信するアプリケーションを実行します。

サーバ起動

```
$ python tcp_socket_server.py
```

クライアント起動

```
$ python tcp_socket_client.py
```

