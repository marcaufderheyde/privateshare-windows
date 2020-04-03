# privateshare
Effective TCP Server and Client operating using python web sockets:

**Use Anaconda prompt for entering commands. [Download Anaconda Here](https://www.anaconda.com/distribution/#download-section)**

**When entering commands, make sure you are in the same directory as the client.py/server.py file**

### **The client handles commands typed into the command line in the following schematic.**

If the command passed into the command line contains the minimum amount of possibly correct parameters (at least 3, containing IP address, port number and request type), then the command is sent onto the server after having being correctly handled by the client. The command is sent as an encoded utf-8 string. The command is then received by the server and restricted to 32 bytes, where it is then broken up and handled according to the requirements of the command. To clarify, the first message exchanged between the client and server are the exact commands of the request given, if the request fits into the correct format.

When checking whether a file already exists on the server, the server sends a case specific code to the client, allowing it either to continue or cancel the request. The codes are two utf-8 encoded strings, either ‘pass’ or ‘cancel’. When checking whether a file exists on the server and can be sent, the server sends a case specific code to the client, allowing it either to continue or cancel the request. In both these cases, the client receives the case specific code, restricted up to 32 bytes, and continues according to the specified code. 

### **The actual sending and receiving of files was designed as follows:**

Uploading a file from client to server (put): Once receiving the ‘pass’ code from the server as an encoded utf-8 string, the client opens the file it wants to send to the server, and reads the first 33554432 bytes, which it then begins sending in a loop while reading the next 33554432 bytes and sending those in turn. Once all the bytes have been sent, the client shuts down its connection and quits the client program, reporting on the success of the operation. The server does the opposite pretty much, in that he receives the first 33554432 bytes and writes them to a new file, while looping over these steps and receiving more bytes until they have all been sent. After completion the server closes the connection and reports on the success of the operation.

### **EXAMPLE PUT: python client.py localhost 365 put apple.jpg**

Downloading a file from server to client (get): Once sending the ‘pass’ code to the client as an encoded utf-8 string, the server opens the file it wants to send to the client, and reads the first 33554432 bytes, which then begins sending in a loop while reading the next 33554432 bytes and sending those in turn. Once all the bytes have been sent, the server shuts down the connection and waits for the next request, reporting on the success of the operation. The client does the opposite of this, in that he receives the first 33554432 bytes and writes them to a new file, while looping over these steps and receiving more bytes until they have all been sent. After completion the client program quits, reporting on the success of the operation.

### **EXAMPLE GET: python client.py localhost 365 get apple.jpg**

Receiving the file directory from the server (list): Once the server receives the list command as an encoded utf-8 string, it begins handling the request. It first reads the directory in which it is running, and creates a String containing all files in the directory. Once compiling this list, it sends the list as a single packet to the client, which is in turn waiting to receive a packet. Upon having sent the list, the server quits the connection with the client and reports on the success of the operation. The client upon receiving the list ensures that it has received the list, and reports on the success of the operation. The connection is then closed.

### **EXAMPLE LIST: python client.py localhost 365 list**
