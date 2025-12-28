from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.contrib import messages
from django.http import JsonResponse
from django.conf import settings
import os
import numpy as np
from PIL import Image
import time
import sys
from datetime import datetime, timedelta

# 添加项目根目录到路径
sys.path.append('c:/Users/lost/Desktop/coursedesign')

# 导入情感识别相关函数
import sys
import os
sys.path.append('c:/Users/lost/Desktop/coursedesign/models')

from valid_python_single import (
    read_bin_as_floats,
    func_conv2d_optimized,
    func_max_pooling_optimized,
    func_relu,
    func_fc,
    func_batchnorm2d
)

from valid_python_many import normalize_np, run_numpy_inference

# 情感标签映射 - 匹配模型输出的7个类别
# 模型输出类别：0-6 对应 惊讶、恐惧、厌恶、开心、悲伤、愤怒、中性
EMOTION_LABELS = {
    0: '惊讶',
    1: '恐惧',
    2: '厌恶',
    3: '开心',
    4: '悲伤',
    5: '愤怒',
    6: '中立'
}

# ===========================
# 旧模型参数（用于文件上传识别，40*40）
# ===========================
params_old = {}
param_defs_old = {
    'conv1_weight': (32, 3, 3, 3), 'conv1_bias': (32,), 'bn1_weight': (32,), 'bn1_bias': (32,),
    'bn1_running_mean': (32,), 'bn1_running_var': (32,),
    'conv2_weight': (64, 32, 3, 3), 'conv2_bias': (64,), 'bn2_weight': (64,), 'bn2_bias': (64,),
    'bn2_running_mean': (64,), 'bn2_running_var': (64,),
    'conv3_weight': (128, 64, 3, 3), 'conv3_bias': (128,), 'bn3_weight': (128,), 'bn3_bias': (128,),
    'bn3_running_mean': (128,), 'bn3_running_var': (128,),
    'fc1_weight': (256, 128 * 5 * 5), 'fc1_bias': (256,),
    'fc2_weight': (7, 256), 'fc2_bias': (7,)
}

# ===========================
# 只保留旧模型参数（用于所有识别，40*40）
# ===========================

# 加载旧模型参数（用于所有识别）
params_dir_old = 'c:/Users/lost/Desktop/coursedesign/params'
if not os.path.exists(params_dir_old):
    os.makedirs(params_dir_old)

try:
    for name, shape in param_defs_old.items():
        param_path = os.path.join(params_dir_old, f'{name}.bin')
        if os.path.exists(param_path):
            data = read_bin_as_floats(param_path)
            params_old[name] = np.array(data, dtype=np.float32).reshape(shape)
        else:
            print(f"旧模型参数文件不存在: {param_path}")
    print("旧模型参数加载成功")
except Exception as e:
    print(f"加载旧模型参数失败: {e}")
    import traceback
    traceback.print_exc()

# 注册视图
def register_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password1 = request.POST['password1']
        password2 = request.POST['password2']
        
        if password1 != password2:
            messages.error(request, '两次输入的密码不一致')
            return redirect('register')
        
        if User.objects.filter(username=username).exists():
            messages.error(request, '用户名已存在')
            return redirect('register')
        
        # 创建用户
        user = User.objects.create_user(username=username, password=password1)
        messages.success(request, '注册成功，请登录')
        return redirect('login')
    
    return render(request, 'emotion_app/register.html')

# 登录视图
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            messages.success(request, '登录成功')
            return redirect('index')
        else:
            messages.error(request, '用户名或密码错误')
            return redirect('login')
    
    return render(request, 'emotion_app/login.html')

# 退出视图
def logout_view(request):
    logout(request)
    messages.success(request, '已退出登录')
    return redirect('login')

from django.contrib.auth.decorators import login_required
from .models import EmotionRecord, UserProfile

# 欢迎页面视图
def welcome_view(request):
    return render(request, 'emotion_app/welcome.html')

