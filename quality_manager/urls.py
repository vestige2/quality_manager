from django.conf import settings
from django.conf.urls.static import static
from m3 import get_app_urlpatterns


urlpatterns = [
]

urlpatterns.extend(
    static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
)

urlpatterns.extend(
    get_app_urlpatterns()
)
