# test_no_auth.py
# 测试无需认证的MQTT连接
import paho.mqtt.client as mqtt
import json
import time

# Mosquitto服务器配置
mqtt_broker = "localhost"
mqtt_port = 1883

# 测试主题
TEST_TOPIC = '/sys/test_product/THP-DataSystems/thing/event/property/post'

# 接收到消息的回调函数
def on_message(client, userdata, msg):
    print(f"✅ 收到消息：")
    print(f"  主题: {msg.topic}")
    print(f"  内容: {msg.payload.decode()}")

# 连接成功的回调函数
def on_connect(client, userdata, flags, rc):
    print(f"✅ 连接成功，返回码: {rc}")
    print(f"📥 订阅主题: {TEST_TOPIC}")
    client.subscribe(TEST_TOPIC)

# 创建MQTT客户端（使用空的用户名和密码）
client = mqtt.Client(client_id="no_auth_test_subscriber")

# 设置回调函数
client.on_connect = on_connect
client.on_message = on_message

# 不设置用户名和密码，直接连接
print(f"🔄 连接到MQTT服务器: {mqtt_broker}:{mqtt_port}")
print(f"  不使用认证")

client.connect(mqtt_broker, mqtt_port, 60)

# 启动消息循环
print("\n📡 开始接收消息...")
print("按 Ctrl+C 停止测试\n")
client.loop_start()

try:
    # 保持运行，直到用户中断
    while True:
        time.sleep(1)
except KeyboardInterrupt:
    print("\n🛑 测试停止")
    client.loop_stop()
    client.disconnect()
