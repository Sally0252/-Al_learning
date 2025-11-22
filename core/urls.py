from core import views,views_knowledge
from django.urls import path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name='index'),
    path('chat/<int:conversation_id>',views.chat, name = 'chat'),
    path('index', views.index, name = 'index'),
    path('accounts/login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('accounts/logout/', views.logout_view, name='logout'),
    path('new_chat', views.new_chat, name = 'new_chat'),
    path('choice_chat/<int:conversation_id>', views.choice_chat, name = 'choice_chat'),
    path('remove/<int:conversation_id>', views.remove, name = 'remove'),
    path('dashboard/', views.learning_dashboard, name='dashboard'),
    path('knowledge-library/', views_knowledge.knowledge_library, name='knowledge_library'),
    path('knowledge-search/', views_knowledge.knowledge_search, name='knowledge_search'),

]   
