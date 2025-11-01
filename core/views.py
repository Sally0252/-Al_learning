from django.shortcuts import render
from django.http import HttpRequest, HttpResponseRedirect
from core.models import Conversation
from core import services
from django.utils import timezone
from django.urls import reverse




def new_chat(request: HttpRequest):
    history = [
    {"role": "system", "content": "你是我的python学习助手，你要在明确我的学习目标，和学习背景的情况下，辅助我完成我的学习目标"},
    ] 

    conversation = Conversation.objects.create(
        title = 'python learning',
        history = history,
        created_at = timezone.now(),
        updated_at = timezone.now(),
        )
    return HttpResponseRedirect(reverse('chat',kwargs={'conversation_id': conversation.id}))

# get得到聊天历史， post提交聊天，并更新聊天历史。
def chat(reqeust: HttpRequest, conversation_id: int):
    conversation = Conversation.objects.get(id = conversation_id)
    history = conversation.history

    if reqeust.method == 'POST':
        question = reqeust.POST.get('question')
        # ask
        history.append({"role": "user", "content": question})
        reply = services.get_deepseek_response(history)
        history.append({"role": "assistant", "content": reply})
        conversation.history = history
        conversation.save()
    
    return render(reqeust, 'core/chat.html', {'history': history})


def index(request):
    conversations = Conversation.objects.all()
    return render(request, 'core/index.html', {'conversations': conversations})

