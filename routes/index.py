
def Handler(request,data, parent):
    html = parent.fromFile("index.html", {"title": "httpFrost"})
    # parent.setCookie("test","test",3600)
    #return parent.redirect("https://developer.mozilla.org/fr/docs/Web/HTTP/Headers/Location")
    return parent.sendHtml(html)





