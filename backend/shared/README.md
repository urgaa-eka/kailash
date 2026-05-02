# Kailash shared library

Shared library used by all backend services and modules.

```python
from backend.shared import (
    BaseServiceSettings, build_app, ApiResponse, ErrorDetail,
    PlatformError, NotFoundError, ValidationError, UpstreamError,
    require_internal_token, configure_logging, get_logger,
)
```

`build_app(settings, routers=[...])` returns a FastAPI app with CORS,
request-id middleware, `/health`, `/`, `/metrics` and a platform error
handler already wired.
