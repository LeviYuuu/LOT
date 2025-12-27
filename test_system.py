# test_system.py
# 综合测试整个MQTT系统的功能
import paho.mqtt.client as mqtt
import json
import time
import requests
import threading

# 系统配置
publish_url = "http://localhost:5000"
subscribe_url = "http://localhost:5001"
mqtt_broker = "localhost"
mqtt_port = 1883
TEST_TOPIC = '/sys/test_product/THP-DataSystems/thing/event/property/post'

# 测试结果记录
test_results = {
    "publish_app_running": False,
    "subscribe_app_running": False,
    "mqtt_server_running": False,
    "publish_connect_success": False,
    "subscribe_connect_success": False,
    "message_published": False,
    "message_received": False
}

# 测试发布端应用是否运行
def test_publish_app():
    print("🔍 测试发布端应用...")
    try:
        response = requests.get(f"{publish_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 发布端应用运行正常")
            test_results["publish_app_running"] = True
            return True
        else:
            print(f"❌ 发布端应用返回状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到发布端应用: {e}")
        return False

# 测试订阅端应用是否运行
def test_subscribe_app():
    print("\n🔍 测试订阅端应用...")
    try:
        response = requests.get(f"{subscribe_url}/", timeout=5)
        if response.status_code == 200:
            print("✅ 订阅端应用运行正常")
            test_results["subscribe_app_running"] = True
            return True
        else:
            print(f"❌ 订阅端应用返回状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 无法连接到订阅端应用: {e}")
        return False

# 测试Mosquitto服务器是否运行
def test_mqtt_server():
    print("\n🔍 测试Mosquitto服务器...")
    try:
        client = mqtt.Client(client_id="test_mqtt_checker")
        client.connect(mqtt_broker, mqtt_port, 5)
        client.disconnect()
        print("✅ Mosquitto服务器运行正常")
        test_results["mqtt_server_running"] = True
        return True
    except Exception as e:
        print(f"❌ 无法连接到Mosquitto服务器: {e}")
        return False

# 测试发布端连接到MQTT服务器
def test_publish_connect():
    print("\n🔍 测试发布端连接到MQTT服务器...")
    try:
        response = requests.post(f"{publish_url}/connect", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result["status"] == "connected":
                print(f"✅ 发布端连接成功: {result['message']}")
                test_results["publish_connect_success"] = True
                return True
            else:
                print(f"❌ 发布端连接失败: {result['message']}")
                return False
        else:
            print(f"❌ 发布端连接请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 发布端连接请求异常: {e}")
        return False

# 测试订阅端连接到MQTT服务器
def test_subscribe_connect():
    print("\n🔍 测试订阅端连接到MQTT服务器...")
    try:
        # 使用默认的客户端ID，不提供用户名和密码
        response = requests.post(f"{subscribe_url}/", 
                               data={"ClientID": "test_client", "access_key_id": "", "access_secret": ""},
                               timeout=10)
        if response.status_code == 200:
            print("✅ 订阅端连接成功")
            test_results["subscribe_connect_success"] = True
            return True
        else:
            print(f"❌ 订阅端连接请求失败，状态码: {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ 订阅端连接请求异常: {e}")
        return False

# MQTT消息接收回调
def on_message(client, userdata, msg):
    print(f"✅ 收到发布的消息：")
    print(f"  主题: {msg.topic}")
    print(f"  内容: {msg.payload.decode()}")
    test_results["message_received"] = True
    
    # 解析消息内容
    try:
        result = json.loads(msg.payload.decode())
        if 'params' in result:
            params = result['params']
            print(f"  数据解析成功：")
            print(f"    时间: {params.get('DetectTime', 'N/A')}")
            print(f"    温度: {params.get('CurrentTemperature', 'N/A')}")
            print(f"    湿度: {params.get('CurrentHumidity', 'N/A')}")
            print(f"    气压: {params.get('CurrentPressure', 'N/A')}")
    except Exception as e:
        print(f"  消息解析失败: {e}")

# MQTT连接成功回调
def on_connect(client, userdata, flags, rc):
    print(f"✅ 测试订阅者连接成功，返回码: {rc}")
    client.subscribe(TEST_TOPIC)
    print(f"📥 订阅测试主题: {TEST_TOPIC}")

# 测试发布消息
def test_publish_message():
    print("\n🔍 测试发布消息...")
    
    # 启动测试订阅者
    client = mqtt.Client(client_id="system_test_subscriber")
    client.on_connect = on_connect
    client.on_message = on_message
    
    try:
        client.connect(mqtt_broker, mqtt_port, 60)
        client.loop_start()
        
        # 等待订阅完成
        time.sleep(1)
        
        # 请求发布端发布随机数据
        response = requests.post(f"{publish_url}/publishRandom", timeout=10)
        if response.status_code == 200:
            result = response.json()
            if result["status"] == "success":
                print(f"✅ 发布请求成功: {result['message']}")
                test_results["message_published"] = True
                
                # 等待消息接收
                print("\n⏳ 等待消息接收...")
                time.sleep(3)
                
                client.loop_stop()
                client.disconnect()
                
                return test_results["message_received"]
            else:
                print(f"❌ 发布请求失败: {result['message']}")
                client.loop_stop()
                client.disconnect()
                return False
        else:
            print(f"❌ 发布请求异常，状态码: {response.status_code}")
            client.loop_stop()
            client.disconnect()
            return False
    except Exception as e:
        print(f"❌ 发布测试异常: {e}")
        client.loop_stop()
        client.disconnect()
        return False

# 主测试函数
def run_all_tests():
    print("🚀 开始系统测试...\n")
    
    # 测试各个组件是否运行
    test_publish_app()
    test_subscribe_app()
    test_mqtt_server()
    
    # 如果所有组件都运行正常，继续测试功能
    if test_results["publish_app_running"] and test_results["subscribe_app_running"] and test_results["mqtt_server_running"]:
        print("\n✅ 所有组件都运行正常，开始测试功能...")
        
        # 测试发布端连接
        test_publish_connect()
        
        # 测试发布和订阅
        if test_results["publish_connect_success"]:
            test_publish_message()
    
    # 打印测试报告
    print("\n" + "="*50)
    print("📋 系统测试报告")
    print("="*50)
    for test_name, result in test_results.items():
        status = "✅" if result else "❌"
        print(f"{status} {test_name}: {'成功' if result else '失败'}")
    
    # 总结
    all_passed = all(test_results.values())
    print("\n" + "="*50)
    if all_passed:
        print("🎉 所有测试通过！系统功能正常")
    else:
        print("⚠️  部分测试失败，请检查系统配置")
    print("="*50)

if __name__ == "__main__":
    run_all_tests()
