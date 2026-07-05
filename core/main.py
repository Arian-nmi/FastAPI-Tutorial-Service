from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
from tasks.routs import router as tasks_routes
from users.routs import router as users_routes
from core.config import settings
import time


tags_metadata = [
    {
        "name": "tasks",
        "description": "Operations related to tasks management.",
        "externalDocs": {
            "description": "Tasks API Documentation",
            "url": "https://example.com/docs/tasks"
        }
    }
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Perform any startup tasks here
    print("Starting up the application...")
    yield
    # Perform any shutdown tasks here
    print("Shutting down the application...")


app = FastAPI(
    title="Todo Application",
    description="this is a section for description",
    version="0.0.1",
    terms_of_service="http://example.com/terms/",
    contact={
        "name": "Mr. Arian",
        "url": "https://github.com/Arian-nmi",
        "email": "naeimiarian82@gmail.com",
    },
    license_info={
        "name": "MIT",
    },
    lifespan=lifespan, 
    openapi_tags=tags_metadata
)


from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

#setup the cache backend
redis = aioredis.from_url(settings.REDIS_URL)
cache_backend = RedisBackend(redis)
FastAPICache.init(cache_backend, prefix="fastapi-cache")



app.include_router(tasks_routes)
app.include_router(users_routes)

@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.perf_counter()
    response = await call_next(request)
    proccess_time = time.perf_counter() - start_time
    response.headers["X-Process-Time"] = str(proccess_time)
    return response


@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request, exc):
    error_response = {
        "error": True,
        "status_code": exc.status_code,
        "message": str(exc.detail)
    }

    return JSONResponse(
        status_code=exc.status_code,
        content=error_response
    )


@app.exception_handler(RequestValidationError)
async def http_validation_exception_handler(request, exc):
    error_response = {
        "error": True,
        "status_code": status.HTTP_422_UNPROCESSABLE_ENTITY,
        "message": "There was a problem with the data you provided.",
        "content": exc.errors()
    }

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=error_response
    )


from core.email_util import send_mail

@app.get("/send-mail", status_code=200)
async def test_send_mail():
    await send_mail(
        subject="Test mail from FastAPI",
        recipients=["recipient@example.com"],
        body="This is a test mail sent from FastAPI",
    )
    return JSONResponse(content={"detail": "Email has been sent"})