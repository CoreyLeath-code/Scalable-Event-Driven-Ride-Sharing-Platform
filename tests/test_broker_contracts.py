import pytest

from kafka_bus import KafkaEventBus
from rabbitmq_bus import RabbitMQEventBus
from redis_bus import RedisEventBus


@pytest.mark.asyncio
async def test_kafka_publish_requires_connect():
    with pytest.raises(RuntimeError, match="Call connect"):
        await KafkaEventBus().publish("rides", {"event_type": "ride.requested"})


@pytest.mark.asyncio
async def test_redis_publish_requires_connect():
    with pytest.raises(RuntimeError, match="Call connect"):
        await RedisEventBus().publish("rides", {"event_type": "ride.requested"})


@pytest.mark.asyncio
async def test_rabbitmq_publish_requires_connect():
    with pytest.raises(RuntimeError, match="Call connect"):
        await RabbitMQEventBus().publish("rides", {"event_type": "ride.requested"})


@pytest.mark.asyncio
async def test_broker_close_is_safe_before_connect():
    await KafkaEventBus().close()
    await RedisEventBus().close()
    await RabbitMQEventBus().close()
