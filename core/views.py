from django.shortcuts import render
from django.http import HttpRequest

from core import services

history = [
    {"role": "system", "content": "你是我的python学习助手，你要在明确我的学习目标，和学习背景的情况下，辅助我完成我的学习目标"},
] 

# get得到聊天历史， post提交聊天，并更新聊天历史。
def chat(reqeust: HttpRequest):
    if reqeust.method == 'POST':
        question = reqeust.POST.get('question')
        # ask
        history.append({"role": "user", "content": question})
        reply = services.get_deepseek_response(history)
        history.append({"role": "assistant", "content": reply})
        print(history,'333')
    
    return render(reqeust, 'core/chat.html', {'history': history})