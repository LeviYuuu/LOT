import requests
import time

# 配置
SUBSCRIBE_APP_URL = "http://localhost:5001"

# 测试TopicData端点
print("🔍 测试TopicData端点...")
try:
    start_time = time.time()
    response = requests.get(f"{SUBSCRIBE_APP_URL}/TopicData", timeout=5)
    end_time = time.time()
    
    print(f"✅ 请求耗时: {end_time - start_time:.2f}秒")
    print(f"   状态码: {response.status_code}")
    
    if response.status_code == 200:
        result = response.json()
        print(f"   响应状态: {result['status']}")
        print(f"   消息内容: {result['message']}")
    else:
        print(f"❌ 请求失败，状态码: {response.status_code}")
        
except Exception as e:
    print(f"❌ 请求异常: {e}")
