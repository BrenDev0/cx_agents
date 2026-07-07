from celery import Celery
from src.settings import settings


url = f"amqp://{settings.RABBITMQ_USER}:{settings.RABBITMQ_PASSWORD}@rabbitmq:{settings.RABBITMQ_PORT}//"

worker = Celery(
    "cx_agents",
    broker=url,
    include=[
        "src.integrations.gohighlevel.celery.tasks",
        "src.knowledge_base.celery.tasks"
    ]
)