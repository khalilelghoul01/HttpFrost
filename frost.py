
from enum import auto
import hashlib
import importlib
import os
import re
import socket
import sys
import datetime
import threading
import time
from colorama import Fore, Back, Style
from _thread import *
import threading
import console
from pyfiglet import Figlet

publicDir = 'public'
routeDir = 'routes'
filesIDs = {}

def Log(func):
    def wrapper(*args, **kwargs):
        request = args[1]
        log = Fore.YELLOW + " - ".join(request) + Style.RESET_ALL
        print(log)
        with open("requests.log", "a+") as f:
            f.write(datetime.datetime.now().strftime("[%d-%b-%Y (%H:%M:%S.%f)] : ") + " - ".join(request) + "\n")
        return func(*args, **kwargs)
    return wrapper

def file_as_bytes(file):
    with file:
        return file.read()

class Frost:
    def __init__(self, host='localhost', port=5000, variables=None,debug=False):
        self.debug = debug
        self.host = host.strip()
        self.port = port
        self.routes = []
        self.config = variables
        self.data = {}
        self.cookies = {}
        self.status = {
            200: "OK",
            301: "Moved Permanently",
            302: "Found",
            400: "Bad Request",
            401: "Unauthorized",
            403: "Forbidden",
            404: "Not Found",
            500: "Internal Server Error",
            501: "Not Implemented"
        }
        self.filesList = os.listdir(routeDir)

    def run(self):

        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        server_socket.bind((self.host, self.port))
        server_socket.listen(5)
        running = True

        f = Figlet(font='smslant')
        author = "by @khalilelghoul01"
        httpFrost = f.renderText('HttpFrost')
        author = author + (" "*(len(httpFrost.split("\n")[0])-len(author)))+"\n"
        author += (" "*(len(httpFrost.split("\n")[0])+10))
        httpfrostLines = httpFrost.split("\n")
        for index,line in enumerate(httpfrostLines):
            line = " "*5+line+" "*5
            httpfrostLines[index] = line
            
        httpFrost = "\n".join(httpfrostLines)
        print(console.Color(0, 0, 0,True)+console.Color(43, 216, 255) + httpFrost + console.Color(230, 0, 153)+author+ Style.RESET_ALL)



        if(self.debug):
            print(console.Color(245, 155, 66)+"Starting Frost in debuggin mode"+Style.RESET_ALL)
            debugThread = threading.Thread(target=self.debug_mode)
            debugThread.start()




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
        global filesIDs
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
                moduleID = {
                    "module": module,
                    "file": filePDir,
                    "md5": str(hashlib.md5(file_as_bytes(open(filePDir, 'rb'))).hexdigest())
                }
                filesIDs[fileToCall] = moduleID
                handler = getattr(module, 'Handler')
                response = handler(request,self.data, self)
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
    
    def sendHtml(self,html,status=200):
        if(not self.checkStatusExist(status)):
            status = 200
        response = 'HTTP/1.0 '+str(status)+' '+self.status[status]+'\nContent-Type: text/html\n\n'+  html
        return response

    def redirect(self,url,status=302):
        if(not self.checkStatusExist(status)):
            status = 302
        response = 'HTTP/1.0 '+str(status)+' '+self.status[status]+'\nLocation: '+url+'\n\n'
        return response

    def checkStatusExist(self,status):
        if(status in self.status):
            return True
        return False

    def debug_mode(self):
        global filesIDs
        while(self.debug):
            time.sleep(2)
            for file in filesIDs:
                path = filesIDs[file]["file"]
                hashmd5 = str(hashlib.md5(file_as_bytes(open(path, 'rb'))).hexdigest())
                if(filesIDs[file]["md5"] != hashmd5):
                    self.reload()
                    filesIDs[str(file)]["md5"] =  hashmd5
                    
    def reload(self):
        print(Fore.GREEN + "Reloading" + Style.RESET_ALL)
        for key in filesIDs:
            module = filesIDs[key]["module"]
            importlib.reload(module)
        print(Fore.GREEN + "All up to date" + Style.RESET_ALL)




if __name__ == '__main__':
    frost = Frost(host='0.0.0.0', port=80,debug=True)
    frost.run()
    