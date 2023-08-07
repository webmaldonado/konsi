from fastapi import FastAPI, Body
from config import *
import pika
import uvicorn

app = FastAPI()


def send_to_rabbitmq(cpf: str):
    connection = pika.BlockingConnection(pika.ConnectionParameters(host=RABBITMQ_HOST))
    try:
        channel = connection.channel()
        channel.queue_declare(queue=RABBITMQ_QUEUE)
        channel.basic_publish(exchange='', routing_key=RABBITMQ_QUEUE, body=cpf)
        return "Sent to RabbitMq"
    except Exception as e:
        print("Error in RabbitMQ:", e)
        return "Error in RabbitMQ"
    finally:
        connection.close()


@app.post("/enviar_dados/")
def enviar_dados(cpf: str = Body(...)):
    return send_to_rabbitmq(cpf)


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
