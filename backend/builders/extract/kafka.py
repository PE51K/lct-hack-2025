from kafka import KafkaConsumer
import json
import logging
from datetime import datetime

class KafkaMessageReader:
    def __init__(self, bootstrap_servers, topic_name, group_id=None):
        self.bootstrap_servers = bootstrap_servers
        self.topic_name = topic_name
        self.group_id = group_id
        self.consumer = None
        self.setup_logging()
        
    def setup_logging(self):
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(levelname)s - %(message)s'
        )
        self.logger = logging.getLogger(__name__)
    
    def connect(self):
        """Подключение к Kafka"""
        try:
            self.consumer = KafkaConsumer(
                self.topic_name,
                bootstrap_servers=self.bootstrap_servers,
                group_id=self.group_id,
                auto_offset_reset='latest',
                enable_auto_commit=True,
                value_deserializer=self.deserialize_message
            )
            self.logger.info(f"Успешно подключено к Kafka: {self.bootstrap_servers}")
            self.logger.info(f"Подписан на топик: {self.topic_name}")
            return True
        except Exception as e:
            self.logger.error(f"Ошибка подключения: {e}")
            return False
    
    def deserialize_message(self, message):
        """Десериализация сообщения"""
        if message is None:
            return None
        
        try:
            return json.loads(message.decode('utf-8'))
        except json.JSONDecodeError:
            return message.decode('utf-8')
        except Exception:
            return message
    
    def process_message(self, message):
        """Обработка отдельного сообщения"""
        timestamp = datetime.fromtimestamp(message.timestamp / 1000).strftime('%Y-%m-%d %H:%M:%S')
        
        print(f"\n[{timestamp}] Сообщение из {message.topic}")
        print(f"Партиция: {message.partition}, Оффсет: {message.offset}")
        print(f"Ключ: {message.key}")
        print(f"Данные: {message.value}")
        print("-" * 50)
    
    def start_consuming(self, max_messages=None):
        """Начало потребления сообщений"""
        if not self.consumer:
            self.logger.error("Consumer не инициализирован")
            return
        
        message_count = 0
        self.logger.info("Начинаем чтение сообщений...")
        
        try:
            for message in self.consumer:
                self.process_message(message)
                message_count += 1
                
                if max_messages and message_count >= max_messages:
                    self.logger.info(f"Достигнут лимит в {max_messages} сообщений")
                    break
                    
        except KeyboardInterrupt:
            self.logger.info("Получен сигнал прерывания")
        except Exception as e:
            self.logger.error(f"Ошибка при чтении: {e}")
        finally:
            self.close()
    
    def close(self):
        """Закрытие соединения"""
        if self.consumer:
            self.consumer.close()
            self.logger.info("Соединение закрыто")

def main():
    # Конфигурация
    config = {
        'bootstrap_servers': ['localhost:9092'],
        'topic_name': 'MyTopic',
        'group_id': 'python-consumer-group',
        'max_messages': 100  # None для бесконечного чтения
    }
    
    # Создание и запуск reader
    reader = KafkaMessageReader(
        config['bootstrap_servers'],
        config['topic_name'],
        config['group_id']
    )
    
    if reader.connect():
        reader.start_consuming(config['max_messages'])

if __name__ == "__main__":
    main()
