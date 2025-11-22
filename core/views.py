from django.shortcuts import render
from django.http import HttpRequest, HttpResponseRedirect
from core.models import Conversation
from core import services,services_dash
from django.urls import reverse
from core.forms import ChoiceForm
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.decorators import login_required


@login_required
def new_chat(request: HttpRequest):
    if request.method == 'POST':
        conversation_id = services.create_conversation(
            request.POST.get('answer'),
            request.user #当前用户
            )

        return HttpResponseRedirect(reverse('choice_chat',kwargs={'conversation_id': conversation_id}))
  
    return render(request, 'core/new_chat.html')
   
# get 显示choice，和表单， post，处理choice的答案，然后redirect到chat
@login_required
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
@login_required
def chat(request: HttpRequest, conversation_id: int):

    module_id = request.GET.get('module_id', "M01")

    if request.method == 'POST':
 
        
        action = request.POST.get('action')
        current_module_id = request.POST.get("current_module_id",module_id)

        if action == 'next':
            next_module_id =  services.handle_next(conversation_id,current_module_id)
            return HttpResponseRedirect(reverse('chat',kwargs={'conversation_id':conversation_id}) + 
                                        f'?module_id={next_module_id}'
                                        )
            
        elif action == 'answer':
            services.handle_answer(conversation_id,current_module_id)
            # 处理答案后，重定向回当前页面以显示答案,添加锚点重定向到答案区域
            return HttpResponseRedirect(
                reverse('chat', kwargs={'conversation_id': conversation_id}) + 
                f'?module_id={module_id}#answerArea'
            )

            
        elif action == 'Q&A':
            question = request.POST.get('question')
            services.handle_question(question, conversation_id,current_module_id)
            #添加锚点，重定向到答案区域
            return HttpResponseRedirect(
                reverse('chat', kwargs={'conversation_id': conversation_id}) + 
                f'?module_id={module_id}#qaArea'
            )

    #获取当前模块的学习计划及内容
    learning_plan = services.get_learning_plan(conversation_id)
    learning_content = services.get_learning_module(conversation_id, module_id)
    
    #获取当前模块的答疑以及进度信息
    conversation = Conversation.objects.get(id = conversation_id)
    current_qa_session = None
    for session in conversation.qa_sessions:
        if session.get('module_id') == module_id:
            current_qa_session = session
            break
        
    context = {
        'learning_plan': learning_plan,
        'learning_content': learning_content,
        'qa_session': current_qa_session,
        'conversation_id': conversation_id,
        'learning_progress': conversation.current_progress,#学习进度
        'completed_modules': conversation.completed_modules,#已完成学习模块
        }
    return render(request, 'core/chat.html', context)

@login_required
def index(request):
    #添加一个过滤条件
    conversations = Conversation.objects.filter(
        user=request.user,
        module_index_map__isnull=False
    ).exclude(module_index_map={})  # 排除空的module_index_map
    return render(request, 'core/index.html', {'conversations': conversations})

@login_required
def remove(request, conversation_id: int):
    Conversation.objects.get(id = conversation_id).delete()
    return HttpResponseRedirect(reverse('index'))
  
def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # 重定向到next参数指定的页面，如果没有则到首页
                next_url = request.GET.get('next', reverse('index'))
                return HttpResponseRedirect(next_url)
    else:
        form = AuthenticationForm()
    
    return render(request, 'core/login.html', {'form': form})

def register_view(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return HttpResponseRedirect(reverse('index'))
    else:
        form = UserCreationForm()
    
    return render(request, 'core/register.html', {'form': form})

def logout_view(request):
    logout(request)
    return HttpResponseRedirect(reverse('index'))


@login_required
def learning_dashboard(request):
    """学习仪表盘"""
    
    dashboard_data = services_dash.get_learning_dashboard_data(request.user)
    return render(request, 'core/dashboard.html', dashboard_data)