from presentation.routers.authentication_router import auth_router
from presentation.routers.organization_router import organization_router
from presentation.routers.user_router import user_router
from presentation.routers.my_user_router import my_user_router
from presentation.routers.my_organization_router import my_organization_router
from presentation.routers.organization_user_groups_router import organization_user_groups_router
from presentation.routers.alert_router import alert_router


__all__ = [
    auth_router,
    organization_router,
    user_router,
    my_user_router,
    my_organization_router,
    organization_user_groups_router,
    alert_router,
]
