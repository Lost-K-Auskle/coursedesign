from django.db import models
from django.contrib.auth.models import User
from datetime import datetime

class UserProfile(models.Model):
    """用户个人资料扩展模型"""
    # 与User模型一对一关联
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    
    # 个性化字段
    bio = models.TextField(max_length=500, blank=True, verbose_name='个人简介')
    gender = models.CharField(max_length=10, choices=[('male', '男'), ('female', '女'), ('other', '其他')], blank=True, verbose_name='性别')
    avatar = models.BinaryField(blank=True, null=True, verbose_name='头像')  # 头像存储在数据库中
    avatar_content_type = models.CharField(max_length=100, blank=True, verbose_name='头像内容类型')  # 头像的MIME类型
    recycle_bin_days = models.IntegerField(default=7, verbose_name='回收站保管天数', help_text='最高为7天')  # 自定义回收站保管时间
    
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='创建时间')
    updated_at = models.DateTimeField(auto_now=True, verbose_name='更新时间')
    
    class Meta:
        verbose_name = '用户个人资料'
        verbose_name_plural = '用户个人资料'
    
    def __str__(self):
        return f"{self.user.username} 的个人资料"

class EmotionRecord(models.Model):
    """用户情感识别记录模型"""
    # 关联到用户
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='emotion_records')
    
    # 情感识别结果
    emotion = models.CharField(max_length=20, verbose_name='识别到的情感')
    
    # 识别置信度
    confidence = models.FloatField(default=0.0, verbose_name='识别置信度')
    
    # 图片相关信息 - 全部存储在数据库中
    image_name = models.CharField(max_length=255, verbose_name='图片名称')
    image_data = models.BinaryField(blank=True, null=True, verbose_name='图片数据')
    image_content_type = models.CharField(max_length=100, blank=True, verbose_name='图片MIME类型')
    
    # 识别时间
    created_at = models.DateTimeField(auto_now_add=True, verbose_name='识别时间')
    
    # 软删除相关字段
    is_deleted = models.BooleanField(default=False, verbose_name='是否已删除')
    deleted_at = models.DateTimeField(null=True, blank=True, verbose_name='删除时间')
    
    class Meta:
        verbose_name = '情感识别记录'
        verbose_name_plural = '情感识别记录'
        ordering = ['-created_at']  # 按时间倒序排列
    
    def __str__(self):
        return f"{self.user.username} - {self.emotion} ({self.created_at.strftime('%Y-%m-%d %H:%M:%S')})"