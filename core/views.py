from django.shortcuts import render
from django.http import HttpRequest, HttpResponseRedirect
from core.models import Conversation
from core import services
from django.utils import timezone
from django.urls import reverse
from core.forms import ChoiceForm



def new_chat(request: HttpRequest):
    if request.method == 'POST':
        conversation_id = services.create_conversation(request.POST.get('answer'))

        return HttpResponseRedirect(reverse('choice_chat',kwargs={'conversation_id': conversation_id}))
  
    return render(request, 'core/new_chat.html')
   
# get 显示choice，和表单， post，处理choice的答案，然后redirect到chat
def choice_chat(request: HttpRequest, conversation_id: int):

    choice_questions = services.get_choice_data(conversation_id)

    if request.method == 'POST':
        form = ChoiceForm(request.POST, choice_data=choice_questions)

        if form.is_valid():
            choice_answers = ''.join(form.cleaned_data.values())
            services.handle_choice_answers(choice_answers, conversation_id)

            return HttpResponseRedirect(reverse('chat',kwargs={'conversation_id': conversation_id}))

    form = ChoiceForm(choice_data=choice_questions)

    context = {'form': form, 'conversation_id': conversation_id}
    return render(request, 'core/choice_chat.html', context)
    


# get得到聊天历史， post提交聊天，并更新聊天历史。
# 每次都有2个id
# 
def chat(request: HttpRequest, conversation_id: int):

    module_id = request.GET.get('module_id', "M01")

    if request.method == 'POST':
 
        
        action = request.POST.get('action')

        if action == 'next':
            module_id =  services.handle_next(conversation_id)
            
        elif action == 'answer':
            services.handle_answer(conversation_id)

            
        elif action == 'Q&A':
            question = request.POST.get('question')
            services.handle_question(question, conversation_id)

		
    learning_plan = services.get_learning_plan(conversation_id)
    learning_content = services.get_learning_module(conversation_id, module_id)
    context = {'learning_plan': learning_plan, 'learning_content': learning_content, "conversation_id": conversation_id}
    return render(request, 'core/chat.html', context)


def index(request):
    conversations = Conversation.objects.all()
    return render(request, 'core/index.html', {'conversations': conversations})


def remove(request, conversation_id: int):
    Conversation.objects.get(id = conversation_id).delete()
    return HttpResponseRedirect(reverse('index'))
  