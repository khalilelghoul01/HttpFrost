
import os
import re
import socket
import sys
import datetime
import threading
from colorama import Fore, Back, Style
from _thread import *
import console
from pyfiglet import Figlet

publicDir = 'public'
routeDir = 'routes'




def Log(func):
    def wrapper(*args, **kwargs):
        request = args[1]
        print(Fore.YELLOW + " - ".join(request) + Style.RESET_ALL)
        return func(*args, **kwargs)
    return wrapper


class Frost:
    def __init__(self, host='localhost', port=5000, variables=None):
        self.host = host.strip()
        self.port = port
        self.routes = []
        self.config = variables
        self.data = {}
        self.cookies = {}

    def run(self):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        running = True

        f = Figlet(font='smslant')
        print(console.Color(43, 216, 255) + f.renderText('HttpFrost') + Style.RESET_ALL)

        # create a thread to handle each request
        while running:
            client_socket, address = server_socket.accept()
            thread = threading.Thread(target=self.handle_requests, args=(client_socket,address,))
            thread.start()
        server_socket.close()


    def handle_requests(self, client_socket, client_address):
        request = client_socket.recv(10000000).decode()
        if not request:
            client_socket.close()
            return False
        self.data = self.parseData(request)
        headers = request.split('\n')
        request = headers[0].split()
        request.append(str(client_address[0])+":"+str(client_address[1]))
        return self.handle_request(request, client_socket)

    def parseData(self,request):
        data = {}
        if("\n"in request):
            request = request.split("\n")
            for requestLine in request:
                if(":" in requestLine):
                    requestLine = requestLine.split(":")
                    if("Cookie" in requestLine):
                        cookies={}
                        if(";" in requestLine[1]):
                            requestLine[1] = requestLine[1].split(";")
                            for cookie in requestLine[1]:
                                if("=" in cookie):
                                    cookie = cookie.split("=")
                                    cookies[cookie[0].strip()] = cookie[1].strip()
                        data["Cookie"] = cookies
                    else:
                        data[requestLine[0].strip()] = requestLine[1].strip()
        return data
    @Log
    def handle_request(self, request, client_connection):
        filename = request[1]
        if not "." in filename:
            if filename.endswith('/'):
                filename += 'index'
            fileToCall = "-".join(filename[1:].split('/'))
            filePDir = routeDir + \
                "/".join(filename.split('/')[:-1])+"/"+fileToCall+".py"
            fileDir = routeDir + "/".join(filename.split('/')[:-1])
            if(not os.path.exists(filePDir)):
                print(Fore.RED + "404 Not Found" + Style.RESET_ALL)
                client_connection.sendall(str(
                    'HTTP/1.0 404 Not Found\n\n<h1>404 Not Found</h1><br><h3>you can add / or create new file: "'+fileToCall+'.py"</h3>').encode())
                client_connection.close()
                return False
            if(not filename in self.routes):
                sys.path.insert(1, fileDir)
            try:
                module = __import__(fileToCall)
                handler = getattr(module, 'Handler')
                response = 'HTTP/1.0 200 OK\n'+ handler(request,self.data, self)
                client_connection.sendall(response.encode())
            except Exception as e:
                print(e)
        else:
            if(os.path.exists(publicDir+filename)):
                with open(publicDir+filename, 'r') as f:
                    content = f.read()
                response = 'HTTP/1.0 200 OK\nContent-Type: text/html\n\n'+  content
            else:
                response = 'HTTP/1.0 404 Not Found\nContent-Type: text/html\n\n<h1>404 Not Found</h1><br><h3>can\'t find: "'+filename+'"</h3>'
            client_connection.sendall(response.encode())
        client_connection.close()
        return True

    def fromFile(self,filepath, variables={}):
        filepath = publicDir + "/" + filepath
        html = ""
        if(not os.path.exists(filepath)):
            return "<h1>404 Not Found</h1><br><h3>can\'t find: '"+filepath+"'</h3>"
        with open(filepath, 'r') as f:
            html =  f.read()
        for key in variables:
            html = html.replace("$"+key+"$", variables[key])
        return html

    def setCookie(self,name,value,expire=None):
        if(expire):
            expire = datetime.datetime.fromtimestamp(datetime.datetime.now().timestamp()+expire).strftime('%a, %d %b %Y %H:%M:%S GMT')

        cookie = {
            "value": value,
            "expire": expire
        }
    
        self.cookies[name] = cookie

    def serializeCookies(self):
        cookie = ""
        for key in self.cookies:
            if(self.cookies[key]["expire"]):
                cookie += "Set-Cookie: "+str(key)+"="+str(self.cookies[key]["value"])+"; Expires="+str(self.cookies[key]["expire"])+"; Secure\n"
            else:
                cookie += "Set-Cookie: "+str(key)+"="+str(self.cookies[key]["value"])+"; Secure\n"
        return cookie
    
    def sendHtml(self,html):
        return self.serializeCookies() + "\n\n" + html


if __name__ == '__main__':
    frost = Frost(host='0.0.0.0', port=80)
    frost.run()
    