import requests
import time
import json
import paho.mqtt.client as mqtt

# 配置
SUBSCRIBE_APP_URL = "http://localhost:5001"
PUBLISH_APP_URL = "http://localhost:5000"
TEST_TOPIC = "/sys/test_product/THP-DataSystems/thing/event/property/post"

# 测试发布消息
print("🔍 测试发布随机数据...")
response = requests.post(f"{PUBLISH_APP_URL}/publishRandom")
result = response.json()
if result['status'] == 'success':
    print(f"✅ 发布成功: {result['message']}")
else:
    print(f"❌ 发布失败: {result['message']}")
    exit(1)

# 等待消息传递
time.sleep(2)

# 测试获取消息
print("🔍 测试获取消息...")
try:
    # 创建一个直接的MQTT客户端来测试消息接收
    def on_message(client, userdata, msg):
        print(f"✅ 直接MQTT客户端收到消息:")
        print(f"   主题: {msg.topic}")
        try:
            data = json.loads(msg.payload.decode())
            print(f"   内容: {json.dumps(data, indent=2)}")
            userdata["received"] = True
        except Exception as e:
            print(f"❌ 消息解析失败: {e}")
    
    test_client = mqtt.Client(client_id="test_reception")
    user_data = {"received": False}
    test_client.on_message = on_message
    test_client.user_data_set(user_data)
    
    test_client.connect("localhost", 1883, 60)
    test_client.subscribe(TEST_TOPIC)
    test_client.loop_start()
    
    # 等待消息
    time.sleep(5)
    
    test_client.loop_stop()
    test_client.disconnect()
    
    if not user_data["received"]:
        print("❌ 直接MQTT客户端未收到消息")
    else:
        print("✅ 直接MQTT客户端测试成功")
        
    # 测试应用的TopicData端点
    print("🔍 测试应用的TopicData端点...")
    response = requests.get(f"{SUBSCRIBE_APP_URL}/TopicData")
    result = response.json()
    if result['status'] == 'success':
        print(f"✅ TopicData端点调用成功")
        if result['message']:
            print(f"   消息内容: {result['message']}")
        else:
            print("   消息内容为空")
    else:
        print(f"❌ TopicData端点调用失败: {result}")
        
    print("🎉 测试完成！")
    
except Exception as e:
    print(f"❌ 测试过程中发生错误: {e}")