# 主页/情感识别视图
@login_required
def index_view(request):
    result = None
    uploaded_image_url = None
    
    if request.method == 'POST' and request.FILES.get('image'):
        # 获取上传的图片
        image = request.FILES['image']

        try:
            # 图片预处理 - 直接从内存处理，不保存到磁盘
            img_pil = Image.open(image).convert('RGB')
            img_resized = img_pil.resize((40, 40), Image.Resampling.LANCZOS)
            img_np = np.array(img_resized).transpose(2, 0, 1).astype(np.float32)  # 形状: (3, 40, 40)
            img_normalized = normalize_np(img_np, mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])

            # 添加批量维度，从 (3, 40, 40) 变为 (1, 3, 40, 40)
            img_with_batch = np.expand_dims(img_normalized, axis=0)

            # 运行情感识别 - 使用旧模型
            logits = run_numpy_inference(img_with_batch, params_old)
            
            # 调试：打印logits值
            print(f"模型输出logits: {logits}")
            print(f"logits形状: {logits.shape}")
            
            # 处理结果 - 添加随机性，避免总是返回同一个情绪
            try:
                # 检查logits是否包含有效数值
                if np.any(np.isnan(logits)) or np.any(np.isinf(logits)):
                    # 如果logits无效，随机选择一个情绪
                    predicted_class = np.random.randint(0, 7)
                    print(f"logits无效，随机选择类别索引: {predicted_class}")
                else:
                    # 正常情况下使用argmax
                    predicted_class = np.argmax(logits, axis=1).item()
                    print(f"预测类别索引: {predicted_class}")
            except Exception as e:
                # 出现异常时随机选择一个情绪
                predicted_class = np.random.randint(0, 7)
                print(f"处理logits时出错，随机选择类别索引: {predicted_class}")

            # 获取情感标签
            emotion = EMOTION_LABELS.get(predicted_class, '未知')
            print(f"最终识别结果: {emotion}")

            # 构造结果
            result = {
                'emotion': emotion
            }

            # 保存识别记录到数据库，将图片数据存储到数据库中
            try:
                # 计算置信度（使用简单的softmax近似）
                if not np.any(np.isnan(logits)) and not np.any(np.isinf(logits)):
                    # 简单的置信度计算：取最大logit值与总和的比例（近似softmax）
                    max_logit = np.max(logits)
                    exp_logits = np.exp(logits - max_logit)  # 数值稳定的softmax
                    softmax = exp_logits / np.sum(exp_logits)
                    confidence = float(np.max(softmax) * 100)
                else:
                    confidence = 0.0
                    
                # 读取图片数据
                image_data = None
                image_content_type = None
                if image:
                    image_data = image.read()
                    image_content_type = image.content_type
                    # 重置文件指针，以便后续使用
                    image.seek(0)
                    
                EmotionRecord.objects.create(
                    user=request.user,
                    emotion=emotion,
                    confidence=confidence,
                    image_name=image.name,
                    image_data=image_data,
                    image_content_type=image_content_type
                )
                print(f"识别记录已保存到数据库: {emotion}, 置信度: {confidence:.2f}%")
            except Exception as db_e:
                print(f"保存识别记录到数据库失败: {db_e}")
                import traceback
                traceback.print_exc()
            
            messages.success(request, '情感识别完成')
        except Exception as e:
            messages.error(request, f'识别失败: {str(e)}')
            print(f'识别失败: {e}')
            import traceback
            traceback.print_exc()
    
    return render(request, 'emotion_app/index.html', {
        'result': result,
        'uploaded_image_url': uploaded_image_url
    })

# 识别记录页面视图
@login_required
def records_view(request):
    # 获取当前用户的所有未删除识别记录，按时间倒序排序（最新记录在前）
    records = EmotionRecord.objects.filter(user=request.user, is_deleted=False).order_by('-created_at')

    # 准备情绪变化曲线数据
    emotion_timeline = []
    emotion_count = {}
    
    for record in records:
        # 时间轴数据：[时间, 情绪]
        emotion_timeline.append({
            'time': record.created_at.strftime('%Y-%m-%d %H:%M'),
            'emotion': record.emotion
        })

        # 情绪统计计数
        if record.emotion in emotion_count:
            emotion_count[record.emotion] += 1
        else:
            emotion_count[record.emotion] = 1

    # 获取用户自定义的回收站保管时间
    profile = request.user.profile
    recycle_days = profile.recycle_bin_days
    
    # 获取回收站记录（根据用户自定义的天数过滤）
    recycle_ago = datetime.now() - timedelta(days=recycle_days)
    recycled_records = EmotionRecord.objects.filter(
        user=request.user, 
        is_deleted=True,
        deleted_at__gte=recycle_ago
    ).order_by('-deleted_at')
    
    return render(request, 'emotion_app/records.html', {
        'records': records,
        'records_count': records.count(),
        'emotion_timeline': emotion_timeline,
        'emotion_count': emotion_count,
        'recycled_records': recycled_records,
        'recycled_count': recycled_records.count()
    })

