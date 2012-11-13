import json
import subprocess
import io
import urllib2

from django.http import HttpResponse
from django.shortcuts import render
from django import forms


def echo(request):
    #return HttpResponse(json.dumps(request, indent=4), content_type="application/json")
    return HttpResponse(request, content_type="application/json")

def sign(request):
    callback = None
    inputd = io.BytesIO()
    if request.method == 'POST':
        for chunk in request.FILES['file_data'].chunks():
            inputd.write(chunk)
    else:
        url = request.GET['url']
        callback = request.GET['callback']
        data = urllib2.urlopen(url)
        inputd.write(data.read())
        data.close()

    output = _sign(inputd)
    j = dict()
    j['signature'] = output.getvalue()
    if callback:
        #return HttpResponse(callback + "({ signature: \"" + output.getvalue() +"\" });", content_type='application/javascript')
        #return HttpResponse(callback + "({ signature: \"json P!\" });", content_type='application/javascript')
        return HttpResponse(callback + "(" + json.dumps(j) + ");", content_type='application/javascript')
    else:
        return HttpResponse("{ signature: \"" + output.getvalue() +"\" }", content_type='text/javascript')

def upload(request):
    return render(request, 'upload.html')

def _sign(inputd):
    output = io.StringIO()
    gpg = subprocess.Popen(["gpg", "--detach-sign", "-a", "-"], stdin=subprocess.PIPE, stdout=subprocess.PIPE, shell=False)
    o, e = gpg.communicate(inputd.getvalue())
    if o:
        output.write(unicode(o))
    if e:
        output.write(unicode(e))
    gpg.wait()
    return output
