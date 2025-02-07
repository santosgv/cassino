from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('jogo/', views.jogo, name='jogo'),
    path('spin/', views.spin, name='spin'),
    path('creditos/',views.creditos, name='creditos'),
    path('convert-credits/', views.convert_credits, name='convert_credits'),
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)