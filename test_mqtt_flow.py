#!/usr/bin/env python3
# 测试MQTT通信流程的脚本
import json
import time
import paho.mqtt.client as mqtt
import global_var as gv

def on_connect(client, userdata, flags, rc):
    print(f"Connected with result code {rc}")
    client.subscribe("#")  # 订阅所有主题

def on_message(client, userdata, msg):
    print(f"Received message on topic {msg.topic}: {msg.payload.decode()}")
    
    # 尝试解析消息，模拟subscribe_module中的处理
    try:
        result = json.loads(msg.payload.decode())
        
        # 处理三种不同的消息格式
        if 'items' in result and 'DetectTime' in result['items']:
            # 阿里云格式
            prop_data = {}
            prop_data["time"] = int(result['items']['DetectTime']['value'])
            prop_data["temperature"] = float(result['items']['CurrentTemperature'].get("value", None))
            prop_data["humidity"] = float(result['items']['CurrentHumidity'].get("value", None))
            prop_data["pressure"] = int(result['items']['CurrentPressure'].get("value", None))
        elif 'params' in result and 'DetectTime' in result['params']:
            # publish_app.py发送的格式
            prop_data = {}
            prop_data["time"] = int(result['params']['DetectTime'])
            prop_data["temperature"] = float(result['params']['CurrentTemperature'])
            prop_data["humidity"] = float(result['params']['CurrentHumidity'])
            prop_data["pressure"] = int(result['params']['CurrentPressure'])
        else:
            # 直接格式
            prop_data = {}
            prop_data["time"] = int(result.get("time", time.time() * 1000))
            prop_data["temperature"] = float(result.get("temperature", None))
            prop_data["humidity"] = float(result.get("humidity", None))
            prop_data["pressure"] = int(result.get("pressure", None))
        
        ans_data = {}
        print(f"Topic list length: {len(gv.global_var.topic_list)}")
        
        # 如果topic_list为空，默认显示所有数据
        if len(gv.global_var.topic_list) == 0:
            ans_data["temperature"] = prop_data.get("temperature", None)
            ans_data["humidity"] = prop_data.get("humidity", None)
            ans_data["pressure"] = prop_data.get("pressure", None)
        else:
            for topic in gv.global_var.topic_list:
                if topic in prop_data and prop_data[topic] is not None:
                    ans_data[topic] = prop_data[topic]
        
        if ans_data != {} or any(ans_data.values()):
            ans_data['time'] = prop_data['time']
            ans_data["printed"] = False
            gv.global_var.receive_data.append(ans_data)
            print(f"Data added to receive_data: {ans_data}")
            
    except json.JSONDecodeError as e:
        print(f"Error parsing JSON: {e}")
    except KeyError as e:
        print(f"Key error: {e}")

def main():
    # 初始化全局变量
    gv.global_var.receive_data = []
    gv.global_var.topic_list = []
    
    # 创建MQTT客户端
    client = mqtt.Client(client_id="test_subscriber")
    client.on_connect = on_connect
    client.on_message = on_message
    
    # 连接到Mosquitto服务器
    print("正在连接到Mosquitto服务器...")
    client.connect("localhost", 1883, 60)
    
    # 启动后台线程处理MQTT网络流量
    client.loop_start()
    
    # 创建发布客户端
    publisher = mqtt.Client(client_id="test_publisher")
    publisher.connect("localhost", 1883, 60)
    publisher.loop_start()
    
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
    print("正在发布测试消息...")
    publisher.publish("/sys/test_product/test_device/thing/event/property/post", json.dumps(test_payload))
    
    # 等待接收消息
    time.sleep(2)
    
    # 检查是否接收到消息
    print(f"\nReceived data count: {len(gv.global_var.receive_data)}")
    for data in gv.global_var.receive_data:
        print(f"Data: {data}")
    
    # 断开连接
    client.loop_stop()
    client.disconnect()
    publisher.loop_stop()
    publisher.disconnect()

if __name__ == "__main__":
    main()
