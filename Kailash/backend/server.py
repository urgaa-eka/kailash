# Entry point for uvicorn
# This file imports the astAPI app from the new backend structure
# Configure uvicorn to not add Server header
import uvicorn

from backend.main import app


class CustomUvicornServer(uvicorn.Server):
    def install_signal_handlers(self):
        pass

# Export app for uvicorn
__all__ = ['app']

if __name__ == "__main__":
    config = uvicorn.Config(
        app=app,
        host="0.0.0.0",
        port=8001,
        server_header=False,  # Disable default server header
        log_level="info"
    )
    server = uvicorn.Server(config)
    server.run()
