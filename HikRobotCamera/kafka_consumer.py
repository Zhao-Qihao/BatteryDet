from kafka import KafkaConsumer
import json

# 初始化Kafka消费者
consumer = KafkaConsumer(
    'TOPIC_VISION_BATTERY_STATUS',  # 订阅的主题
    bootstrap_servers=['localhost:9092'],  # Kafka集群地址
    # auto_offset_reset='earliest',  # 从最早的消息开始读取（也可以设置为 'latest' 以读取最新消息）
    auto_offset_reset='latest',  # 从最早的消息开始读取（也可以设置为 'latest' 以读取最新消息）
    enable_auto_commit=True,  # 自动提交偏移量
    group_id='battery_status_group',  # 消费者组ID，多个消费者可以共享一个组
    value_deserializer=lambda x: json.loads(x.decode('utf-8'))  # 将消息从字节反序列化为JSON对象
)

print("Starting to consume messages from TOPIC_VISION_BATTERY_STATUS...")

# 消费消息
for message in consumer:
    # 获取消息内容
    message_value = message.value
    print(f"Received message: {message_value}")
    
    # 提取并处理消息中的状态信息
    status = message_value.get('status', 0)
    
    if status == 1:
        print("Battery is in place (status: 1).")
    elif status == 0:
        print("Battery is not in place (status: 0).")
    else:
        print(f"Unknown status received: {status}")

# 如果需要关闭消费者，使用以下命令：
# consumer.close()
