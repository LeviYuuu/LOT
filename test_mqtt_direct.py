# test_mqtt_direct.py
# 直接测试MQTT订阅功能，绕过登录界面
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
    
    # 解析消息内容
    try:
        result = json.loads(msg.payload.decode())
        if 'params' in result and 'DetectTime' in result['params']:
            print(f"  数据解析成功：")
            print(f"    时间: {result['params']['DetectTime']}")
            print(f"    温度: {result['params']['CurrentTemperature']}")
            print(f"    湿度: {result['params']['CurrentHumidity']}")
            print(f"    气压: {result['params']['CurrentPressure']}")
    except Exception as e:
        print(f"  消息解析失败: {e}")

# 连接成功的回调函数
def on_connect(client, userdata, flags, rc):
    print(f"✅ 连接成功，返回码: {rc}")
    print(f"📥 订阅主题: {TEST_TOPIC}")
    client.subscribe(TEST_TOPIC)

# 创建MQTT客户端
client = mqtt.Client(client_id="direct_test_subscriber")

# 设置回调函数
client.on_connect = on_connect
client.on_message = on_message

# 连接到Mosquitto服务器
print(f"🔄 连接到MQTT服务器: {mqtt_broker}:{mqtt_port}")
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
