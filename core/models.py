from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Conversation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # 关联用户
    title = models.CharField(max_length=200)
    history = models.JSONField(default=list)
    module_index_map = models.JSONField(default=dict)
    
    qa_sessions = models.JSONField(default=list)  # 改为答疑会话，每个模块一个会话
    
    # 新增进度跟踪字段
    completed_modules = models.JSONField(default=list)  # 已完成的模块ID列表
    current_progress = models.FloatField(default=0.0)   # 当前进度百分比 0-100
    
    created_at = models.DateTimeField()
    updated_at = models.DateTimeField()
    
    def __str__(self):
        return f"{self.title} - {self.user.username}"


