from django.db import connection


class SSEConnectionMiddleware:
    """
    Middleware that closes database connections before SSE streaming responses.

    When using Django with ASGI servers (Hypercorn, Uvicorn, Daphne), database
    connections opened by middleware (like AuthenticationMiddleware) remain open
    for the entire duration of streaming responses. For long-lived SSE connections,
    this causes connection pool exhaustion.

    This middleware closes the DB connection right before the SSE view runs,
    in the same thread where the connection was opened.
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Close DB connection before SSE endpoints to prevent connection leak
        # during long-lived streaming responses
        if request.path.endswith('/sse/'):
            print("Closing DB connection for SSE request")
            connection.close()

        return self.get_response(request)