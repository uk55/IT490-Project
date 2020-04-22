import pika

credentials = pika.PlainCredentials('dev', 'sdp150516')
connection = pika.BlockingConnection(
    pika.ConnectionParameters(host='localhost'))
channel = connection.channel()

channel.queue_declare(queue='queuename')


def callback(ch, method, properties, body):
    print(" [x] Received %r" % body)


channel.basic_consume(
    queue='queuename', on_message_callback=callback, auto_ack=True)

print(' [*] Waiting for messages. To exit press CTRL+C')
channel.start_consuming()


#### working fine #####


# from flask import Flask
# from flask_restful import Resource, Api
# import pika

# app = Flask(__name__)
# api = Api(app)

# app.config['DEBUG'] = True

# message = "Hello World, its me appone"


# class HelloWorld(Resource):
#     def get(self):
#         connection = pika.BlockingConnection(
#             pika.ConnectionParameters(host='localhost'))
#         channel = connection.channel()

#         channel.queue_declare(queue='hello', durable=True)

#         channel.basic_publish(exchange='', routing_key='hello', body='Hello World!', properties=pika.BasicProperties(delivery_mode=2))

#         connection.close()

#         return {'message': message}


# api.add_resource(HelloWorld, '/api/appone/post')

# if __name__ == '__main__':
#     # Development
#     app.run(host="0.0.0.0", port=5001)