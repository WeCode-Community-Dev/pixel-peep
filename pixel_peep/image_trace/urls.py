from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('', views.image_similarity_upload, name='image-similarity'),
    path('img-upload/', views.upload_image_to_db, name='image-upload'),      
    path('detect-org-img/', views.optimised_solution, name='detect-original-img'),

] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)



