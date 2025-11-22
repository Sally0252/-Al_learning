from django.db.models import Q
from core.models import Conversation
import re

def get_user_knowledge_data(user):
    """获取用户知识库数据"""
    conversations = Conversation.objects.filter(
        user=user
    ).exclude(module_index_map={}).order_by('-updated_at')
    
    # 计算统计
    total_topics = conversations.count()
    total_modules = sum(len(conv.module_index_map) for conv in conversations)
    completed_modules = sum(len(conv.completed_modules) for conv in conversations)
    completion_rate = (completed_modules / total_modules * 100) if total_modules > 0 else 0
    
    # 构建知识概览
    knowledge_overview = []
    for conv in conversations:
        if conv.completed_modules:
            overview = {
                'id': conv.id,
                'title': conv.title,
                'progress': conv.current_progress,
                'completed_count': len(conv.completed_modules),
                'total_count': len(conv.module_index_map),
                'last_updated': conv.updated_at,
                'key_concepts': extract_key_concepts(conv),
                'module_titles': get_module_titles(conv)
            }
            knowledge_overview.append(overview)
    
    return {
        'knowledge_overview': knowledge_overview,
        'total_topics': total_topics,
        'total_modules': total_modules,
        'completed_modules': completed_modules,
        'completion_rate': completion_rate
    }

def extract_key_concepts(conversation):
    """从对话历史中提取关键概念"""
    key_concepts = []
    important_keywords = ['概念', '定义', '原理', '方法', '技巧', '步骤', '核心', '关键']
    
    for message in conversation.history[:10]:
        if message['role'] == 'assistant':
            content = message['content']
            
            for keyword in important_keywords:
                if keyword in content:
                    sentences = content.split('。')
                    for sentence in sentences:
                        if keyword in sentence and len(sentence) > 10 and len(sentence) < 100:
                            clean_sentence = sentence.strip().replace('\n', ' ')
                            if clean_sentence not in key_concepts:
                                key_concepts.append(clean_sentence)
                                break
                    
                    if len(key_concepts) >= 3:
                        return key_concepts
    
    return key_concepts[:3]

def get_module_titles(conversation):
    """获取模块标题列表"""
    try:
        learning_plan = extract_learning_plan(conversation)
        return [module['title'] for module in learning_plan[:4]]
    except:
        return [f"模块 {i+1}" for i in range(min(4, len(conversation.module_index_map)))]

def extract_learning_plan(conversation):
    """从对话历史中提取学习计划"""
    for message in conversation.history:
        if message['role'] == 'assistant' and '<plan>' in message['content']:
            return parse_learning_plan(message['content'])
    return []

def parse_learning_plan(xml_content):
    """解析学习计划XML"""
    plan = []
    module_pattern = re.compile(r'<module>(.*?)</module>', re.DOTALL)
    id_pattern = re.compile(r'<module_id>(.*?)</module_id>')
    title_pattern = re.compile(r'<module_title>(.*?)</module_title>')
    
    for module_match in module_pattern.finditer(xml_content):
        module_block = module_match.group(1)
        id_match = id_pattern.search(module_block)
        title_match = title_pattern.search(module_block)
        
        if id_match and title_match:
            plan.append({
                'id': id_match.group(1).strip(),
                'title': title_match.group(1).strip()
            })
    
    return plan

def search_knowledge_content(user, query):
    """搜索知识内容"""
    conversations = Conversation.objects.filter(user=user)
    
    if query:
        conversations = conversations.filter(
            Q(title__icontains=query) | 
            Q(history__icontains=query)
        )
    
    search_results = []
    for conv in conversations:
        relevance = 0
        if query.lower() in conv.title.lower():
            relevance += 10
        if query in str(conv.history):
            relevance += 1
        
        if relevance > 0:
            search_results.append({
                'conversation': conv,
                'relevance': relevance,
                'matches': find_content_matches(conv, query)
            })
    
    # 按相关度排序
    search_results.sort(key=lambda x: x['relevance'], reverse=True)
    return search_results

def find_content_matches(conversation, query):
    """在对话历史中查找匹配的内容"""
    matches = []
    
    for i, message in enumerate(conversation.history[:20]):
        if query.lower() in str(message).lower():
            content = str(message)[:200]
            matches.append({
                'index': i,
                'preview': content
            })
            
            if len(matches) >= 3:
                break
    
    return matches