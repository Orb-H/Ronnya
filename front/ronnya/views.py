from django.shortcuts import render
from django.http import HttpResponse
import requests
# Create your views here.

def index(request):
    return render(request, "ronnya.html");

def makeimg(request):
    name=request.GET.get("name","");
    if name=="":
        return render(request, "ronnya.html",{'isEmpty':'True'});
    else:
        data={
            "name" : name
        }
        res=requests.get("http://58.123.175.31/api",data=data);
        svg='''
        <svg version="1.1" xmlns="http://www.w3.org/2000/svg" width="400" height="180">
            <g>
                <rect x="0" y="0" rx="20" ry="20" width="300" height="150"
                style="fill:red;stroke:black;stroke-width:5;opacity:0.5" />
                <text x="0" y="50" font-family="Verdana" font-size="30" fill="white" >{name}</text>
            </g>
        </svg>
        '''.format(name=res.text);
        response=HttpResponse(content=svg);
        response['Content-Type'] = 'image/svg+xml';
        response['Cache-Control'] = 'max-age=1800';
        
        return response