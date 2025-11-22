# Please install OpenAI SDK first: `pip3 install openai`
import os, re
from openai import OpenAI
from core.models import Conversation
from django.utils import timezone
from pathlib import Path
from django.conf import settings
from typing import Dict, List

DEEPSEEK_API_KEY = "sk-179e4c17fe8c40418956ed4ab9ad7642"
DEEPSEEK_API_URL = "https://api.deepseek.com"
client = OpenAI(api_key=DEEPSEEK_API_KEY, base_url=DEEPSEEK_API_URL)

def handle_next(conversation_id: int,current_module_id:str = None):
    conversation = Conversation.objects.get(id = conversation_id)

    #只要点击下一课就标记当前模块为学习完成
    if current_module_id and current_module_id not in conversation.completed_modules:
        conversation.completed_modules.append(current_module_id)
    
    #生成下一模块的学习内容
    content = "学习"
    conversation.history.append({"role": "user", "content": content})
    reply = get_deepseek_response(conversation.history)
    conversation.history.append({"role": "assistant", "content": reply})
    next_module_id = get_module_id(reply)
    history_index = len(conversation.history) - 1
    
    #更新模块索引映射
    conversation.module_index_map[next_module_id] = {'content_index': history_index}
    
    #更新进度
    learning_plan = get_learning_plan(conversation_id)
    total_modules = len(learning_plan)
    completed_count = len(conversation.completed_modules)
    
    
    if total_modules > 0 :
        conversation.current_progress = (completed_count / total_modules) * 100
        print(f"进度更新: {completed_count}/{total_modules} = {conversation.current_progress}%")
    else :
        conversation.current_progress = 0;

    conversation.save()
    return next_module_id  
     
def handle_answer(conversation_id: int,current_module_id:str):
    
    conversation = Conversation.objects.get(id=conversation_id)
    
    # 确保当前生成答案是关联到当前模块的
    content = '请给出模块{current_module_id}课后习题的参考答案和详细解析，不要使用任何XML标签，直接返回纯文本答案。'
    conversation.history.append({
        "role": "user", 
        "content": content,
    })
    print(f"开始为模块 {current_module_id} 生成答案")
    print(f"请求内容: {content}")
    reply = get_deepseek_response(conversation.history)
    conversation.history.append({
        "role": "assistant",
        "content": reply,
        })
    
    #记录答案位置
    answer_index = len(conversation.history) - 1
    
    # 更新模块索引映射，确保使用字典格式
    if current_module_id in conversation.module_index_map:
        conversation.module_index_map[current_module_id]['answer_index'] = answer_index
    else:
        # 如果模块索引映射中还没有这个模块，创建一个基础记录
        conversation.module_index_map[current_module_id] = {
            'answer_index': answer_index
        }
    
    print(f"已为模块 {current_module_id} 生成答案，位置: {answer_index}")
    conversation.save()
    
def handle_question(question, conversation_id: int,current_module_id: str):
    conversation = Conversation.objects.get(id = conversation_id)
    
    # 获取或创建当前模块的答疑会话
    current_session = None
    session_index = -1
    
    for i, session in enumerate(conversation.qa_sessions):
        if session.get('module_id') == current_module_id:
            current_session = session
            session_index = i
            break
    
    # 如果没有找到当前模块的答疑会话，创建一个新的
    if not current_session:
        current_session = {
            'module_id': current_module_id,
            'qa_pairs': [],  # 存答疑对话
            'created_at': timezone.now().isoformat()
        }
        conversation.qa_sessions.append(current_session)
        session_index = len(conversation.qa_sessions) - 1
        
    # 将用户问题添加到历史记录中
    question_record = {"role": "user", "content": f"答疑，请直接回答以下问题，不要使用XML格式，不要生成学习内容：{question}"}
    conversation.history.append(question_record)
    
    
    reply = get_deepseek_response(conversation.history)
    answer_record = {"role": "assistant", "content": reply}
    conversation.history.append(answer_record)
    
    # 保存答疑会话
    qa_pair = {
        'question': question,
        'answer': reply,
        'timestamp': timezone.now().isoformat()
    }
    
    current_session['qa_pairs'].append(qa_pair)
    conversation.qa_sessions[session_index] = current_session
    
    conversation.save()
    print(f"答疑记录已保存到模块 {current_module_id} 的会话中")



def handle_choice_answers(choice_answers, conversation_id: int):
    conversation = Conversation.objects.get(id = conversation_id)

    content = f'的答案是{choice_answers}, 阶段二开始,请根据答案生成学习计划, 在下一段对话中，阶段三开始'
    conversation.history.append({"role": "user", "content": content})
    reply = get_deepseek_response(conversation.history)
    conversation.history.append({"role": "assistant", "content": reply})

    conversation.save()
    handle_next(conversation_id,None)




