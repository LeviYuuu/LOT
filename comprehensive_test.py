import requests
import time
import json
import paho.mqtt.client as mqtt

# 配置
SUBSCRIBE_APP_URL = "http://localhost:5001"
PUBLISH_APP_URL = "http://localhost:5000"
TEST_TOPIC = "/sys/test_product/THP-DataSystems/thing/event/property/post"

print("🚀 开始全面测试...")

# 1. 清除全局数据（通过保存空数据）
print("🔍 清除历史数据...")
try:
    response = requests.get(f"{SUBSCRIBE_APP_URL}/saveData")
    print(f"✅ 清除数据: {response.json()['message']}")
except Exception as e:
    print(f"❌ 清除数据失败: {e}")

# 2. 创建一个独立的MQTT客户端来监控消息
print("🔍 创建监控MQTT客户端...")
monitor_received = False
monitor_message = None

def on_monitor_message(client, userdata, msg):
    global monitor_received, monitor_message
    monitor_received = True
    monitor_message = msg
    print(f"📡 监控客户端收到消息: {msg.topic}")

try:
    monitor_client = mqtt.Client(client_id="monitor")
    monitor_client.on_message = on_monitor_message
    monitor_client.connect("localhost", 1883, 60)
    monitor_client.subscribe(TEST_TOPIC)
    monitor_client.loop_start()
except Exception as e:
    print(f"❌ 创建监控客户端失败: {e}")

# 3. 发布消息
print("🔍 发布测试消息...")
response = requests.post(f"{PUBLISH_APP_URL}/publishRandom")
result = response.json()
if result['status'] == 'success':
    print(f"✅ 发布成功: {result['message']}")
else:
    print(f"❌ 发布失败: {result['message']}")
    exit(1)

# 4. 等待消息传递
time.sleep(3)

# 5. 检查监控客户端是否收到消息
if monitor_received and monitor_message:
    print(f"✅ 监控客户端确认消息已发布")
    try:
        data = json.loads(monitor_message.payload.decode())
        print(f"   消息内容: {json.dumps(data, indent=2)}")
    except Exception as e:
        print(f"❌ 解析消息失败: {e}")
else:
    print("❌ 监控客户端未收到消息")

# 6. 检查应用的TopicData端点
print("🔍 检查应用的TopicData端点...")
try:
    response = requests.get(f"{SUBSCRIBE_APP_URL}/TopicData", timeout=5)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ TopicData响应: {result['status']}")
        if result['message']:
            print(f"   收到消息: {result['message']}")
        else:
            print("   未收到消息")
    else:
        print(f"❌ TopicData请求失败: {response.status_code}")
except Exception as e:
    print(f"❌ TopicData请求异常: {e}")

# 7. 直接测试发布应用生成的消息格式
print("🔍 测试直接发布消息...")
try:
    # 生成一个与publish_app.py相同格式的消息
    test_message = {
        "id": "test-789",
        "version": "1.0",
        "params": {
            "DetectTime": "1392220800000",
            "CurrentTemperature": 28.5,
            "CurrentHumidity": 65.2,
            "CurrentPressure": 1015
        },
        "method": "thing.event.property.post"
    }
    
    pub_client = mqtt.Client(client_id="direct_pub")
    pub_client.connect("localhost", 1883, 60)
    pub_client.publish(TEST_TOPIC, json.dumps(test_message))
    pub_client.disconnect()
    
    print("✅ 直接发布测试消息成功")
    
    # 等待消息传递
    time.sleep(2)
    
    # 再次检查TopicData端点
    response = requests.get(f"{SUBSCRIBE_APP_URL}/TopicData", timeout=5)
    if response.status_code == 200:
        result = response.json()
        print(f"✅ TopicData响应: {result['status']}")
        if result['message']:
            print(f"   收到消息: {result['message']}")
        else:
            print("   未收到消息")
    
except Exception as e:
    print(f"❌ 直接发布测试失败: {e}")

# 清理
monitor_client.loop_stop()
monitor_client.disconnect()

print("🎉 测试完成！")
