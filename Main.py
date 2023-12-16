from flask import Flask, request, jsonify
from confluent_kafka import Producer
from flask_cors import CORS
import json
import re 

app = Flask(__name__)
CORS(app)

# Kafka configurations
cloudkafka_hostname = 'dory.srvs.cloudkafka.com'
cloudkafka_username = 'oazuqtwy'
cloudkafka_password = 'NEtRpKG_6rMchQ3W55NYhNVbu1R_6tNj'
kafka_bootstrap_servers = f'{cloudkafka_hostname}:9094'
kafka_topic = 'oazuqtwy-events'

producer_conf = {
    'bootstrap.servers': kafka_bootstrap_servers,
    'security.protocol': 'SASL_SSL',
    'sasl.mechanism': 'SCRAM-SHA-512',
    'sasl.username': cloudkafka_username,
    'sasl.password': cloudkafka_password,
}

producer = Producer(producer_conf)

# Regular expression for email validation
email_regex = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'

# Route to send events to Kafka
@app.route('/events/send', methods=['POST'])
def send_event():
    try:
        # Extract JSON data from the request
        data = request.json

        # Validate the email address
        user_email = data.get('user_email')
        if not re.match(email_regex, user_email):
            raise ValueError('Invalid email address')

        # Create an event dictionary
        event = {
            'event': data.get('event'),
            'user': {
                'email': user_email,
            },
            'data': {
                'name': data.get('user_name'),
                'date': data.get('event_date'),
            }
        }

        event_json = json.dumps(event)

        # Produce the event to the Kafka topic
        producer.produce(kafka_topic, key=event.get('user').get('email'), value=event_json)
        producer.flush() 

        return jsonify({'status': 'success', 'message': 'Event sent to Kafka'}), 200

    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)}), 500


if __name__ == '__main__':
    app.run(debug=True)