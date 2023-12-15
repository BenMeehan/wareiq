from flask import Flask
from flask_mail import Mail, Message
from confluent_kafka import Consumer, Producer, KafkaError
import traceback
import json

app = Flask(__name__)

# Flask-Mail configuration - using gmail as provider
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
app.config['MAIL_USERNAME'] = 'wareiqben@gmail.com'
app.config['MAIL_PASSWORD'] = 'zhat yeqz rvpm tzdd'
app.config['MAIL_DEFAULT_SENDER'] = 'wareiqben@gmail.com'

mail = Mail(app)

# Kafka configurations
cloudkafka_hostname = 'dory.srvs.cloudkafka.com'
cloudkafka_username = 'oazuqtwy'
cloudkafka_password = 'NEtRpKG_6rMchQ3W55NYhNVbu1R_6tNj'
kafka_bootstrap_servers = f'{cloudkafka_hostname}:9094'
kafka_topic = 'oazuqtwy-events'
dlq_topic = 'oazuqtwy-dlq'

# Consumer to consume events and send emails
consumer_conf = {
    'bootstrap.servers': kafka_bootstrap_servers,
    'group.id': f'{cloudkafka_username}-email_consumer_group',
    'auto.offset.reset': 'earliest',
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'SCRAM-SHA-512',
    'sasl.username': cloudkafka_username,
    'sasl.password': cloudkafka_password,
}

# Producer for dead letter queue (failed messages)
producer_conf = {
    'bootstrap.servers': kafka_bootstrap_servers,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'SCRAM-SHA-512',
    'sasl.username': cloudkafka_username,
    'sasl.password': cloudkafka_password,
}

consumer = Consumer(consumer_conf)
consumer.subscribe([kafka_topic])

producer = Producer(producer_conf)

def consume_and_send_email():
    try:
        while True:
            msg = consumer.poll(1.0)

            if msg is None:
                continue
            if msg.error():
                if msg.error().code() == KafkaError._PARTITION_EOF:
                    continue
                else:
                    print(msg.error())
                    break

            try:
                kafka_message = json.loads(msg.value().decode('utf-8'))
            except json.JSONDecodeError as je:
                print(f"Error decoding JSON: {je}")
                continue
            except KeyError as ke:
                print(f"Missing key in JSON: {ke}")
                continue

            # Send email with user details and event with retry mechanism
            send_email_with_retry(kafka_message)

            # Commit the offset only if the email was sent successfully
            consumer.commit()
    except Exception as e:
        print(f"Error occurred: {e}")
        # traceback.print_exc()
    finally:
        consumer.close()

    return 'Consumed messages from Kafka and sent emails'

def send_email_with_retry(kafka_message, max_retries=5):
    retries = 0
    user_email = kafka_message['user']['email']
    user_name = kafka_message.get('data', {}).get('name')
    date = kafka_message.get('data', {}).get('date')
    event = kafka_message.get('event')
    while retries < max_retries:
        try:
            # Attempt to send email
            send_email(user_email, user_name, date, event)
            break  # Break out of the retry loop if successful
        except Exception as e:
            retries += 1
            print(f"Error sending email (Attempt {retries}/{max_retries}): {e}")
            # traceback.print_exc()
    else:
        # If all retries fail, log and move the message to the DLQ
        print(f"All retry attempts failed for message: {event}")
        move_to_dlq(kafka_message)

def send_email(user_email, user_name, date, event):
    with app.app_context():
        try:
            subject = f'{user_name} - {date}'
            body = f'Event: {event}'

            msg = Message(subject=subject, recipients=[user_email], body=body)
            mail.send(msg)

            print(f'Email sent to {user_email} for event: {event}')

        except Exception as e:
            print(f"Error sending email: {e}")
            # traceback.print_exc()

def move_to_dlq(message):
    try:
        # Produce the message to the DLQ topic
        producer.produce(dlq_topic, key=message.key(), value=message.value())
        producer.flush()

        print(f"Message moved to DLQ: {message.value()}")
    except Exception as e:
        print(f"Error moving message to DLQ: {e}")
        traceback.print_exc()

print("Consumer started...")
consume_and_send_email()