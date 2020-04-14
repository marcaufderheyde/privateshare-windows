# privateshare

Effective TCP Server and Client operating using python web sockets:

## Download server [Here](https://github.com/marcaufderheyde/privateshare-windows/raw/master/Server/dist/serverApp.exe)
## Download client [Here](https://github.com/marcaufderheyde/privateshare-windows/raw/master/Client/dist/clientApp.exe)
## Access the Mac Repo [Here](https://github.com/Vivinen/privateshare-mac)

#### General notes: 

###### To use privateshare across networks (server on one network, client on different network), you will need to set up port forwarding through your router.

* Files are downloaded/uploaded to/from wherever application or script is stored. 
  * If you are launching serverApp.exe from the downloads folder, the downloads folder becomes the server folder. 
  * If you are launching clientApp.exe from the downloads folder, the downlaods folder becomes the client folder. 
* Uploading a file with same filename of file already in server is prohibited to deny duplicates.
* Downloading a file with same filename of file already in client folder is prohibited to deny duplicates.
* Currently the server must be force closed

## Graphical User Interface (GUI) Instructions:

### **Using the Server:**

1. Download the executable server application from [Here](https://github.com/marcaufderheyde/privateshare-windows/raw/master/Server/dist/serverApp.exe)
2. Open serverApp.exe
3. Enter the port number you wish to bind to.
4. Click Run Server.
5. The server is now running and will remain running for up to 5 minutes without any connection requests. After 5 minutes, the server will automatically shutdown.
6. While the server is running, the GUI will appear unresponsive. Logging can be found in the Command Window opened when the serverApp is opened.

### **Using the Client:**

1. Download the executable client application from [Here](https://github.com/marcaufderheyde/privateshare-windows/raw/master/Client/dist/clientApp.exe)
2. Open clientApp.exe
3. Enter the IP address of the server you are trying to connect to. If you are running both server and client on the same machine, you can use 'localhost' for server address.
4. Enter the port number to which the server is bound (this number is specified by the maintainer of the server.
5. Select an operation from the menu on the left of the log box.
6. 'Put' corresponds to uploading a file, 'Get' corresponds to downloading a file and 'List' simply requests a list of all filenames accessible on the server for download.
7. For 'Put' and 'Get' commands, a filename is required. Enter this in the bottom box.
8. Click Put/Get/List in order to initialize an operation. Client will appear unresponsive if successfully carrying out an operation.
9. Client will become responsive once operation is completed.

## Command Line Interface Instructions & Detailed description of how it works:

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