def create_conversation(answer: str,user)-> int:
        
        prompt = get_prompt_text()
        content = f'你是我的学习助手，你需要辅助我完成{answer}的学习' + prompt
            

        history = [
        {"role": "system", "content": content},
        {"role": "user", "content": "阶段一开始"}
        ]

        choice_content = get_deepseek_response(history)


        history.append({"role": "assistant", "content": choice_content})
        conversation = Conversation.objects.create(
            user = user,#关联当前用户
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



def get_learning_plan(conversation_id: int) -> List[Dict[str, str]]:

    conversation = Conversation.objects.get(id = conversation_id)
    xml_string = conversation.history[4]['content'].replace('\n', '')

    """
    从包含 <plan>...<module> 结构的 XML 字符串中提取学习计划目录。
    
    Args:
        xml_string: 包含学习计划结构的原始字符串。
        
    Returns:
        一个列表，每个元素是一个字典 {'id': 'MXX', 'title': '模块标题'}。
    """
    extracted_plan = []
    
    # 正则表达式说明：
    # r'<module>.*?</module>' 匹配一个完整的 <module> 块。
    # 匹配是惰性的 (.*?)，以防止匹配到下一个 <module> 块之后的内容。
    module_pattern = re.compile(r'<module>(.*?)</module>')
    
    # 匹配 <module_id> 和 <module_title> 的内容
    id_pattern = re.compile(r'<module_id>(.*?)</module_id>')
    title_pattern = re.compile(r'<module_title>(.*?)</module_title>')

    # 1. 查找所有 <module> 块
    module_blocks = module_pattern.finditer(xml_string)
    
    for block_match in module_blocks:
        module_block_content = block_match.group(1).strip()
        
        # 2. 从每个块中提取 ID
        id_match = id_pattern.search(module_block_content)
        module_id = id_match.group(1).strip() if id_match else "N/A"
        
        # 3. 从每个块中提取 Title
        title_match = title_pattern.search(module_block_content)
        module_title = title_match.group(1).strip() if title_match else "无标题"
        
        # 4. 存储结果
        extracted_plan.append({
            'id': module_id,
            'title': module_title
        })

    return extracted_plan



def get_learning_module(conversation_id: int, module_id: str) -> str:

    conversation = Conversation.objects.get(id = conversation_id)
    module_info = conversation.module_index_map.get(module_id)
    print(f"模块索引映射: {conversation.module_index_map}")
    print(f"module_info结构: {module_info}")
    if module_info is None:
        return get_default_module_content()
    
    content_index = module_info.get('content_index')
    xml_string = conversation.history[content_index]['content']
    """
    从阶段三的学习内容 XML 字符串中提取当前模块信息、内容、习题和进度目录。
    
    Args:
        xml_string: 包含学习内容和进度地图的原始 XML 字符串。
        
    Returns:
        一个字典，包含 'module_info', 'content', 'exercise', 'progress_map' 等键。
    """
    
    result = {
        'module_info': {},
        'content': '',
        'exercise': '',
        'progress_map': [],
        'answer': ''
    }
    
    # --------------------------------------------------
    # 1. 提取 <current_module> 信息 (ID 和 Title)
    # --------------------------------------------------
    current_module_match = re.search(r'<current_module>([\s\S]*?)</current_module>', xml_string)
    if current_module_match:
        module_block = current_module_match.group(1)
        id_match = re.search(r'<module_id>(.*?)</module_id>', module_block)
        title_match = re.search(r'<module_title>(.*?)</module_title>', module_block)
        
        result['module_info'] = {
            'id': id_match.group(1).strip() if id_match else 'N/A',
            'title': title_match.group(1).strip() if title_match else 'N/A'
        }

    # --------------------------------------------------
    # 2. 提取 <content> 和 <exercise>
    # --------------------------------------------------
    # (?s) 启用 DOTALL 模式，让 . 匹配包括换行符在内的所有字符
    content_match = re.search(r'(?s)<content>(.*?)</content>', xml_string)
    exercise_match = re.search(r'(?s)<exercise>(.*?)</exercise>', xml_string)
    
    if content_match:
        result['content'] = content_match.group(1).strip()
        
    if exercise_match:
        result['exercise'] = exercise_match.group(1).strip()
        
    # --------------------------------------------------
    # 3. 提取 <progress_map> (目录)
    # --------------------------------------------------
    progress_map_match = re.search(r'(?s)<progress_map>([\s\S]*?)</progress_map>', xml_string)
    if progress_map_match:
        map_content = progress_map_match.group(1)
        # 匹配所有 <map_item ...> 标签
        # r'<map_item\s+id="([^"]+)"\s+status="([^"]+)">(.*?)</map_item>'
        item_pattern = re.compile(r'<map_item\s+id="([^"]+)"\s+status="([^"]+)">(.*?)</map_item>')
        
        for item_match in item_pattern.finditer(map_content):
            result['progress_map'].append({
                'id': item_match.group(1),
                'status': item_match.group(2),
                'title': item_match.group(3).strip()
            })
            
        #获取答案
        result['answer'] = find_answer_for_module(conversation, module_id) 
        print(result['exercise'])
    return result

def find_answer_for_module(conversation, module_id: str) -> str:
    """获取各模块的答案"""
    module_info = conversation.module_index_map.get(module_id, {})
    
    # 从记录的答案索引获取
    if isinstance(module_info, dict) and 'answer_index' in module_info:
        answer_index = module_info['answer_index']
        if answer_index < len(conversation.history):
            return conversation.history[answer_index]['content']
    
    # 如果没有记录答案索引，使用模块标识搜索
    module_patterns = [
        f"模块{module_id}课后习题",
        f"模块 {module_id} 课后习题", 
        f"模块{module_id}参考答案",
        f"模块 {module_id} 参考答案"
    ]
    
    for i in range(len(conversation.history)-1, -1, -1):
        message = conversation.history[i]
        if message['role'] == 'assistant':
            content = message['content']
            for pattern in module_patterns:
                if pattern in content:
                    return content
    
    return ""

def get_default_module_content() -> Dict[str, any]:
    """当模块不存在时返回默认内容"""
    return {
        'module_info': {'id': 'M01', 'title': '默认模块'},
        'content': '内容加载中...',
        'exercise': '习题加载中...',
        'progress_map': [],
        'answer': '答案加载中...'
    }


def get_module_id(xml_fragment: str):

    id_pattern = re.compile(r'<module_id>(.*?)</module_id>')
    match = id_pattern.search(xml_fragment)
    if match:
        return match.group(1).strip()
