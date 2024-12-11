from app.api.v1.endpoints.objects_api import object_router
from app.api.v1.endpoints.buckets_api import bucket_router
from app.api.v1.endpoints.users_api import user_router
from app.api.v1.endpoints.misc_api import misc_router

ROUTES = {
    "": misc_router,
    "/buckets/{bucket_name}": object_router,
    "/buckets": bucket_router,
    "/users": user_router
}