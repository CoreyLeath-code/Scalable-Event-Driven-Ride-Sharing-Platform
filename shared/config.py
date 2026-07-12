from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    APP_NAME: str = "RideSharingPlatform"
    ENVIRONMENT: str = "development"

    # Kafka
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    KAFKA_TOPIC_RIDE_REQUESTED: str = "ride_requested"
    KAFKA_TOPIC_DRIVER_ASSIGNED: str = "driver_assigned"

    # Database
    DATABASE_URL: str = "postgresql://postgres:postgres@localhost:5432/rides"

    # Redis
    REDIS_HOST: str = "localhost"
    REDIS_PORT: int = 6379

    # Observability
    ENABLE_METRICS: bool = True

    class Config:
        env_file = ".env"


settings = Settings()
