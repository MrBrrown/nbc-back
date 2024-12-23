from app.api.v1.endpoints.files_api import file_router
from app.api.v1.endpoints.buckets_api import bucket_router
from app.api.v1.endpoints.users_api import user_router
from app.api.v1.endpoints.misc_api import misc_router



ROUTES = {
    "": misc_router,
    "/files": file_router,
    "/buckets": bucket_router,
    "/users": user_router
}
