
from core.models import Conversation
# 学习仪表盘相关服务函数
def get_learning_dashboard_data(user):
    """获取学习仪表盘数据"""
    conversations = Conversation.objects.filter(user=user)
    
    total_conversations = conversations.count()
    completed_conversations = conversations.filter(current_progress=100).count()
    in_progress_conversations = conversations.filter(current_progress__gt=0, current_progress__lt=100).count()
    
    learning_topics_with_percent = analyze_learning_topics(conversations)
    chart_data = prepare_chart_data(conversations, learning_topics_with_percent)
    
    return {
        'total_conversations': total_conversations,
        'completed_conversations': completed_conversations,
        'in_progress_conversations': in_progress_conversations,
        'chart_data': chart_data,
        'learning_topics_with_percent': learning_topics_with_percent,
    }

def analyze_learning_topics(conversations):
    """分析学习主题分类"""
    learning_topics = {}
    
    for conv in conversations:
        if conv.title and conv.module_index_map:
            topic = normalize_topic_title(conv.title)
            if len(topic) > 15:
                topic = topic[:15] + "..."
            learning_topics[topic] = learning_topics.get(topic, 0) + 1
    
    return calculate_topic_percentages(learning_topics)

def normalize_topic_title(title):
    """规范化主题标题"""
    prefixes = ["学习", "掌握", "了解", "理解"]
    for prefix in prefixes:
        if prefix in title:
            title = title.replace(prefix, "").strip()
            break
    return title

def calculate_topic_percentages(learning_topics):
    """计算主题百分比"""
    learning_topics_with_percent = {}
    total_topics = sum(learning_topics.values())
    
    for topic, count in learning_topics.items():
        percentage = (count / total_topics * 100) if total_topics > 0 else 0
        learning_topics_with_percent[topic] = {
            'count': count,
            'percentage': round(percentage, 1)
        }
    
    return learning_topics_with_percent

def prepare_chart_data(conversations, learning_topics_with_percent):
    """准备图表数据"""
    topics_data = {
        'topics': list(learning_topics_with_percent.keys()),
        'counts': [data['count'] for data in learning_topics_with_percent.values()],
        'percentages': [data['percentage'] for data in learning_topics_with_percent.values()],
    }
    
    progress_data = []
    for conv in conversations:
        if conv.module_index_map:
            progress_data.append({
                'title': conv.title[:20] + '...' if len(conv.title) > 20 else conv.title,
                'progress': conv.current_progress,
                'completed_modules': len(conv.completed_modules),
                'total_modules': len(conv.module_index_map),
                'id': conv.id
            })
    
    return {**topics_data, 'progress_data': progress_data}