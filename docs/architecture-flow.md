# Architecture flow reference

This manually maintained diagram was relocated from the repository root during root-directory hygiene.

```text
[ Frontend Clients (Web / Mobile) ]
        ↓
[ API Gateway (REST / WebSocket) ]
        ↓
[ Backend Microservices / Business Logic ]
        ↓
[ Event Bus (Kafka / RabbitMQ) ]
        ↓
[ Database (SQL / NoSQL) ]
        ↓
[ Analytics / Monitoring ]
```
