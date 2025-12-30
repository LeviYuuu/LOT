
class global_var:
    receive_data = []
    topic_list = []
    # 添加一个标志，以跟踪断开是不是用户主动操作的
    user_initiated_disconnect = False
    # 连接检查线程运行标志
    connection_check_running = False