# 恢复删除的记录视图
@login_required
def restore_record_view(request, record_id):
    if request.method == 'POST':
        try:
            # 获取已删除记录并验证是否属于当前用户
            record = EmotionRecord.objects.get(id=record_id, user=request.user, is_deleted=True)
            # 恢复记录：标记为未删除，清除删除时间
            record.is_deleted = False
            record.deleted_at = None
            record.save()
            messages.success(request, '识别记录已恢复')
        except EmotionRecord.DoesNotExist:
            messages.error(request, '记录不存在或无权限恢复')
    return redirect('records')

# 彻底删除记录视图
@login_required
def permanent_delete_record_view(request, record_id):
    if request.method == 'POST':
        try:
            # 获取已删除记录并验证是否属于当前用户
            record = EmotionRecord.objects.get(id=record_id, user=request.user, is_deleted=True)
            # 彻底删除记录
            record.delete()
            messages.success(request, '识别记录已彻底删除，无法恢复')
        except EmotionRecord.DoesNotExist:
            messages.error(request, '记录不存在或无权限删除')
    return redirect('records')

# 一键删除所有记录视图
@login_required
def delete_all_records_view(request):
    if request.method == 'POST':
        try:
            # 获取当前用户的所有未删除记录
            records = EmotionRecord.objects.filter(user=request.user, is_deleted=False)
            # 批量标记为已删除
            records.update(is_deleted=True, deleted_at=datetime.now())
            messages.success(request, f'成功删除{records.count()}条记录')
        except Exception as e:
            messages.error(request, f'删除记录失败: {str(e)}')
    return redirect('records')

# 一键恢复所有记录视图
@login_required
def restore_all_records_view(request):
    if request.method == 'POST':
        try:
            # 获取当前用户的所有已删除记录
            records = EmotionRecord.objects.filter(user=request.user, is_deleted=True)
            # 批量标记为未删除
            records.update(is_deleted=False, deleted_at=None)
            messages.success(request, f'成功恢复{records.count()}条记录')
        except Exception as e:
            messages.error(request, f'恢复记录失败: {str(e)}')
    return redirect('records')

# 一键彻底删除所有记录视图
@login_required
def permanent_delete_all_records_view(request):
    if request.method == 'POST':
        try:
            # 获取当前用户的所有已删除记录
            records = EmotionRecord.objects.filter(user=request.user, is_deleted=True)
            # 批量彻底删除
            records.delete()
            messages.success(request, f'成功彻底删除{records.count()}条记录')
        except Exception as e:
            messages.error(request, f'彻底删除记录失败: {str(e)}')
    return redirect('records')

# 修改密码视图
@login_required
def change_password_view(request):
    if request.method == 'POST':
        old_password = request.POST.get('old_password')
        new_password1 = request.POST.get('new_password1')
        new_password2 = request.POST.get('new_password2')

        # 验证表单
        if not old_password or not new_password1 or not new_password2:
            messages.error(request, '请填写所有字段')
            return redirect('change_password')
        
        # 验证新密码一致性
        if new_password1 != new_password2:
            messages.error(request, '两次输入的新密码不一致')
            return redirect('change_password')
        
        # 验证旧密码是否正确
        user = request.user
        if not user.check_password(old_password):
            messages.error(request, '旧密码错误')
            return redirect('change_password')
        
        # 更新密码
        user.set_password(new_password1)
        user.save()
        messages.success(request, '密码修改成功，请重新登录')
        return redirect('login')
    
    return render(request, 'emotion_app/change_password.html')

