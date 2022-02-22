
def Handler(request,data, parent):
    html = parent.fromFile("index.html", {"title": "booboo"})
    # for i in range(1, 1000):
        # parent.setCookie("test"+str(i),"test",3600)
    #return parent.redirect("https://developer.mozilla.org/fr/docs/Web/HTTP/Headers/Location")
    return parent.sendHtml(html)





