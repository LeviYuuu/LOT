# test_publisher.py
# 独立的MQTT发布测试脚本
import paho.mqtt.client as mqtt
import json

# Mosquitto服务器配置
mqtt_broker = "localhost"
mqtt_port = 1883

# 测试主题
TEST_TOPIC = '/sys/test_product/THP-DataSystems/thing/event/property/post'

# 测试消息 payload
test_payload = {
    "id": "123",
    "version": "1.0",
    "params": {
        "DetectTime": "1392220800000",
        "CurrentTemperature": 25.5,
        "CurrentHumidity": 60.2,
        "CurrentPressure": 1013
    },
    "method": "thing.event.property.post"
}

# 创建MQTT客户端
client = mqtt.Client(client_id="test_publisher")

# 连接到Mosquitto服务器
print(f"🔄 连接到MQTT服务器: {mqtt_broker}:{mqtt_port}")
client.connect(mqtt_broker, mqtt_port, 60)

# 发布消息
print(f"📤 发布测试消息到主题: {TEST_TOPIC}")
print(f"  消息内容: {json.dumps(test_payload)}")

rc, mid = client.publish(TEST_TOPIC, json.dumps(test_payload), qos=0, retain=False)

if rc == 0:
    print(f"✅ 消息发布成功，消息ID: {mid}")
else:
    print(f"❌ 消息发布失败，错误代码: {rc}")

# 断开连接
client.disconnect()
print("\n🔌 已断开连接")
