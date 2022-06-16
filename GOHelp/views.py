import json

from django.contrib import auth
from django.contrib.auth import authenticate
from django.contrib.auth.models import User
from django.core.paginator import Paginator
from django.shortcuts import redirect
from django.http import JsonResponse
from django.shortcuts import render
from django.views import generic
from GOHelp.models import Bizinfo
from GOHelp.models import Bookmark

# Create your views here.


def index(request):
    num_bizinfo = Bizinfo.objects.all().count()
    if User.is_authenticated:
        username = User.username
    else:
        username = None
    context = {
        'num_bizinfo' : num_bizinfo,
        'username' : username,
    }
    return render(request, 'index.html', context=context)

class BizListView(generic.ListView):
    model = Bizinfo
    def get_context_data(self, **kwargs):
        search = self.request.GET.get("search")
        context = super().get_context_data(**kwargs)
        if search is not None:
            context['search'] = search
            querys = Bizinfo.objects.all().filter(title__contains=search) | \
                     Bizinfo.objects.all().filter(summary__contains=search) | \
                     Bizinfo.objects.all().filter(ministry__contains=search) | \
                     Bizinfo.objects.all().filter(institution__contains=search)
        else:
            querys = context['bizinfo_list']
        paginator = Paginator(querys, 12)
        last_page = paginator.page_range[-1]
        current_page = int(self.request.GET.get("page", 1))
        start_page = ((current_page - 1) // 10) * 10 + 1
        end_page = last_page if start_page + 9 > last_page else start_page + 9
        context['pages'] = [i for i in range(start_page, end_page + 1)]
        context['previous'] = end_page - 10 if current_page > 10 else None
        context['next'] = start_page + 10 if end_page + 1 < last_page else None
        if last_page > 0:
            context['is_paginated'] = True
        user_list = [data.biz_id.title for data in Bookmark.objects.all() if
                     data.username.username == str(self.request.user)]
        biz_list = []
        for i in querys[(current_page-1)*12:current_page*12]:
            biz = {}
            biz['id'] = i.id
            biz['title'] = i.title
            if biz['title'] in user_list:
                biz['bmk'] = 'chk'
            biz['ministry'] = i.ministry
            biz['period'] = i.period
            biz['url'] = i.get_absolute_url
            n = i.summary.find('☞')
            biz['summary'] = i.summary[:n]
            biz_list.append(biz)
        context['result'] = biz_list
        return context

class BizDetailView(generic.DetailView):
    model = Bizinfo

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['summary'] = context['bizinfo'].summary.split('☞')
        context['outline'] = context['summary'][0]
        return context

class BookmarkListView(generic.ListView):
    model = Bookmark
    paginate_by = 12
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        last_page = context['page_obj'].paginator.page_range[-1]
        current_page = context['page_obj'].number
        start_page = ((current_page - 1) // 10) * 10 + 1
        end_page = last_page if start_page + 9 > last_page else start_page + 9
        context['pages'] = [i for i in range(start_page, end_page + 1)]
        context['previous'] = end_page - 10 if current_page > 10 else None
        context['next'] = start_page + 10 if end_page + 1 < last_page else None
        querys = [data for data in Bookmark.objects.all() if
                  data.username.username == str(self.request.user)]
        biz_list = []
        for i in querys:
            biz = {}
            biz['id'] = i.biz_id.id
            biz['title'] = i.biz_id.title
            biz['bmk'] = 'chk'
            biz['ministry'] = i.biz_id.ministry
            biz['period'] = i.biz_id.period
            biz['url'] = i.biz_id.get_absolute_url
            n = i.biz_id.summary.find('☞')
            biz['summary'] = i.biz_id.summary[:n]
            biz_list.append(biz)
        context['result'] = biz_list
        return context


def signup(request):
    if request.method == 'POST':
        type = request.POST.get("type")
        trigger = "$('.img__btn').trigger('click');"
        if type == 'signup':
            try:
                if request.POST['id'] == '':
                    error = '아이디를 입력해주세요.'
                    return render(request, 'GOHelp/signup.html', {'signup_error': error, 'trigger': trigger})
                if request.POST['pw1'] == '' or request.POST['pw2'] == '':
                    error = '비밀번호를 입력해주세요.'
                    return render(request, 'GOHelp/signup.html', {'signup_error': error, 'trigger': trigger})
                if request.POST['email'] == '':
                    error = '이메일을 입력해주세요.'
                    return render(request, 'GOHelp/signup.html', {'signup_error': error, 'trigger': trigger})
                if len(request.POST['id']) < 4:
                    error = '아이디는 4자 이상 입력해야합니다.'
                    return render(request, 'GOHelp/signup.html', {'signup_error': error, 'trigger': trigger})
                if len(request.POST['pw1']) < 6:
                    error = '비밀번호는 6자 이상 입력해야합니다.'
                    return render(request, 'GOHelp/signup.html', {'signup_error': error, 'trigger': trigger})
                if request.POST['pw1'] != request.POST['pw2']:
                    error = '비밀번호가 서로 일치하지 않습니다.'
                    return render(request, 'GOHelp/signup.html', {'signup_error': error, 'trigger': trigger})
                if User.objects.filter(username=request.POST['id']).exists():
                    error = '이미 등록된 아이디입니다.'
                    return render(request, 'GOHelp/signup.html', {'signup_error': error, 'trigger': trigger})
                user = User.objects.create_user(
                    username = request.POST['id'],
                    password = request.POST['pw1'],
                    email = request.POST['email'],
                )
                auth.login(request, user)
                return redirect('/')
            except:
                render(request, 'GOHelp/signup.html')
        elif type == 'signin':
            try:
                id = request.POST['id']
                pw = request.POST['pw']
                user = authenticate(request, username=id, password=pw)
                if id == '':
                    error = '아이디를 입력해주세요.'
                    return render(request, 'GOHelp/signup.html', {'signin_error': error})
                if pw == '':
                    error = '비밀번호를 입력해주세요.'
                    return render(request, 'GOHelp/signup.html', {'signin_error': error})
                if user is None:
                    error = '아이디와 비밀번호가 일치하지 않습니다.'
                    return render(request, 'GOHelp/signup.html', {'signin_error': error})
                if user is not None:
                    auth.login(request, user)
                    return redirect('/')
            except:
                render(request, 'GOHelp/signup.html')
    return render(request, 'GOHelp/signup.html')

def login(request):
    if request.method == 'POST':
        id = request.POST['id']
        pw = request.POST['pw']
        user = authenticate(request, username=id, password=pw)
        if user is not None:
            auth.login(request, user)
            return redirect('/')
        else:
            return render(request, 'login.html', {'error':'아이디와 비밀번호가 일치하지 않습니다.'})
    else:
        return render(request, 'GOHelp/login.html')

def logout(request):
    auth.logout(request)
    return redirect('/')

def bookmark_in(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        biz_id = Bizinfo.objects.get(id=data['id'])
        username = User.objects.get(username=data['username'])
        Bookmark(username=username, biz_id=biz_id).save()
    return JsonResponse(data)

def bookmark_out(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        biz_id = Bizinfo.objects.get(id=data['id'])
        username = User.objects.get(username=data['username'])
        Bookmark.objects.get(username=username, biz_id=biz_id).delete()
    return JsonResponse(data)