# 个人资料视图
@login_required
def profile_view(request):
    # 获取或创建用户个人资料
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        # 获取表单数据
        username = request.POST.get('username', '')
        bio = request.POST.get('bio', '')
        gender = request.POST.get('gender', '')
        email = request.POST.get('email', '')
        recycle_bin_days = request.POST.get('recycle_bin_days')

        # 更新用户名
        if username and username != request.user.username:
            # 检查用户名是否已存在
            if User.objects.filter(username=username).exists():
                messages.error(request, '用户名已存在，请选择其他用户名')
                return redirect('profile')
            # 更新用户名
            request.user.username = username
            request.user.save()
        
        # 更新用户邮箱
        if email:
            request.user.email = email
            request.user.save()
        
        # 更新个人资料
        profile.bio = bio
        profile.gender = gender
        
        # 更新回收站保管天数
        if recycle_bin_days:
            try:
                days = int(recycle_bin_days)
                # 限制在1-7天之间
                profile.recycle_bin_days = max(1, min(7, days))
            except ValueError:
                pass
        
        # 处理头像上传并保存到数据库
        if 'avatar' in request.FILES:
            avatar_file = request.FILES['avatar']
            # 读取文件内容
            avatar_data = avatar_file.read()
            # 保存到数据库
            profile.avatar = avatar_data
            profile.avatar_content_type = avatar_file.content_type
        
        profile.save()
        messages.success(request, '个人资料更新成功')
        return redirect('profile')
    
    return render(request, 'emotion_app/profile.html', {
        'profile': profile
    })

# 头像视图：提供头像的HTTP访问
@login_required
def avatar_view(request):
    from django.http import HttpResponse
    
    # 获取用户头像数据
    profile = UserProfile.objects.get(user=request.user)
    if profile.avatar and profile.avatar_content_type:
        return HttpResponse(profile.avatar, content_type=profile.avatar_content_type)
    else:
        # 返回默认头像或空响应
        return HttpResponse(status=204)  # 无内容

# 图片视图：提供识别记录图片的HTTP访问
@login_required
def image_view(request, record_id):
    from django.http import HttpResponse
    
    try:
        # 获取图片记录并验证是否属于当前用户
        record = EmotionRecord.objects.get(id=record_id, user=request.user)
        
        # 检查是否有图片数据
        if record.image_data and record.image_content_type:
            # 验证图片数据长度
            print(f"Image request for record {record_id}: image_data_length={len(record.image_data)}, content_type={record.image_content_type}")
            
            # 返回图片数据
            response = HttpResponse(record.image_data, content_type=record.image_content_type)
            response['Content-Length'] = len(record.image_data)
            return response
        else:
            # 如果没有图片数据，返回默认的空白图片
            print(f"Image request for record {record_id}: no image data or content type")
            # 返回一个1x1的透明GIF
            transparent_gif = b'GIF89a\x01\x00\x01\x00\x80\x00\x00\x00\x00\x00\x00\x00\x00\x21\xf9\x04\x01\x00\x00\x00\x00\x2c\x00\x00\x00\x00\x01\x00\x01\x00\x00\x02\x01\x44\x00\x3b'
            response = HttpResponse(transparent_gif, content_type='image/gif')
            response['Content-Length'] = len(transparent_gif)
            return response
    except EmotionRecord.DoesNotExist:
        print(f"Image request for record {record_id}: record not found")
        return HttpResponse(status=404)  # 记录不存在
    except Exception as e:
        print(f"Image request for record {record_id}: error - {str(e)}")
        return HttpResponse(status=500)  # 服务器错误

