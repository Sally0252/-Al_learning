from core import views
from django.urls import path

urlpatterns = [
    path('chat/<int:conversation_id>',views.chat, name = 'chat'),
    path('index', views.index, name = 'index'),
    path('new_chat', views.new_chat, name = 'new_chat'),
    path('choice_chat/<int:conversation_id>', views.choice_chat, name = 'choice_chat'),

]   
