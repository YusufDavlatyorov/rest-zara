from django.db import models

class ChatHistory(models.Model):
    session_id = models.CharField(max_length=255) # для идентификации юзера
    role = models.CharField(max_length=20)       # user или assistant
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
