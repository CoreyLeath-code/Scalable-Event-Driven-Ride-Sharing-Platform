# Daily Log

## 2026-08-12 — Load-balancer gap recorded

An infrastructure audit found that the Compose demo exposes one `driver-location-api` instance directly on host port 8000. The event-driven architecture has no local Layer-7 gateway, multi-replica API routing, or unhealthy-replica resilience demonstration.

Tracking issue: [#17 — add a gateway load balancer for horizontally scaled APIs](https://github.com/CoreyLeath-code/Scalable-Event-Driven-Ride-Sharing-Platform/issues/17).

This record does **not** claim a load balancer, horizontal scaling, resilience test, or benchmark result has been implemented. The issue defines the required implementation and validation scope.
