from kafka import KafkaConsumer

class KafkaSource:
    def __init__(self, topic):
        self.consumer = KafkaConsumer(topic, bootstrap_servers="kafka:9092")

    def stream(self):
        for msg in self.consumer:
            yield msg.value
