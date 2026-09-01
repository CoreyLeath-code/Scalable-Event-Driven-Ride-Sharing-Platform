from fastapi.routing import APIRoute

import api_router
from auth import require_authenticated_request


def route_by_path(path: str) -> APIRoute:
    for route in api_router.router.routes:
        if isinstance(route, APIRoute) and route.path == path:
            return route
    raise AssertionError(f"route not found: {path}")


def dependency_calls(route: APIRoute):
    return {dependency.call for dependency in route.dependant.dependencies}


def test_sensitive_driver_routes_wire_auth_dependency():
    for path in ("/drivers", "/drivers/{driver_id}", "/count"):
        assert require_authenticated_request in dependency_calls(route_by_path(path))


def test_health_and_readiness_remain_probeable_without_auth_dependency():
    for path in ("/health", "/ready"):
        assert require_authenticated_request not in dependency_calls(route_by_path(path))
