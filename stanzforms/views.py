from django.shortcuts import Http404
from django.shortcuts import render
from .models import Doska, Knife


def doska_list(request):
    table = Doska.objects.all()
    return render(request, 'doska.html', {'table': table})


def knife_list(request, doskaid):
    try:
        knives = Knife.objects.filter(doska=doskaid)
    except Knife.DoesNotExist:
        raise Http404

    return render(request, 'knife.html', {'knives': knives})