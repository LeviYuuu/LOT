#!/usr/bin/env python3
# MQTT通信诊断脚本
import json
import time
import paho.mqtt.client as mqtt
import sys

# 配置
MQTT_BROKER = "localhost"
MQTT_PORT = 1883
TEST_TOPIC = '/sys/test_product/THP-DataSystems/thing/event/property/post'

# 测试结果
results = {
    "mosquitto_running": False,
    "can_connect": False,
    "can_publish": False,
    "can_subscribe": False,
    "message_received": False,
    "errors": []
}

# 回调函数
def on_connect(client, userdata, flags, rc):
    if rc == 0:
        results["can_connect"] = True
        print("✅ 成功连接到MQTT服务器")
        if client == sub_client:
            client.subscribe(TEST_TOPIC)
            print(f"✅ 成功订阅主题: {TEST_TOPIC}")
            results["can_subscribe"] = True
    else:
        results["errors"].append(f"连接失败 (rc={rc})")
        print(f"❌ 连接失败 (rc={rc})")

def on_publish(client, userdata, mid):
    results["can_publish"] = True
    print("✅ 消息发布成功")

def on_message(client, userdata, msg):
    results["message_received"] = True
    print(f"✅ 收到消息：")
    print(f"  主题: {msg.topic}")
    print(f"  内容: {msg.payload.decode()}")
    
    # 解析消息
    try:
        result = json.loads(msg.payload.decode())
        if 'params' in result and 'DetectTime' in result['params']:
            print(f"  数据解析成功：")
            print(f"    时间: {result['params']['DetectTime']}")
            print(f"    温度: {result['params']['CurrentTemperature']}")
            print(f"    湿度: {result['params']['CurrentHumidity']}")
            print(f"    气压: {result['params']['CurrentPressure']}")
        else:
            print("  消息格式不符合预期")
    except Exception as e:
        print(f"  消息解析失败: {e}")
        results["errors"].append(f"消息解析失败: {e}")

# 检查Mosquitto是否运行
def check_mosquitto():
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    result = sock.connect_ex((MQTT_BROKER, MQTT_PORT))
    sock.close()
    
    if result == 0:
        results["mosquitto_running"] = True
        print("✅ Mosquitto服务器正在运行")
    else:
        results["errors"].append("Mosquitto服务器未运行")
        print("❌ Mosquitto服务器未运行")

# 运行诊断
def run_diagnostic():
    print("开始MQTT通信诊断...")
    print(f"测试主题: {TEST_TOPIC}")
    
    # 检查Mosquitto
    check_mosquitto()
    if not results["mosquitto_running"]:
        return
    
    # 创建客户端
    global sub_client
    sub_client = mqtt.Client(client_id="diagnose_subscriber")
    sub_client.on_connect = on_connect
    sub_client.on_message = on_message
    
    pub_client = mqtt.Client(client_id="diagnose_publisher")
    pub_client.on_connect = on_connect
    pub_client.on_publish = on_publish
    
    # 连接客户端
    try:
        sub_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        sub_client.loop_start()
        
        pub_client.connect(MQTT_BROKER, MQTT_PORT, 60)
        pub_client.loop_start()
        
        # 等待连接
        time.sleep(1)
        
        # 发布测试消息
        if results["can_connect"]:
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
            
            print(f"📤 发布测试消息到主题: {TEST_TOPIC}")
            pub_client.publish(TEST_TOPIC, json.dumps(test_payload))
            
            # 等待接收消息
            time.sleep(2)
    except Exception as e:
        results["errors"].append(f"客户端操作失败: {e}")
        print(f"❌ 客户端操作失败: {e}")
    finally:
        sub_client.loop_stop()
        sub_client.disconnect()
        pub_client.loop_stop()
        pub_client.disconnect()

# 显示诊断报告
def show_report():
    print("\n=== MQTT诊断报告 ===")
    print(f"Mosquitto服务器运行: {'✅ 是' if results['mosquitto_running'] else '❌ 否'}")
    print(f"能够连接服务器: {'✅ 是' if results['can_connect'] else '❌ 否'}")
    print(f"能够发布消息: {'✅ 是' if results['can_publish'] else '❌ 否'}")
    print(f"能够订阅主题: {'✅ 是' if results['can_subscribe'] else '❌ 否'}")
    print(f"能够接收消息: {'✅ 是' if results['message_received'] else '❌ 否'}")
    
    if results['errors']:
        print("\n❌ 错误列表:")
        for error in results['errors']:
            print(f"  - {error}")
    
    if all(results[key] for key in ['mosquitto_running', 'can_connect', 'can_publish', 'can_subscribe', 'message_received']):
        print("\n🎉 所有测试通过！MQTT通信正常")
        print("\n📋 可能的问题：")
        print("  - 应用可能没有正确使用测试的主题")
        print("  - 应用的连接参数可能不正确")
        print("  - 应用可能没有正确处理连接状态")
    else:
        print("\n❌ MQTT通信存在问题")

if __name__ == "__main__":
    run_diagnostic()
    show_report()
