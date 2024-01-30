from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.models import User
from django.contrib.messages import constants
from django.contrib import auth
from django.contrib import messages



def login(request):
    if request.method == 'GET':
        return render(request, 'login.html')
    elif request.method == 'POST':
        username = request.POST.get('username')
        senha = request.POST.get('senha')

        user = auth.authenticate(request, username=username, password=senha)
        if user:
            auth.login(request, user)
            messages.add_message(request, constants.SUCCESS, 'Logado!')
            return redirect('/')
        else:
            messages.add_message(
                request, constants.ERROR, 'Username ou senha inválidos'
            )
            return redirect('/usuarios/login/')
        
        
def logout(request):
    if request.method == "GET":
        auth.logout(request)
        messages.add_message(request, constants.SUCCESS, 'Você efetuou o logout com sucesso')
        return redirect('/usuarios/login/')


def cadastro(request):
    if request.method == 'GET':
        return render(request, 'cadastro.html')
    else:
        username = request.POST.get('username')
        senha = request.POST.get('senha')
        confirmar_senha = request.POST.get('confirmar_senha')

        if not senha == confirmar_senha:
            messages.add_message(
                request, constants.ERROR, 'As senhas não coincídem'
            )
            return redirect('/usuarios/cadastro/')

        user = User.objects.filter(username=username)

        if user.exists():
            messages.add_message(
                request,
                constants.ERROR,
                'Já existe um usuário com o mesmo username',
            )
            return redirect('/usuarios/cadastro/')

        try:
            user = User.objects.create_user(
                username=username,
                password=confirmar_senha,
            )
            messages.add_message(
                request, constants.ERROR, 'Usuário cadastrado com sucesso.'
            )
            return redirect('/usuarios/login/')
        except:
            messages.add_message(
                request, constants.ERROR, 'Erro interno do sistema'
            )
            return redirect('/usuarios/cadastro/')


