from django.test import TestCase
from django.shortcuts import render_to_response

# Create your tests here.

def test(request):

    class fruit():
        def __init__(self, color, size):
            self.color = color
            self.size = size

    arbuz = fruit('red', 'big')
    sliva = fruit('blue', 'small')

    #list
    data = []
    data.append(arbuz)
    data.append(sliva)

    return render_to_response('test.html', {'data':data})