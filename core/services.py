# Please install OpenAI SDK first: `pip3 install openai`
import os, re
from openai import OpenAI
from core.models import Conversation
from django.utils import timezone
from pathlib import Path
from django.conf import settings

DEEPSEEK_API_KEY = "sk-179e4c17fe8c40418956ed4ab9ad7642"
DEEPSEEK_API_URL = "https://api.deepseek.com"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)

def handle_next(conversation_id: int):
    conversation = Conversation.objects.get(id = conversation_id)

    content = "进入下一阶段学习"
    conversation.history.append({"role": "user", "content": content})
    reply = get_deepseek_response(conversation.history)
    conversation.history.append({"role": "assistant", "content": reply})
    conversation.save()
     
     
def handle_answer(answer, conversation_id: int):
    conversation = Conversation.objects.get(id = conversation_id)

    content = f'的答案是{answer}, 请根据答案生成学习计划'
    conversation.history.append({"role": "user", "content": content})
    reply = get_deepseek_response(conversation.history)
    conversation.history.append({"role": "assistant", "content": reply})
    conversation.save()

def handle_question(question, conversation_id: int):
    conversation = Conversation.objects.get(id = conversation_id)

    content = f'的答案是{question}, 请根据答案生成学习计划'
    conversation.history.append({"role": "user", "content": content})
    reply = get_deepseek_response(conversation.history)
    conversation.history.append({"role": "assistant", "content": reply})
    conversation.save()

def handle_choice_answers(choice_answers, conversation_id: int):
    conversation = Conversation.objects.get(id = conversation_id)

    content = f'的答案是{choice_answers}, 请根据答案生成学习计划'
    conversation.history.append({"role": "user", "content": content})
    reply = get_deepseek_response(conversation.history)
    conversation.history.append({"role": "assistant", "content": reply})
    conversation.save()



def create_conversation(answer: str)-> int:
        
        prompt = get_prompt_text()
        content = f'你是我的学习助手，你需要辅助我完成{answer}的学习' + prompt
            

        history = [
        {"role": "system", "content": content},
        {"role": "user", "content": "阶段一开始"}
        ]

        choice_content = get_deepseek_response(history)


        history.append({"role": "assistant", "content": choice_content})
        conversation = Conversation.objects.create(
            title = answer,
            history = history,
            created_at = timezone.now(),
            updated_at = timezone.now(),
        )
        return conversation.id

def get_deepseek_response(messages):

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=messages,
        stream=False
    )

    return response.choices[0].message.content





def get_choice_data(conversation_id: int):
    choice_content = Conversation.objects.get(pk = conversation_id).history[-1]['content']
    print(choice_content)
    
    parsed_data = []

    # 1. 匹配整个 <question> 块
    question_pattern = re.compile(r'<question>([\s\S]*?)</question>')
    
    # 2. 匹配 <label> 内容
    label_pattern = re.compile(r'<label>(.*?)</label>')
    
    # 3. 匹配 <option> 属性和内容
    # 捕获 value 属性值 (A, B, C...) 和 标签内容
    option_pattern = re.compile(r'<option\s+value="([A-Z])">(.*?)</option>')

    # 遍历所有 <question> 块
    for q_match in question_pattern.finditer(choice_content):
        q_block = q_match.group(1) # 获取 <question> 和 </question> 之间的内容
        
        # 提取 label
        label_match = label_pattern.search(q_block)
        label = label_match.group(1).strip() if label_match else "未知问题"
        
        # 提取 choices
        choices = []
        for opt_match in option_pattern.finditer(q_block):
            value = opt_match.group(1) # 例如：'A'
            display_text = opt_match.group(2).strip() # 例如：'完全零基础，没写过任何代码'
            choices.append((value, display_text))
            
        if label and choices:
            parsed_data.append({
                'label': label,
                'choices': choices,
            })

    return parsed_data  


def get_prompt_text(filename: str = 'prompt.txt') -> str:

    prompt_path = Path(settings.BASE_DIR) / 'core' / filename
    try:
        with open(prompt_path, 'r', encoding='utf-8') as f:
            prompt_content = f.read()
        return prompt_content
    
    except FileNotFoundError:
        print(f"错误：未找到提示词文件: {filename}")
        return ""
