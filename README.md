# HttpFrost
a python web framework


it's a web framework for python
type: a nested framework like PHP or Ruby
   every file is a web page


## Logo
![](https://github.com/khalilelghoul01/HttpFrost/blob/master/logo.png?raw=true)


## Main

# Language: python
# Path: main.py

```python
from frost import Frost

frost = Frost(host='0.0.0.0', port=80)
frost.run()

```


you need two folders (routes, public):

-in public you can put your static files (css, js, images, etc)<br>
-in routes you can put your routes controller in python files


## Routes

# Language: python
# Path: index.py

```python
def Handler(request,data, parent):
    html = parent.fromFile("index.html", {"title": "httpFrost"})
    # parent.setCookie("test","test",3600)
    #return parent.redirect("https://developer.mozilla.org/fr/docs/Web/HTTP/Headers/Location")
    return parent.sendHtml(html)

```