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
            # 使用简单的print语句，避免格式化字符串可能导致的问题
            print("MQTT已连接 (rc=", rc, ")")
        else:
            # 使用简单的print语句，避免格式化字符串可能导致的问题
            print("MQTT连接失败 (rc=", rc, ")")

    def on_disconnect(self, client, userdata, rc):
        self.connected = False
        # 使用简单的print语句，避免格式化字符串可能导致的问题
        print("MQTT已断开连接 (rc=", rc, ")")

    def on_publish(self, client, userdata, mid):
        # 使用简单的print语句，避免格式化字符串可能导致的问题
        print("消息已发布 (mid=", mid, ")")

    def on_message(self, client, userdata, msg):
        # 使用简单的print语句，避免格式化字符串可能导致的问题
        print("已接收消息 (topic=", msg.topic, ", payload=", msg.payload.decode(), ", qos=", msg.qos, ")")

    def connect(self):
        try:
            # 检查MQTT客户端的状态
            if self.client is None:
                print("MQTT客户端未初始化")
                return False
            
            print("尝试连接到MQTT服务器:", self.broker, ":", self.port)
            
            # 先断开可能存在的连接
            try:
                self.client.disconnect()
            except:
                pass
            
            # 使用connect_async代替connect，避免阻塞
            self.client.connect_async(self.broker, self.port, 60)
            self.client.loop_start()  # 开启后台循环
            print("MQTT客户端正在连接...")
            
            # 直接返回，不等待连接完成
            # 连接状态会通过on_connect回调更新
            return True
        except Exception as e:
            print("MQTT连接错误:", e)
            import traceback
            traceback.print_exc()
            return False

    def disconnect(self):
        self.client.loop_stop()
        self.client.disconnect()
        print("MQTT客户端正在断开连接...")

    def publish(self, topic, message):
        try:
            if not self.connected:
                print("MQTT客户端未连接，无法发布消息。")
                return -1, 0
            if isinstance(message, dict):
                message_str = json.dumps(message)
                print(f"[DEBUG] 发布消息到主题 {topic}: {message_str[:100]}...")
                message = message_str
            else:
                print(f"[DEBUG] 发布消息到主题 {topic}: {message[:100]}...")
            result = self.client.publish(topic, message)
            print(f"[DEBUG] 发布结果: rc={result.rc}, mid={result.mid}")
            return result.rc, result.mid
        except Exception as e:
            print("[DEBUG] 发布错误:", e)
            return -1, 0
    
    def subscribe(self, topic):
        try:
            result, mid = self.client.subscribe(topic)
            return result, mid
        except Exception as e:
            print("订阅错误:", e)
            return -1, 0
    
    def unsubscribe(self, topic):
        try:
            result, mid = self.client.unsubscribe(topic)
            return result, mid
        except Exception as e:
            print("取消订阅错误:", e)
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
            # 使用简单的print语句，避免格式化字符串可能导致的问题
            print("属性上报成功:", rc, ", 请求ID:", request_id)
        else:
            # 使用简单的print语句，避免格式化字符串可能导致的问题
            print("属性上报失败, rc=", rc)
    
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