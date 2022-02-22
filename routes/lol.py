def Handler(request,data, parent):
    phrases = ["Hello", "World", "from", "httpFrost"]
    element = ""
    for phrase in phrases:
        element += phrase+"<br>"
    html = parent.fromFile("index.html", {"title": element})
    return parent.sendHtml(html)
    