from django.shortcuts import render_to_response, RequestContext, Http404
from .models import Doska, Knife


def doska_list(request):
    context_instance = RequestContext(request)
    table = Doska.objects.all()
    return render_to_response('doska.html', {'table': table}, context_instance)


def knife_list(request, doskaid):
    context_instance = RequestContext(request)

    try:
        knives = Knife.objects.filter(doska=doskaid)
    except Knife.DoesNotExist:
        raise Http404

    return render_to_response('knife.html', {'knives': knives}, context_instance)