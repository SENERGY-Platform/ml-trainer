from data.kafka.kafka import KafkaLoader
from config import Config 

k = KafkaLoader("http://localhost:8088", Config.KAFKA_TOPIC_CONFIG, "test")
k.connect()
k.load_data()
print(k.get_data())