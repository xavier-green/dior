import subprocess, os, socket, sys

server_address = './request.sock'

# Make sure the socket does not already exist
try:
    os.unlink(server_address)
except FileNotFoundError:
    pass

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the port
print('starting up on %s' % server_address
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    # Wait for a connection
    print('waiting for a connection')
    connection, client_address = sock.accept()
    try:
        print('Someone connected!')
        # Receive the data in small chunks and retransmit it
        while True:
            data = connection.recv(16)
            print('received "%s"' % data)
            if data:
                print('Sending the request to the MSSQL Server')
                p = subprocess.run('docker exec  mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P D10R_password! -d Reporting -W -w 999 -s | -Q'.split() + [data], stdout=subprocess.PIPE, universal_newlines=True)
                connection.sendall(p.stdout)
            else:
                print('no more data from', client_address)
                break

    finally:
        # Clean up the connection
        connection.close()
