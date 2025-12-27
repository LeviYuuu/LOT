# user_flow_test.py
# 模拟用户操作流程，测试系统功能
import requests
import time
import json
import paho.mqtt.client as mqtt

# 配置
PUBLISH_APP_URL = "http://localhost:5000"
SUBSCRIBE_APP_URL = "http://localhost:5001"
TEST_TOPIC = "/sys/test_product/THP-DataSystems/thing/event/property/post"

# 步骤1: 测试发布端连接到MQTT服务器
def test_publisher_connect():
    print("🔍 步骤1: 测试发布端连接到MQTT服务器...")
    response = requests.post(f"{PUBLISH_APP_URL}/connect")
    result = response.json()
    if result['status'] in ['connected', 'already_connected']:
        print(f"✅ 发布端连接成功: {result['message']}")
        return True
    else:
        print(f"❌ 发布端连接失败: {result['message']}")
        return False

# 步骤2: 测试发布端发布消息
def test_publisher_publish():
    print("🔍 步骤2: 测试发布端发布消息...")
    response = requests.post(f"{PUBLISH_APP_URL}/publishRandom")
    result = response.json()
    if result['status'] == 'success':
        print(f"✅ 发布端发布消息成功: {result['message']}")
        return True
    else:
        print(f"❌ 发布端发布消息失败: {result['message']}")
        return False

# 步骤3: 测试订阅端连接和订阅
def test_subscriber_connect():
    print("🔍 步骤3: 测试订阅端连接和订阅...")
    # 生成随机ClientID
    import datetime
    client_id = f"test_user_{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"
    
    # 连接到订阅端应用
    try:
        response = requests.post(f"{SUBSCRIBE_APP_URL}/", data={
            'ClientID': client_id,
            'access_key_id': '',  # 不使用认证
            'access_secret': ''   # 不使用认证
        }, timeout=5, allow_redirects=True)
        
        print(f"   响应状态码: {response.status_code}")
        print(f"   响应URL: {response.url}")
        print(f"   响应内容: {response.text[:100]}...")
        
        if response.status_code == 200:
            print("✅ 订阅端连接和订阅成功")
            # 保存会话以便后续请求
            session = requests.Session()
            session.cookies = response.cookies
            return session
        else:
            print("❌ 订阅端连接和订阅失败")
            return None
    except Exception as e:
        print(f"❌ 订阅端连接请求异常: {e}")
        return None

# 步骤4: 测试订阅端获取消息
def test_subscriber_get_messages(session):
    print("🔍 步骤4: 测试订阅端获取消息...")
    # 等待一段时间让消息传递
    time.sleep(2)
    
    response = session.get(f"{SUBSCRIBE_APP_URL}/TopicData")
    result = response.json()
    if result['status'] == 'success' and result['message']:
        print(f"✅ 订阅端获取消息成功:")
        print(f"   消息内容: {result['message']}")
        return True
    else:
        print("❌ 订阅端获取消息失败")
        return False

# 主测试流程
def run_user_flow_test():
    print("🚀 开始用户操作流程测试...")
    
    # 测试独立MQTT通信
    print("\n📡 测试独立MQTT通信...")
    def on_message(client, userdata, msg):
        print(f"✅ 独立测试收到消息:")
        print(f"   主题: {msg.topic}")
        try:
            data = json.loads(msg.payload.decode())
            print(f"   内容: {json.dumps(data, indent=2)}")
            userdata["received"] = True
        except Exception as e:
            print(f"❌ 消息解析失败: {e}")
    
    # 创建测试订阅者
    test_client = mqtt.Client(client_id="flow_test_subscriber")
    
    # 使用自定义数据结构
    user_data = {"received": False}
    
    def on_message_with_data(client, userdata, msg):
        print(f"✅ 独立测试收到消息:")
        print(f"   主题: {msg.topic}")
        try:
            data = json.loads(msg.payload.decode())
            print(f"   内容: {json.dumps(data, indent=2)}")
            user_data["received"] = True
        except Exception as e:
            print(f"❌ 消息解析失败: {e}")
    
    test_client.on_message = on_message_with_data
    
    try:
        test_client.connect("localhost", 1883, 60)
        test_client.subscribe(TEST_TOPIC)
        test_client.loop_start()
        
        # 创建测试发布者
        pub_client = mqtt.Client(client_id="flow_test_publisher")
        pub_client.connect("localhost", 1883, 60)
        
        # 发布测试消息
        test_message = {
            "id": "test-123",
            "version": "1.0",
            "params": {
                "DetectTime": "1392220800000",
                "CurrentTemperature": 25.5,
                "CurrentHumidity": 60.2,
                "CurrentPressure": 1013
            },
            "method": "thing.event.property.post"
        }
        pub_client.publish(TEST_TOPIC, json.dumps(test_message))
        pub_client.disconnect()
        
        # 等待消息接收
        time.sleep(2)
        test_client.loop_stop()
        test_client.disconnect()
        
        if not user_data["received"]:
            print("❌ 独立MQTT测试失败，未收到消息")
            return
    except Exception as e:
        print(f"❌ 独立MQTT测试失败: {e}")
        return
    
    # 测试发布端应用
    if not test_publisher_connect():
        return
    
    if not test_publisher_publish():
        return
    
    # 测试订阅端应用
    session = test_subscriber_connect()
    if not session:
        return
    
    if not test_subscriber_get_messages(session):
        print("\n❌ 测试失败")
        return
    
    print("\n🎉 所有测试通过！系统工作正常")

if __name__ == "__main__":
    run_user_flow_test()
