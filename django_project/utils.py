## importing socket module
import socket

# Python program to find the IP Address of the client
# https://www.tutorialspoint.com/python-program-to-find-the-ip-address-of-the-client


def getHostIp():
    ## getting the hostname by socket.gethostname() method
    hostname = socket.gethostname()
    ## getting the IP address using socket.gethostbyname() method
    ip_address = socket.gethostbyname(hostname)
    ## printing the hostname and ip_address
    print(f"Hostname: {hostname}")
    print(f"IP Address: {ip_address}")

    return {"Hostname": {hostname}, "IP Address": {ip_address}}
