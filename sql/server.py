import subprocess, os, socket, sys

server_address = '/tmp/request.sock'

# Make sure the socket does not already exist
try:
    os.unlink(server_address)
except FileNotFoundError:
    pass

# Create a UDS socket
sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)

# Bind the socket to the port
print('starting up on %s' % server_address)
sock.bind(server_address)

# Listen for incoming connections
sock.listen(1)

while True:
    print('waiting')
    con, add = sock.accept()
    try:
        print('Connectecd!')
        while True:
            data = con.recv(8192).decode("utf-8")
            print(data)
            if data:
                print('Sending the request to the MSSQL Server')
                p = subprocess.run('docker exec  mssql /opt/mssql-tools/bin/sqlcmd -S localhost -U sa -P D10R_password! -d Reporting -W -w 999 -s | -Q'.split() + [data], stdout=subprocess.PIPE, universal_newlines=True)
                print(p.stdout)
                con.sendall(bytes(p.stdout, 'utf-8'))
            else:
                print('No more data')
                break
    finally:
        con.close()
