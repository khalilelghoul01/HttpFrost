
def Handler(request,data, parent):
    html = parent.fromFile("index.html", {"title": "str(data)"})
    for i in range(1, 1000):
        parent.setCookie("test"+str(i),"test",3600)
    return parent.sendHtml(html)