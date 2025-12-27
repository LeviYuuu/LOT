import paho.mqtt.client as mqtt
import json
import time
import threading
import sys

# 配置
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TEST_TOPIC = "/sys/******/THP-DataSystems/thing/event/property/post"

# 消息计数器
received_messages = []

# 订阅客户端回调
def on_connect_sub(client, userdata, flags, rc):
    print(f"[订阅端] 连接成功，返回码: {rc}")
    client.subscribe(TEST_TOPIC)
    print(f"[订阅端] 已订阅主题: {TEST_TOPIC}")

def on_message_sub(client, userdata, msg):
    print(f"[订阅端] 收到消息 - 主题: {msg.topic}")
    print(f"[订阅端] 消息内容: {msg.payload.decode()}")
    received_messages.append(msg.payload.decode())

# 发布客户端回调
def on_connect_pub(client, userdata, flags, rc):
    print(f"[发布端] 连接成功，返回码: {rc}")

def on_publish_pub(client, userdata, mid):
    print(f"[发布端] 消息发布成功，消息ID: {mid}")

# 创建并配置订阅客户端
def create_subscriber():
    sub_client = mqtt.Client()
    sub_client.on_connect = on_connect_sub
    sub_client.on_message = on_message_sub
    return sub_client

# 创建并配置发布客户端
def create_publisher():
    pub_client = mqtt.Client()
    pub_client.on_connect = on_connect_pub
    pub_client.on_publish = on_publish_pub
    return pub_client

# 模拟publish_app.py的发布格式
def publish_test_message(pub_client):
    test_payload = {
        "id": "123",
        "version": "1.0",
        "params": {
            "DetectTime": "1609459200000",
            "CurrentTemperature": 25.5,
            "CurrentHumidity": 60.2,
            "CurrentPressure": 1013
        },
        "method": "thing.event.property.post"
    }
    
    print(f"[发布端] 发布消息: {json.dumps(test_payload)}")
    result = pub_client.publish(TEST_TOPIC, json.dumps(test_payload))
    
    if result.rc == mqtt.MQTT_ERR_SUCCESS:
        print(f"[发布端] 发布请求已发送，消息ID: {result.mid}")
    else:
        print(f"[发布端] 发布失败，错误码: {result.rc}")

# 测试Mosquitto服务器连接
def test_mosquitto_connection():
    print("\n=== 测试Mosquitto服务器连接 ===")
    
    test_client = mqtt.Client()
    try:
        result = test_client.connect(MQTT_BROKER, MQTT_PORT, 5)
        if result == mqtt.MQTT_ERR_SUCCESS:
            print(f"✓ 成功连接到Mosquitto服务器: {MQTT_BROKER}:{MQTT_PORT}")
            test_client.disconnect()
            return True
        else:
            print(f"✗ 连接失败，错误码: {result}")
            return False
    except Exception as e:
        print(f"✗ 连接异常: {e}")
        return False

# 主测试函数
def main():
    print("THP-Data 消息发布/订阅端到端测试")
    print("=" * 50)
    
    # 测试Mosquitto连接
    if not test_mosquitto_connection():
        print("请确保Mosquitto服务器正在运行!")
        sys.exit(1)
    
    # 创建客户端
    print("\n=== 创建MQTT客户端 ===")
    sub_client = create_subscriber()
    pub_client = create_publisher()
    
    # 连接到服务器
    print("\n=== 连接到MQTT服务器 ===")
    sub_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    pub_client.connect(MQTT_BROKER, MQTT_PORT, 60)
    
    # 启动客户端循环
    sub_client.loop_start()
    pub_client.loop_start()
    
    # 等待连接稳定
    time.sleep(2)
    
    # 发布测试消息
    print("\n=== 发布测试消息 ===")
    publish_test_message(pub_client)
    
    # 等待消息接收
    print("\n=== 等待消息接收 (10秒) ===")
    for i in range(10):
        print(f"等待中... {i+1}秒")
        time.sleep(1)
        if received_messages:
            break
    
    # 结果分析
    print("\n=== 测试结果 ===")
    if received_messages:
        print(f"✓ 成功收到 {len(received_messages)} 条消息")
        
        # 解析消息
        for i, msg in enumerate(received_messages):
            try:
                parsed = json.loads(msg)
                print(f"\n消息 {i+1} 解析结果:")
                print(f"  消息ID: {parsed.get('id')}")
                print(f"  版本: {parsed.get('version')}")
                
                if 'params' in parsed:
                    params = parsed['params']
                    print(f"  检测时间: {params.get('DetectTime')}")
                    print(f"  温度: {params.get('CurrentTemperature')}")
                    print(f"  湿度: {params.get('CurrentHumidity')}")
                    print(f"  气压: {params.get('CurrentPressure')}")
                    print("  ✓ 消息格式正确，包含所有THP数据字段")
                else:
                    print("  ✗ 消息格式错误，缺少params字段")
                    
            except json.JSONDecodeError as e:
                print(f"  ✗ 解析失败: {e}")
    else:
        print("✗ 未收到任何消息")
        print("\n可能的原因:")
        print("1. 订阅主题不正确")
        print("2. 发布主题不正确")
        print("3. MQTT服务器配置问题")
        print("4. 网络连接问题")
    
    # 清理资源
    print("\n=== 清理资源 ===")
    sub_client.loop_stop()
    pub_client.loop_stop()
    sub_client.disconnect()
    pub_client.disconnect()
    
    print("\n=== 测试完成 ===")

if __name__ == "__main__":
    main()