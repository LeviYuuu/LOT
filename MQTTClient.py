# MQTTClient.py
import json
import random
import time
import paho.mqtt.client as mqtt
import csv
from datetime import datetime

class MQTTClient:
    def __init__(self, product_key, device_name, device_secret, broker='localhost', port=1883):
        # 使用paho-mqtt创建客户端
        self.client = mqtt.Client()
        self.broker = broker
        self.port = port
        self.product_key = product_key
        self.device_name = device_name
        self.device_secret = device_secret
        self.mqtt_topic_post = f'/sys/{product_key}/{device_name}/thing/event/property/post'
        self.connected = False
        
        # 设置回调函数
        self.client.on_connect = self.on_connect
        self.client.on_disconnect = self.on_disconnect
        self.client.on_publish = self.on_publish
        self.client.on_message = self.on_message

    def on_connect(self, client, userdata, flags, rc):
        if rc == 0:
            self.connected = True
            print(f"MQTT已连接 (rc={rc})")
        else:
            print(f"MQTT连接失败 (rc={rc})")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        print(f"MQTT已断开连接 (rc={rc})")

    def on_publish(self, client, userdata, mid):
        print(f"消息已发布 (mid={mid})")

    def on_message(self, client, userdata, msg):
        print(f"已接收消息 (topic={msg.topic}, payload={msg.payload.decode()}, qos={msg.qos})")

    def connect(self):
        try:
            self.client.connect(self.broker, self.port, 60)
            self.client.loop_start()  # 开启后台循环
            print("MQTT客户端正在连接...")
            # 等待连接成功
            time.sleep(1)
            if not self.connected:
                print("MQTT客户端连接超时。")
            return self.connected
        except Exception as e:
            print(f"MQTT连接错误: {e}")
            return False

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("MQTT客户端正在断开连接...")

    def publish(self, topic, message):
        try:
            if isinstance(message, dict):
                message = json.dumps(message)
            result = self.client.publish(topic, message)
            return result.rc, result.mid
        except Exception as e:
            print(f"发布错误: {e}")
            return -1, 0
    
    def subscribe(self, topic):
        try:
            result, mid = self.client.subscribe(topic)
            return result, mid
        except Exception as e:
            print(f"订阅错误: {e}")
            return -1, 0
    
    def unsubscribe(self, topic):
        try:
            result, mid = self.client.unsubscribe(topic)
            return result, mid
        except Exception as e:
            print(f"取消订阅错误: {e}")
            return -1, 0

    def is_connected(self):
        return self.connected
    
    # 上报随机数据
    def post_random_data(self, topic):
        # 上报随机属性
        prop_data = {
            "CurrentTemperature": random.randint(-10, 40) + random.random(),
            "CurrentHumidity": random.randint(0, 100) + random.random(),
            "CurrentPressure": random.randint(900, 1100),
            "DetectTime": str(int(round(time.time() * 1000)))
        }
        # 构造上报数据结构
        payload = {
            "id": "123",
            "version": "1.0",
            "params": prop_data,
            "method": "thing.event.property.post"
        }
        # 上报属性
        rc, request_id = self.publish(topic, payload)
        if rc == 0:
            print("属性上报成功:%r, 请求ID:%r" % (rc, request_id))
        else:
            print("属性上报失败, rc=%d" % rc)
    
    # 读取数据并上报
    '''def read_and_post_data(self, publish_file, topic):
        with open(publish_file, 'r') as file:
            reader = csv.reader(file)
            count = 0
            for row in reader:
                if len(row) == 4:
                    # 从行中提取数据并构建属性字典
                    prop_data = {
                        "DetectTime": int(row[0]),  # 假设 CSV 文件中的时间戳已经是毫秒格式
                        "CurrentTemperature": float(row[1]),
                        "CurrentHumidity": float(row[2]),
                        "CurrentPressure": int(row[3])
                    }
                    # 构造上报数据结构
                    payload = {
                        "id": "123",
                        "version": "1.0",
                        "params": prop_data,
                        "method": "thing.event.property.post"
                    }
                    # 上报属性
                    rc, request_id = self.lk.publish_topic(
                        topic,
                        json.dumps(payload)
                    )
                    if rc == 0:
                        print(f"thing post property success:{rc}, request id:{request_id}")
                    else:
                        print(f"thing post property failed, rc={rc}")
                    count += 1
                    print(f"Posted {count} entries so far.")
                    time.sleep(1)  # 防止发送过快，根据平台限制可能需要调整
            print("Data posting complete. Total entries posted:", count)'''