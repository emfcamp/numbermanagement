from django.shortcuts import render, redirect
from django.http import HttpResponse, Http404
from .forms import CreateNumberForm, EditNumberForm, DeleteNumberForm
from django.contrib.auth.models import User
from .models import  Event, Number, TypeOfService, Range
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.conf import settings
import requests
from groups.models import Group
import os.path 

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TEMPLATE_DIR = os.path.join(BASE_DIR, 'templates')

def home(request):
    return render(request, 'base.html', {'title': 'Number Management System', 'description':'Welcome to Numberwang!'})

def phonebook(request):
    publicnumbers = Number.objects.filter(directory=True).order_by('value')
    context = {'numbers': publicnumbers, 'title': "Phonebook"}
    return render(request, 'numman/phonebook.html', context)

def about(request):
    context = {'title': "Numberwang"}
    return render(request, 'numman/numberwang.html', context)


def getTOSData(priv=False):
    if priv:
        data =  list(TypeOfService.objects.values())
    else:
        data =  list(TypeOfService.objects.filter(privileged=False).values())
    newdata = {}
    for item in data:
        del item["privileged"]
        name = item['name']
        del item["name"]
        newdata[name] = item
    return newdata

def getRanges():
    data =  list(Range.objects.filter(privileged=False).values())
    for item in data:
        del item["id"]
        del item["privileged"]
    return data

def publish(action, number, tos):
    data = {}
    data['number'] = number
    data['tos'] = tos
    headers = {'token': settings.HOOKDECK_TOKEN}
    url = settings.HOOKDECK_URL+'/'+action
    r = requests.post(url, headers=headers, data=data)
    print(r.text)

    


@login_required
def create_number(request):
    if request.method == 'GET':
        first_event = Event.objects.filter(active=True)[0]
        form = CreateNumberForm(initial={'event': first_event})
        context = {'form': form, 'tosdata': getTOSData(), 'ranges': getRanges(), 'userdata' : {"username": request.user.username}, 'title': "Create new Number"}
        return render(request, 'numman/create_number.html', context)
    elif request.method == 'POST':
        form = CreateNumberForm(request.POST)
        form.instance.user  = request.user
        if form.is_valid():
            form.save()
            tosGroupObj = TypeOfService.objects.get(name='Group')
            if form.cleaned_data['typeofservice'] == tosGroupObj:
                n = Number.objects.get(pk=form.cleaned_data['value'])
                Group.objects.create(value=n, event=form.cleaned_data['event'], user=form.instance.user)
            publish('add', form.cleaned_data['value'], form.cleaned_data['typeofservice'])
            messages.success(request, 'The number has been created successfully.')
            return redirect('/number')
        else:
            return render(request, 'numman/create_number.html', {'form': form, 'tosdata': getTOSData(), 'ranges': getRanges(), 'userdata' : {"username": request.user.username}, 'title': "Create new Number"})

@login_required
def my_numbers(request):
    numbers = Number.objects.filter(user=request.user).order_by('value')
    context = {'numbers': numbers, 'title': "My Numbers"}
    return render(request, 'numman/mynumbers.html', context)


@login_required
def edit_number(request, id):
    number = Number.objects.filter(user=request.user).filter(value=id).first()
    if number == None:
        raise Http404
    else:
        if request.method == 'GET':
            context = {'form': EditNumberForm(instance=number), 'id': id, 'title': "Edit "+str(id)}
            return render(request,'form.html',context)
        elif request.method == 'POST':
            form = EditNumberForm(request.POST, instance=number)
            if form.is_valid():
                form.save()
                publish('removecache', id, number.typeofservice )
                messages.success(request, 'The number has been updated successfully.')
                return redirect('/number')
            else:
                messages.error(request, 'Please correct the following errors:')
                return render(request,'numman/edit_number.html',{'form':form, 'id': id, 'title': "Edit "+str(id)})

@login_required
def delete_number(request, id):
    number = Number.objects.filter(user=request.user).filter(value=id).first()
    if number == None:
        raise Http404
    else:
        if request.method == 'GET':
            context = {'form': DeleteNumberForm(), 'id': id, 'title': "Delete "+str(id)}
            return render(request,'form.html', context)
        elif request.method == 'POST':
            form = DeleteNumberForm(request.POST)
            if form.is_valid():
                data = form.cleaned_data
                print(data['checknumber'])
                print(id)
                if int(data['checknumber']) == int(id):
                    number = Number.objects.get(value=id)
                    number.delete()
                    publish('remove', id, number.typeofservice )
                    messages.success(request, 'The number has been deleted.')
                else:
                    messages.error(request, 'The confirmation did not match.')
            else:
                messages.error(request, 'Invalid Form')
        return redirect('/number')

@login_required
def number_info(request, id):
    number = Number.objects.filter(user=request.user).filter(value=id).first()
    if number == None:
        raise Http404
    ins_file = "service_instructions/"+number.typeofservice_id+".html"
    if os.path.exists(os.path.join(TEMPLATE_DIR, ins_file)):
        instructions = ins_file
    else:
        instructions = "service_instructions/_DEFAULT.html"
    print(instructions)
    context = {'number': number, 'title': 'Settings for '+str(id), 'instructions' : instructions}
    return render(request, 'numman/numberinfo.html', context)

def available_numbers(request):
    takennumbers =  Number.objects.values('value')
    numberlist = [o['value'] for o in list(takennumbers)]
    context = {'takennumbers': numberlist, 'rangedata': getRanges(), 'title': "Available Numbers"}
    return render(request, 'numman/availible_numbers.html', context)