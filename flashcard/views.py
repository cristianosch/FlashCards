from django.shortcuts import render, redirect
from .models import Categoria, Flashcard, Desafio, FlashcardDesafio
from django.contrib.messages import constants
from django.contrib import messages
from django.http import Http404


 
def index(request):
    if not request.user.is_authenticated:
        return redirect('/usuarios/login/')
    
    if request.method == 'GET':
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        flashcards = Flashcard.objects.filter(user=request.user)  
        #print(f'Aqui aparece as categorias {categorias}\n')
        categoria_filtrar = request.GET.get('categorias')
        dificuldade_filtrar = request.GET.get('dificuldade') 
                
        if categoria_filtrar:
            flashcards = flashcards.filter(categoria__id = categoria_filtrar)
            #print(f'Aqui deve aparecer a categoria {categoria_filtrar}\n')
            
        if dificuldade_filtrar:
            flashcards = flashcards.filter(dificuldade = dificuldade_filtrar)
            #print(f'Aqui deve aparecer o nivel de dificuldade {dificuldade_filtrar}\n')
               
        return render(request,'index.html',
                      {'categorias': categorias,
                       'dificuldades': dificuldades,
                       'flashcards': flashcards,
                       })
        
    elif request.method == 'POST':
        pergunta = request.POST.get('pergunta')
        resposta = request.POST.get('resposta')
        categoria = request.POST.get('categoria')
        dificuldade = request.POST.get('dificuldade')
        
        if len(pergunta.strip()) == 0 or len(resposta.strip()) == 0:
            messages.add_message(request,constants.ERROR,'Preencha os campos de pergunta e resposta',)
            return redirect('/')
        flashcard = Flashcard(
            user=request.user,
            pergunta=pergunta,
            resposta=resposta,
            categoria_id=categoria,
            dificuldade=dificuldade,
            )
        flashcard.save()
        messages.add_message(
            request, constants.SUCCESS, 'Flashcard criado com sucesso')
        return redirect('/')
      
      

def deletar_flashcard(request, id):        
    flashcard = Flashcard.objects.filter(user=request.user, id=id)
    if not flashcard:
        messages.add_message(request, constants.ERROR, 'Você esta tentando fazer algo errado')
        return redirect('/')
    flashcard.delete()
    messages.add_message(request, constants.SUCCESS, 'Flashcard deletado com sucesso!')
    return redirect('/')


def iniciar_desafio(request):
    if request.method == 'GET':
        desafios = Desafio.objects.all()
        categorias = Categoria.objects.all()
        dificuldades = Flashcard.DIFICULDADE_CHOICES
        return render(
            request,
            'iniciar_desafio.html',
            {'categorias': categorias, 
             'dificuldades': dificuldades,
             'desafios': desafios},
        )
    elif request.method == 'POST':
        titulo = request.POST.get('titulo')
        categorias = request.POST.getlist('categoria')
        dificuldade = request.POST.get('dificuldade')
        qtd_perguntas = request.POST.get('qtd_perguntas')       


        desafio = Desafio(
            user=request.user,
            titulo=titulo,
            quantidade_perguntas=qtd_perguntas,
            dificuldade=dificuldade,
        )
        desafio.save()

        desafio.categoria.add(*categorias)

        flashcards = (
            Flashcard.objects.filter(user=request.user)
            .filter(dificuldade=dificuldade)
            .filter(categoria_id__in=categorias)
            .order_by('?')
        )

        if flashcards.count() < int(qtd_perguntas):
            return redirect('/flashcard/iniciar_desafio/')

        flashcards = flashcards[: int(qtd_perguntas)]

        for f in flashcards:
            flashcard_desafio = FlashcardDesafio(
                flashcard=f,
            )
            flashcard_desafio.save()
            desafio.flashcards.add(flashcard_desafio)

        desafio.save()

        return redirect(f'/flashcard/desafio/{desafio.id}/')
    
        
def listar_desafio(request):
    desafios = Desafio.objects.filter(user=request.user)       
    # ADIÇÃO O FILTRO DE BUSCA     
    if request.method == 'GET':   
        categorias = Categoria.objects.all()               
        dificuldades = Flashcard.DIFICULDADE_CHOICES            
        categoria_filtrar = request.GET.get('categoria')             
        #print(f'Aqui deve aparecer a categoria {categoria_filtrar}\n')                 
        dificuldade_filtrar = request.GET.get('dificuldade')        
        if categoria_filtrar:
            desafios = desafios.filter(categoria__id = categoria_filtrar)            
            
        if dificuldade_filtrar:
            desafios = desafios.filter(dificuldade = dificuldade_filtrar)
            #print(f'Aqui deve aparecer o nivel de dificuldade {dificuldade_filtrar}\n')
            
            
        return render(request,'listar_desafio.html',{
            'desafios': desafios,
            'categorias': categorias,
            'dificuldades': dificuldades,                     
            })
    
    

def desafio(request, id):
    desafio = Desafio.objects.get(id=id)
    if not desafio.user == request.user:
        raise Http404()
    if request.method == 'GET':
        acertos = desafio.flashcards.filter(respondido=True).filter(acertou=True).count()
        erros = desafio.flashcards.filter(respondido=True).filter(acertou=False).count()
        faltantes = desafio.flashcards.filter(respondido=False).count()
        return render(
    request,'desafio.html',{
        'desafio': desafio,
        'acertos': acertos,
        'erros': erros,
        'faltantes': faltantes,
        },)
        
        

def responder_flashcard(request, id):
    flashcard_desafio = FlashcardDesafio.objects.get(id=id)
    acertou = request.GET.get('acertou')
    desafio_id = request.GET.get('desafio_id')
    
    if not flashcard_desafio.flashcard.user == request.user:
        raise Http404()

    flashcard_desafio.respondido = True
    flashcard_desafio.acertou = True if acertou == '1' else False
    flashcard_desafio.save()
    return redirect(f'/flashcard/desafio/{desafio_id}/')



def relatorio(request, id):
    desafio = Desafio.objects.get(id=id)


    acertos = desafio.flashcards.filter(acertou=True).count()
    erros = desafio.flashcards.filter(acertou=False).count()

    dados = [acertos, erros]


    categorias = desafio.categoria.all()
    name_categoria = [i.nome for i in categorias]

    dados2 = []
    for categoria in categorias:
        print(categoria)
        dados2.append(desafio.flashcards.filter(flashcard__categoria=categoria).filter(acertou=True).count())

    return render(request, 'relatorio.html', {'desafio': desafio, 'dados': dados, 'categorias': name_categoria, 'dados2': dados2,},)
