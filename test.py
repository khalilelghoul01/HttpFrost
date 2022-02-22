import requests
import threading

def req():
    r = requests.get("http://localhost:80/")
    print("done")
while True:
    threading.Thread(target=req).start()