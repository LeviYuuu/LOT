import paho.mqtt.client as mqtt
import time
import json

# 测试MQTT消息发布和接收

def on_connect(client, userdata, flags, rc):
    print(f"连接成功，返回码: {rc}")
    client.subscribe("/sys/******/THP-DataSystems/thing/event/property/post")
    print("已订阅测试主题")

def on_message(client, userdata, msg):
    print(f"收到消息 - 主题: {msg.topic}")
    print(f"消息内容: {msg.payload.decode()}")
    
    # 尝试解析消息格式
    try:
        result = json.loads(msg.payload.decode())
        print(f"解析后的消息: {result}")
        
        # 检查是否是我们预期的格式
        if 'params' in result and 'DetectTime' in result['params']:
            print("✓ 消息格式正确，包含params和DetectTime字段")
            print(f"温度: {result['params']['CurrentTemperature']}")
            print(f"湿度: {result['params']['CurrentHumidity']}")
            print(f"气压: {result['params']['CurrentPressure']}")
    except json.JSONDecodeError as e:
        print(f"解析JSON失败: {e}")

# 创建订阅客户端
sub_client = mqtt.Client()
sub_client.on_connect = on_connect
sub_client.on_message = on_message

# 连接到Mosquitto服务器
sub_client.connect("localhost", 1883, 60)
sub_client.loop_start()

# 创建发布客户端
pub_client = mqtt.Client()
pub_client.connect("localhost", 1883, 60)
pub_client.loop_start()

# 构造测试消息（与publish_app.py格式相同）
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

# 发布测试消息
print("\n发布测试消息...")
test_topic = "/sys/******/THP-DataSystems/thing/event/property/post"
pub_client.publish(test_topic, json.dumps(test_payload))

# 等待消息接收
time.sleep(2)

# 停止客户端
sub_client.loop_stop()
pub_client.loop_stop()
sub_client.disconnect()
pub_client.disconnect()

print("\n测试完成")