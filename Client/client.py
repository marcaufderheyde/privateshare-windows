import socket
import sys
import os

running = True
# Create a client socket
cli_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# Prevent errors
try:
	# Connect client socket to server socket
	cli_sock.connect((sys.argv[1], int(sys.argv[2])))
	srv_addr = (sys.argv[1], int(sys.argv[2]))

except Exception as e:
	# Print the exception message
	print(e)
	# Exit with a non-zero value, to indicate an error condition
	exit(1)

try:
	while running:

		# Make sure the command has been parsed in correctly. If not, quit the connection
		if(len(sys.argv) < 4):
			print("You entered an invalid command. Please try again")
			break

		# Handling of a put request
		elif (str(sys.argv[3]) == "put"):

			# Make sure the put request has the correct number of arguments. If not, quit the connection.
			if(not (len(sys.argv) == 5)):
				print("You entered an invalid command. Please try again")
				break

			# Make sure that the client directory contains the file it is trying to upload
			directory = os.listdir()
			if(not str(sys.argv[4]) in directory):
				print("You are trying to upload a file which does not exist. Please try again")
				break

			else:
				# Send the server the exact commands of the put request
				cli_sock.sendall((str(sys.argv[3]) + ',' + str(sys.argv[4])).encode('utf-8'))
				
				# Open the file you are trying to send
				f = open(str(sys.argv[4]),'rb')
				data = f.read(33554432)

				# Before starting to send file, check that the server allows it. You cannot upload a file already on the server.
				checkreupload = cli_sock.recv(32)
				if(checkreupload.decode('utf-8') == 'cancel'):
					print("You are trying to upload a file with a taken filename. Please alter the filename.")
					break

				# If server allows it, continue to upload file to server.
				if(checkreupload.decode('utf-8') == 'pass'):
					while(data):
						print("Uploading file to server...")
						cli_sock.send(data)
						data = f.read(33554432)
					f.close()
					print("Done uploading file to server!")
					cli_sock.shutdown(socket.SHUT_WR)
					running = False

		# Handling of a get request	
		elif(str(sys.argv[3]) == "get"):

			# Make sure the correct arguments have been passed for a get request. If not, quit the connection
			if(not (len(sys.argv) == 5)):
				print("You entered an invalid command. Please try again")
				break
			
			# Make sure you don't have a file with the same filename already
			directory = os.listdir()
			if(not str(sys.argv[4]) in directory):

			# Send the server the exact commands of the get request
				cli_sock.send((str(sys.argv[3]) + ',' + str(sys.argv[4])).encode('utf-8'))
				checkreupload = cli_sock.recv(32)

				# Check that the server has the file you are trying to download
				if(checkreupload.decode('utf-8') == 'cancel'):
					print("You are trying to download a file that doesn't exist on the server. Please try again!")
					break

				# If the server has the file, continue to download file.
				if(checkreupload.decode('utf-8') == 'pass'):
					f = open(str(sys.argv[4]),'wb')
					data = cli_sock.recv(33554432)
					while(data):
						print("Receiving...")
						f.write(data)
						data = cli_sock.recv(33554432)
					f.close()
					print("Done Receiving")
					running = False

			else:
				print("You already have a file with that filename in the directory you are trying to download into")
				running = False

		# Handling of a list request
		elif(str(sys.argv[3]) == "list" and len(sys.argv) == 4):
			print("Reqeusting File Directory from server...")
			cli_sock.sendall(str(sys.argv[3]).encode('utf-8'))
			directory = cli_sock.recv(33554432)
			print("File Directory received:")
			print(directory.decode('utf-8'))
			running = False

finally:
	cli_sock.close()

# Exit with a zero value, to indicate success
exit(0)
