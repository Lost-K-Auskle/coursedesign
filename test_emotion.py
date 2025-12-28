import requests
import os

# 测试图片路径
test_image_path = 'c:/Users/lost/Desktop/coursedesign/data/image.bmp'
# 服务器URL
server_url = 'http://127.0.0.1:8000/'

print(f"测试图片路径: {test_image_path}")
print(f"图片是否存在: {os.path.exists(test_image_path)}")

if not os.path.exists(test_image_path):
    print("测试图片不存在，无法进行测试")
    exit(1)

# 发送POST请求，上传图片
with open(test_image_path, 'rb') as f:
    files = {'image': f}
    try:
        print(f"向 {server_url} 发送测试请求...")
        response = requests.post(server_url, files=files)
        print(f"响应状态码: {response.status_code}")
        print(f"响应内容长度: {len(response.content)} 字节")
        
        # 检查响应中是否包含成功信息
        if "识别完成" in response.text or "情感" in response.text:
            print("✅ 测试成功！情感识别功能正常工作")
        elif "识别失败" in response.text:
            print("❌ 测试失败，识别失败")
            # 提取失败原因
            start = response.text.find("识别失败: ")
            if start != -1:
                end = response.text.find("</div>", start)
                if end != -1:
                    error = response.text[start+6:end]
                    print(f"失败原因: {error}")
        else:
            print("❌ 测试失败，响应异常")
            # 打印前500个字符的响应内容
            print(f"响应内容预览: {response.text[:500]}...")
            
    except Exception as e:
        print(f"❌ 测试请求失败: {e}")
        import traceback
        traceback.print_exc()