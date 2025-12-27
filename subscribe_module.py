# encoding=utf-8
# subscribe_module.py
import base64
import csv
import hashlib
import hmac
import json
import ssl
import threading
import time
import paho.mqtt.client as mqtt
import schedule
from datetime import datetime
import global_var as gv

# Mosquitto服务器配置
mqtt_broker = "localhost"
mqtt_port = 1883

client = None
clientId = None
accessKey = None
accessSecret = None
csv_file = "receive_data.csv"

def on_connect(client, userdata, flags, rc):
    """连接成功回调函数"""
    print(f"已连接，返回码: {rc}")
    # 订阅所有主题
    client.subscribe("#")
    print("已成功订阅所有主题")

def on_message(client, userdata, msg):
    """接收消息回调函数"""
    print(f"已接收主题 {msg.topic} 的消息: {msg.payload.decode()}")
    # 创建一个模拟stomp frame的对象，用于兼容transform_data函数
    class MockFrame:
        def __init__(self, body):
            self.body = body
    
    mock_frame = MockFrame(msg.payload.decode())
    transform_data(mock_frame)

def on_disconnect(client, userdata, rc):
    """断开连接回调函数"""
    print(f"已断开连接，返回码: {rc}")

def on_publish(client, userdata, mid):
    """发布消息回调函数"""
    print(f"消息已发布，mid: {mid}")

def disconnect_mqtt():
    global client, clientId, accessKey, accessSecret
    try:
        if client:
            client.disconnect()
            gv.global_var.user_initiated_disconnect = True  # 设置断开标志
            # 清除clientID、accessKey和accessSecret
            clientId = None
            accessKey = None
            accessSecret = None
            print("MQTT连接已断开。")
    except Exception as e:
        print('尝试断开连接时发生错误:', e)

def connect_and_subscribe(client_id, username, password):
    """连接到Mosquitto服务器并订阅主题"""
    global client, clientId, accessKey, accessSecret
    clientId = client_id
    accessKey = username
    accessSecret = password
    
    try:
        # 创建MQTT客户端
        client = mqtt.Client(client_id=clientId)
        
        # 设置回调函数
        client.on_connect = on_connect
        client.on_message = on_message
        client.on_disconnect = on_disconnect
        client.on_publish = on_publish
        
        # 如果需要认证，设置用户名和密码
        if accessKey and accessSecret:
            client.username_pw_set(accessKey, accessSecret)
        
        # 连接到Mosquitto服务器
        client.connect(mqtt_broker, mqtt_port, 60)
        
        # 启动后台线程处理MQTT网络流量
        client.loop_start()
        
        # 清除历史连接检查任务，新建连接检查任务
        schedule.clear('conn-check')
        schedule.every(1).seconds.do(do_check).tag('conn-check')
        
        # 启动一个新线程以保持连接检查
        thread = threading.Thread(target=connection_check_timer)
        thread.start()
        
        print("已成功连接到Mosquitto服务器")
        
    except Exception as e:
        print('连接失败:', e)
        raise e

# 检查连接，如果未连接则重新建连
def do_check():
    global client, clientId, accessKey, accessSecret
    if clientId is None:
        print('请输入clientId')
        return
    
    # 检查客户端状态
    if client and client.is_connected():
        print('连接正常')
    else:
        try:
            # 只有在确保不是因为用户主动断开连接时才尝试重新连接
            if not gv.global_var.user_initiated_disconnect:
                connect_and_subscribe(clientId, accessKey, accessSecret)
        except Exception as e:
            print('尝试重新连接时发生错误:', e)

# 定时任务方法，检查连接状态
def connection_check_timer():
    while 1:
        schedule.run_pending()
        time.sleep(10)

#把时间戳转换成字符串
def timestamp_to_time(timestamp):
    if type(timestamp) == float:
        dt_obj = datetime.fromtimestamp(timestamp / 1000.0)
    else:
        dt_obj = datetime.fromtimestamp(timestamp / 1000)
    return dt_obj.strftime('%Y-%m-%d T %H:%M:%S')

# 将时间字符串转换为时间戳
def time_to_timestamp(time_str):
    dt_obj = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
    return int(dt_obj.timestamp()) * 1000

def transform_data(frame):
    str_result = frame.body
    print(type(frame.body))  # str类型
    print(str_result)
    
    try:
        result = json.loads(str_result)
        
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
        print(str(len(gv.global_var.topic_list)))
        
        # 由于我们订阅了所有主题，直接将所有数据添加到ans_data中
        # 不根据topic_list过滤，因为topic_list存储的是MQTT主题，而不是数据字段
        ans_data["temperature"] = prop_data.get("temperature", None)
        ans_data["humidity"] = prop_data.get("humidity", None)
        ans_data["pressure"] = prop_data.get("pressure", None)
        
        if ans_data and (ans_data["temperature"] is not None or ans_data["humidity"] is not None or ans_data["pressure"] is not None):
            ans_data['time'] = prop_data['time']
            ans_data["printed"] = False
            gv.global_var.receive_data.append(ans_data)
            print(format_topicData(ans_data))
            
    except json.JSONDecodeError as e:
        print(f"JSON解析错误: {e}")
    except KeyError as e:
        print(f"键错误: {e}")

def format_topicData(prop_data):
    formatted_ans = "time:" + timestamp_to_time(prop_data["time"]) + " "
    formatted_ans += (" ".join([f"{k}:{v}" for k, v in prop_data.items() if k != "printed" and k != "time"]) + "")
    return formatted_ans

def format_time(month, day, hour):
    return "2014-" + month + "-" + day + " " + hour + ":00"

def format_topiclist(topic_list):
    formatted_ans = ""
    for topic in topic_list:
        formatted_ans += topic + " "
    return formatted_ans
    
# 读取数据，整理
#写一个函数，它从csv中读取数据，然后存进receive_data里
def read_data():
    try:
        with open(csv_file, 'r') as file:
            reader = csv.reader(file)
            gv.global_var.receive_data = []
            for row in reader:
                prop_data = {}
                for i in range(0, 4):  # 确保读取所有4个字段
                    if i < len(row) and row[i] != "":
                        if i == 0:
                            prop_data["time"] = int(row[i])
                        elif i == 1:
                            prop_data["temperature"] = float(row[i])
                        elif i == 2:
                            prop_data["humidity"] = float(row[i])
                        elif i == 3:
                            prop_data["pressure"] = int(row[i])
                if prop_data:
                    gv.global_var.receive_data.append(prop_data)
            print("数据读取完成。获取的条目总数:", len(gv.global_var.receive_data))
            return gv.global_var.receive_data
    #处理异常
    except Exception as e:
        print('尝试读取数据时发生错误:', e)
        return None