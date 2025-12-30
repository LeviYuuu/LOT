# publish_app.py
# Function: 用于发布消息的Flask应用程序
from flask import Flask, render_template, request, jsonify
import datetime
from MQTTClient import MQTTClient
import csv
import json
import time
import threading

publish_file = "THPData/THP_data.csv"
# 定义变量
product_key = "test_product"
device_name = "THP-DataSystems"
device_secret = "test_secret"

# 使用Mosquitto服务器
broker_address = "localhost"  # Mosquitto服务器地址
broker_port = 1883  # Mosquitto服务器端口

mqtt_topic_post = f'/sys/{product_key}/{device_name}/thing/event/property/post'  # 用于发布消息的主题
mqtt_topic_set = f'/sys/{product_key}/{device_name}/thing/service/property/set'  # 用于发布消息的主题


app = Flask(__name__)
mqtt_client = MQTTClient(product_key, device_name, device_secret, broker_address, broker_port)

# 全局变量，用于存储状态
publish_status = {
    'count': 0,
    'complete': False,
    'error': None
}
stop_publishing = False # 用于停止发布数据的标志

# 读取public_file中的数据，并按照第一列的数据从小到大排序生成信文档，排序完成后写回文件
def sort_data(publish_file):
    with open(publish_file, 'r') as file:
        reader = csv.reader(file)
        data = list(reader)
        data.sort(key=lambda x: int(x[0]))
    with open(publish_file, 'w', newline='') as file:
        writer = csv.writer(file)
        writer.writerows(data)

# 读取并发布数据的后台线程
def read_and_publish_data(topic, publish_file):
    global publish_status, stop_publishing
    try:
        # ... 发布数据的代码 ...
        # 确保更新 publish_status['count'] 和 publish_status['complete'] ...
        sort_data(publish_file) # 排序数据
        with open(publish_file, 'r') as file:
            reader = csv.reader(file)
            for row in reader:
                if stop_publishing:
                    break
                if len(row) == 4:
                    # 从行中提取数据并构建属性字典
                    prop_data = {
                        "DetectTime": str(int(row[0])),  # 假设 CSV 文件中的时间戳已经是毫秒格式
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
                    rc, request_id = mqtt_client.publish(topic, payload)
                    publish_status['count'] += 1
                    if rc == 0:
                        print(f"已发布 {publish_status['count']} 条记录。")
                    else:
                        print(f"属性发布失败, rc={rc}")
                        publish_status['error'] = f"第 {publish_status['count']} 条发布失败, rc={rc}"
                        publish_status['complete'] = True
                    time.sleep(1)  # 防止发送过快，根据平台限制可能需要调整
            print("数据发布完成。发布的记录总数:", {publish_status['count']})
    except Exception as e:
        publish_status['error'] = str(e)
    finally:
        publish_status['complete'] = True
        stop_publishing = False    # 重置停止标志

@app.route('/')
def index():
    return render_template('publish.html')  # 确保HTML文件名与实际文件名相匹配

@app.route('/connect', methods=['POST'])
def connect():
    if not mqtt_client.is_connected():
        # 调用MQTTClient的connect方法，它会返回实际的连接状态
        connected = mqtt_client.connect()
        if connected:
            return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'connected', 'message': '连接成功。'})
        else:
            return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'error', 'message': '连接失败，请检查服务器是否正常运行。'})
    else:
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'already_connected', 'message': '已经连接。'})

@app.route('/disconnect', methods=['POST'])
def disconnect():
    if mqtt_client.is_connected():
        mqtt_client.disconnect()
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'disconnected', 'message': '成功断开连接。'})
    else:
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'already_disconnected', 'message': '已经断开连接。'})


@app.route('/subPost', methods=['POST'])
def subPost():
    if not mqtt_client.is_connected():
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'error', 'message': '尚未连接到MQTT服务器，请先手动连接。'})
    mqtt_client.subscribe(mqtt_topic_post)
    return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'success', 'message': '已订阅主题: /thing/event/property/post。'})

@app.route('/unSubPost', methods=['POST'])
def connunSubPostect():
    if not mqtt_client.is_connected():
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'error', 'message': '尚未连接到MQTT服务器，请先手动连接。'})
    mqtt_client.unsubscribe(mqtt_topic_post)
    return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'success', 'message': '已取消订阅主题: /thing/event/property/post。'})

@app.route('/publishRandom', methods=['POST'])
def publishRandom():
    if not mqtt_client.is_connected():
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'error', 'message': '尚未连接到MQTT服务器，请先手动连接。'})
    # 发布随机数据
    mqtt_client.post_random_data(mqtt_topic_post)
    return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'success', 'message': '随机数据已发布。'})

@app.route('/startPublish', methods=['POST'])
def start_publish():
    if not mqtt_client.is_connected():
        return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'error', 'message': '尚未连接到MQTT服务器，请先手动连接。'})
    global publish_status,stop_publishing
    stop_publishing = False  # 确保停止标志为False，以便开始新的发布流程
    publish_status = {'count': 0, 'complete': False, 'error': None}
    thread = threading.Thread(target=read_and_publish_data, args=(mqtt_topic_post, publish_file))
    thread.start()
    return jsonify({'timestamp': str(datetime.datetime.now()), 'status': 'started', 'message': '数据发布已开始。'})

@app.route('/publishStatus', methods=['GET'])
def publish_status():
    global publish_status
    return jsonify(publish_status)

@app.route('/stopPublish', methods=['POST'])
def stop_publish():
  global stop_publishing
  stop_publishing = True # 设置停止标志为真
  return jsonify({'message': '正在停止发布进程...'})

if __name__ == '__main__':
    import os
    # 隐藏Flask开发服务器警告
    os.environ['FLASK_ENV'] = 'development'
    import warnings
    warnings.filterwarnings("ignore", message=".*development server.*")
    
    app.run(debug=True, port=5000, use_reloader=False)
