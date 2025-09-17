from django.shortcuts import render, redirect
from .models import Group, Membership
from numman.models import Number
from django.contrib.auth.decorators import login_required
from .forms import JoinGroupForm
from django.http import HttpResponse, Http404
from django.conf import settings
import requests
from django.contrib import messages

def publish(action, number, tos):
    data = {}
    data['number'] = number
    data['tos'] = tos
    headers = {'token': settings.HOOKDECK_TOKEN}
    url = settings.HOOKDECK_URL+'/'+action
    r = requests.post(url, headers=headers, data=data)
    print(r.text)

@login_required
def list_groups(request):
    groups = Group.objects.filter(user=request.user).order_by('value')
    context = {'groups': groups, 'title': "My Groups"}
    return render(request, 'group/listgroups.html', context)


@login_required
def lookup_group(request, eventvalue):
    event = eventvalue.split("-")[0]
    value = eventvalue.split("-")[1]
    group = Group.objects.select_related("value").filter(
        value__user=request.user,
        value__value=value,  # Filter by the Number's value field
        event_id=event      # Also filter by event to ensure uniqueness
    ).first()
    print(group)
    if group == None:
        raise Http404
    else:
        return redirect('/group/'+str(group))

@login_required
def manage_group(request, id):
    group = Group.objects.select_related("value").filter(value__user=request.user).filter(id=id).first()
    if group == None:
        raise Http404
    else:
        if request.method == 'GET':
            members = Membership.objects.select_related("member").filter(group=group).values("member_id", "member__label", "member__value", "delay").order_by('member_id')
            joinform = JoinGroupForm(group=group)
            context = {'members': members, 'group': group, 'joinform': joinform}
            return render(request, 'group/managegroup.html', context)
        elif request.method == 'POST':
            joinform = JoinGroupForm(request.POST, group=group)
            joinform.instance.group=group
            if joinform.is_valid():
                publish('updategroup', id, 'Group')
                joinform.save()
                mid = joinform.cleaned_data['member']
                messages.success(request, str(mid)+' addded to Group: '+str(id))
            return redirect('/group/'+str(id))

@login_required
def leave_group(request, gid, mid):
    group = Group.objects.select_related("value").filter(value__user=request.user).filter(id=gid).first() 
    if group == None:
        raise Http404
    member = Membership.objects.get(group=gid, member=mid)
    member.delete()
    publish('updategroup', gid, 'Group')
    messages.success(request, str(mid)+' removed from Group: '+str(gid))
    return redirect('/group/'+str(gid))
