from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from core.services_knowledge import get_user_knowledge_data, search_knowledge_content

@login_required
def knowledge_library(request):
    """学习知识库主页"""
    knowledge_data = get_user_knowledge_data(request.user)
    
    # 添加统计卡片数据
    knowledge_data['stats'] = [
        {'value': knowledge_data['total_topics'], 'label': '学习主题', 'color_class': 'bg-primary'},
        {'value': knowledge_data['completed_modules'], 'label': '完成模块', 'color_class': 'bg-success'},
        {'value': knowledge_data['total_modules'], 'label': '总模块', 'color_class': 'bg-info'},
        {'value': f"{knowledge_data['completion_rate']:.0f}%", 'label': '完成率', 'color_class': 'bg-warning'}
    ]
    
    return render(request, 'core/knowledge_library.html', knowledge_data)

@login_required
def knowledge_search(request):
    """知识搜索页面"""
    
    query = request.GET.get('q', '')
    search_results = search_knowledge_content(request.user, query)
    
    context = {
        'search_results': search_results,
        'query': query,
        'results_count': len(search_results)
    }
    
    return render(request, 'core/knowledge_search.html', context)