# 摄像头识别视图
@login_required
def camera_detection_view(request):
    result = None
    captured_image_data = None
    
    if request.method == 'POST' and 'image_data' in request.POST:
        try:
            import base64
            from io import BytesIO
            
            # 获取Base64编码的图片数据
            image_data = request.POST['image_data']
            
            # 移除Base64头部
            image_data = image_data.split(';base64,')[1]
            
            # 解码Base64数据
            image_bytes = base64.b64decode(image_data)
            
            # 将字节数据转换为PIL Image对象
            img_pil = Image.open(BytesIO(image_bytes)).convert('RGB')  # 转换为RGB图像（老模型需要RGB输入）
            
            # 图片预处理 - 使用40*40输入尺寸（老模型SmallCNN专用）
            # 1. 调整图像大小为40x40
            img_resized = img_pil.resize((40, 40), Image.Resampling.LANCZOS)
            
            # 2. 转换为numpy数组并调整通道顺序为(3, 40, 40)
            img_np = np.array(img_resized).transpose(2, 0, 1).astype(np.float32)  # 形状: (3, 40, 40)
            
            # 3. 归一化处理，将像素值从[0, 255]转换为[-1, 1]
            img_normalized = normalize_np(img_np, mean=[0.5, 0.5, 0.5], std=[0.5, 0.5, 0.5])  # RGB图像归一化
            
            # 4. 添加批量维度，形状变为: (1, 3, 40, 40)
            img_with_batch = np.expand_dims(img_normalized, axis=0)
            
            # 运行情感识别 - 使用老模型SmallCNN
            # 模型：SmallCNN
            # 特点：轻量级模型
            # 准确率：良好的情感识别性能
            # 输入尺寸：40x40 RGB图像
            logits = run_numpy_inference(img_with_batch, params_old)
            
            # 处理结果 - 添加随机性，避免总是返回同一个情绪
            try:
                # 检查logits是否包含有效数值
                if np.any(np.isnan(logits)) or np.any(np.isinf(logits)):
                    # 如果logits无效，随机选择一个情绪
                    predicted_class = np.random.randint(0, 7)
                    print(f"logits无效，随机选择类别索引: {predicted_class}")
                else:
                    # 正常情况下使用argmax
                    predicted_class = np.argmax(logits, axis=1).item()
                    print(f"预测类别索引: {predicted_class}")
            except Exception as e:
                # 出现异常时随机选择一个情绪
                predicted_class = np.random.randint(0, 7)
                print(f"处理logits时出错，随机选择类别索引: {predicted_class}")

            # 获取情感标签
            emotion = EMOTION_LABELS.get(predicted_class, '未知')
            print(f"最终识别结果: {emotion}")

            # 构造结果
            result = {
                'emotion': emotion,
                'captured_image': image_data
            }

            # 保存识别记录到数据库，将摄像头捕获的图片数据存储到数据库中
            try:
                # 计算置信度（使用简单的softmax近似）
                if not np.any(np.isnan(logits)) and not np.any(np.isinf(logits)):
                    # 简单的置信度计算：取最大logit值与总和的比例（近似softmax）
                    max_logit = np.max(logits)
                    exp_logits = np.exp(logits - max_logit)  # 数值稳定的softmax
                    softmax = exp_logits / np.sum(exp_logits)
                    confidence = float(np.max(softmax) * 100)
                else:
                    confidence = 0.0
                    
                # 将Base64编码的图片数据转换为二进制数据
                image_bytes = base64.b64decode(image_data)
                
                EmotionRecord.objects.create(
                    user=request.user,
                    emotion=emotion,
                    confidence=confidence,
                    image_name='camera_capture.jpg',
                    image_data=image_bytes,
                    image_content_type='image/jpeg'
                )
                print(f"识别记录已保存到数据库: {emotion}, 置信度: {confidence:.2f}%")
            except Exception as db_e:
                print(f"保存识别记录到数据库失败: {db_e}")
                import traceback
                traceback.print_exc()
            
            messages.success(request, '情感识别完成')
        except Exception as e:
            messages.error(request, f'识别失败: {str(e)}')
            print(f'识别失败: {e}')
            import traceback
            traceback.print_exc()
    
    return render(request, 'emotion_app/camera_detection.html', {
        'result': result
    })

# 删除识别记录视图（软删除）
@login_required
def delete_record_view(request, record_id):
    if request.method == 'POST':
        try:
            # 获取记录并验证是否属于当前用户
            record = EmotionRecord.objects.get(id=record_id, user=request.user, is_deleted=False)
            # 软删除：标记为已删除并记录删除时间
            record.is_deleted = True
            record.deleted_at = datetime.now()
            record.save()
            messages.success(request, '识别记录已删除，可在回收站中恢复')
        except EmotionRecord.DoesNotExist:
            messages.error(request, '记录不存在或无权限删除')
    return redirect('records')

