#!/usr/bin/env python3
# 测试修改后的MQTT通信
import json
import time
import paho.mqtt.client as mqtt

# 使用修改后的主题
TEST_TOPIC = '/sys/test_product/THP-DataSystems/thing/event/property/post'

def on_connect_sub(client, userdata, flags, rc):
    print(f"订阅客户端连接成功 (rc={rc})")
    client.subscribe(TEST_TOPIC)

def on_message(client, userdata, msg):
    print(f"收到消息：")
    print(f"  主题: {msg.topic}")
    print(f"  内容: {msg.payload.decode()}")
    
    # 尝试解析消息
    try:
        result = json.loads(msg.payload.decode())
        if 'params' in result and 'DetectTime' in result['params']:
            print(f"  解析成功：")
            print(f"    时间: {result['params']['DetectTime']}")
            print(f"    温度: {result['params']['CurrentTemperature']}")
            print(f"    湿度: {result['params']['CurrentHumidity']}")
            print(f"    气压: {result['params']['CurrentPressure']}")
    except Exception as e:
        print(f"  解析失败: {e}")

def main():
    print("开始测试修改后的MQTT通信...")
    print(f"测试主题: {TEST_TOPIC}")
    
    # 创建订阅客户端
    sub_client = mqtt.Client(client_id="test_subscriber_fixed")
    sub_client.on_connect = on_connect_sub
    sub_client.on_message = on_message
    
    # 连接到Mosquitto服务器
    print("连接订阅客户端...")
    sub_client.connect("localhost", 1883, 60)
    sub_client.loop_start()
    
    # 等待连接建立
    time.sleep(1)
    
    # 创建发布客户端
    pub_client = mqtt.Client(client_id="test_publisher_fixed")
    print("连接发布客户端...")
    pub_client.connect("localhost", 1883, 60)
    pub_client.loop_start()
    
    # 模拟publish_app.py发送的消息格式
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
    
    # 发布测试消息
    print("发布测试消息...")
    pub_client.publish(TEST_TOPIC, json.dumps(test_payload))
    
    # 等待接收消息
    time.sleep(2)
    
    # 断开连接
    print("测试完成，断开连接...")
    sub_client.loop_stop()
    sub_client.disconnect()
    pub_client.loop_stop()
    pub_client.disconnect()
    
    print("测试结束")

if __name__ == "__main__":
    main()
