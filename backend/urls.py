from django.contrib import admin
from django.urls import path
from api.views import UploadView, generate_pdf
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/upload/', UploadView.as_view()),
    path('api/report/', generate_pdf), 
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)