from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse

import app.settings  # noqa # muat semua konfigurasi dari file .env
from app.routers import init_routers

app = FastAPI(
    title="GetPay API", description="Your Payment Gateways Service!", version="1.0"
)
app.add_middleware(
    CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"]
)
init_routers(app)


@app.get("/", include_in_schema=False)
def index():
    return {"detail": "ok!"}


@app.get("/rapidoc", response_class=HTMLResponse, include_in_schema=False)
async def rapidoc():
    return f"""
        <!doctype html>
        <html>
            <head>
                <meta charset="utf-8">
                <script
                    type="module"
                    src="https://unpkg.com/rapidoc/dist/rapidoc-min.js"
                ></script>
            </head>
            <body>
                <rapi-doc spec-url="{app.openapi_url}"></rapi-doc>
            </body>
        </html>
    """
