from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404, JsonResponse
from .models import APIAuth
from groups.models import Group, Membership
from numman.models import  Event, Number, TypeOfService, Range, Permission
from django.contrib.auth.models import User
from django.core.exceptions import PermissionDenied
from django.forms.models import model_to_dict
from django.core import serializers
import json
from django.conf import settings
import requests


def obj_to_dict(model_instance):
    serial_obj = serializers.serialize('json', [model_instance])
    obj_as_dict = json.loads(serial_obj)[0]['fields']
    obj_as_dict['value'] = model_instance.pk
    del obj_as_dict['user']
    del obj_as_dict['pub_date']
    newperm = []
    for p in obj_as_dict['permissions']:
        p_model= Permission.objects.get(pk=p)
        p_json = serializers.serialize('json', [p_model])
        p_obj = json.loads(p_json)[0]['fields']
        newperm.append(p_obj['value'])
    obj_as_dict['permissions'] = newperm
    return obj_as_dict

def publish(action, number, tos):
    data = {}
    data['number'] = number
    data['tos'] = tos
    headers = {'token': settings.HOOKDECK_TOKEN}
    url = settings.HOOKDECK_URL+'/'+action
    r = requests.post(url, headers=headers, data=data)
    print(r.text)
# Create your views here.

def list_numbers(request, event, tos):
    try:
        token = request.headers['Token']
        auth = APIAuth.objects.get(token=token)
        scope = auth.scope.filter(name=tos).values()
        if len(scope) == 0:
            raise PermissionDenied()
    except APIAuth.DoesNotExist:
        raise PermissionDenied()
    tosname = scope[0]['name']
    numbers = Number.objects.filter(typeofservice__name=tosname).filter(event__name=event).values()
    return JsonResponse({'numbers':list(numbers)})



def get_number(request, event, id):
    try:
        token = request.headers['Token']
        auth = APIAuth.objects.get(token=token)
    except APIAuth.DoesNotExist:
        raise PermissionDenied()
    scope = list(auth.scope.filter().values_list('name'))
    try:
        n = Number.objects.filter(value=id).filter(event__name=event).get()
        number=obj_to_dict(n)
        if number:
            if number['typeofservice'] in [i[0] for i in scope]:
                return JsonResponse(number, safe=False)
            else:
                raise PermissionDenied()
        else:
            raise Http404
    except:
        raise Http404     

def phonebook(request, event):
    numbers_obj = Number.objects.filter(directory=True).filter(event__name=event).values('value', 'label', 'typeofservice_id')
    return JsonResponse(list(numbers_obj), safe=False)


def get_group(request, event, group):
    try:
        token = request.headers['Token']
        auth = APIAuth.objects.get(token=token)
    except APIAuth.DoesNotExist:
        raise PermissionDenied()
    scope = list(auth.scope.filter().values_list('name'))
    if 'Group' in [i[0] for i in scope]:
        members = Membership.objects.select_related("member", "group").filter(group=group).filter(group__event__name=event).values("member_id", "delay")
        return JsonResponse(list(members), safe=False)
    else:
        raise PermissionDenied()

def join_group(request, event, group):
    try:
        token = request.headers['Token']
        auth = APIAuth.objects.get(token=token)
    except APIAuth.DoesNotExist:
        raise PermissionDenied()
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    scope = list(auth.scope.filter().values_list('name'))
    if 'Group' in [i[0] for i in scope]:
        number = Number.objects.select_related("typeofservice").get(value=int(body['member']))
        tos = number.typeofservice
        currmembers =  Membership.objects.filter(group=group).all()
        print(len(currmembers))
        exists =  currmembers.filter(member=number).first()
        if exists:
            print("Number already in Group")
            return HttpResponse(status=400,content="Number already in Group")
        if tos.group_capable == False:
            print("Number is Not Group Capable")
            return HttpResponse(status=400,content="Number is not group capable")
        if len(currmembers) >= 10:
            print("Group is at max size (10)")
            return HttpResponse(status=400,content="Group is at max size (10)")
        groupobj = Group.objects.filter(value=group).filter(event=event).get()
        print(groupobj)
        Membership.objects.create(group=groupobj, member=number, delay=int(body['delay']))
        return HttpResponse(status=201)
    else:
        raise PermissionDenied()

def leave_group(request, event, group):
    try:
        token = request.headers['Token']
        auth = APIAuth.objects.get(token=token)
    except APIAuth.DoesNotExist:
        raise PermissionDenied()
    body_unicode = request.body.decode('utf-8')
    body = json.loads(body_unicode)
    scope = list(auth.scope.filter().values_list('name'))
    if 'Group' in [i[0] for i in scope]:
        groupobj = Group.objects.filter(value=group).filter(event=event).get()
        member = Membership.objects.get(group=groupobj, member=body['member'])
        member.delete()
        publish('remove', group, 'Group')
        return HttpResponse(status=202)
    else:
        raise PermissionDenied()


