

def Handler(request,data, parent):
    html = parent.fromFile("index.html", {"title": "str(data)"})
    return parent.sendHtml(html)
    