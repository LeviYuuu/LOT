import requests

# 检查发布端
try:
    r = requests.get('http://localhost:5000/', timeout=2)
    print('发布端运行正常')
except:
    print('发布端未运行')

# 检查订阅端
try:
    r = requests.get('http://localhost:5001/', timeout=2)
    print('订阅端运行正常')
except:
    print('订阅端未运行')
