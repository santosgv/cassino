from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    path('jogo/', views.jogo, name='jogo'),
    path('spin/', views.spin, name='spin'),
    path('creditos/',views.creditos, name='creditos'),
    path('convert-credits/', views.convert_credits, name='convert_credits'),
    path('request_pix_withdrawal/',views.request_pix_withdrawal, name='request_pix_withdrawal'),

    path("purchase/<str:package_name>/", views.purchase_credits, name="purchase_credits"),
    path("purchase/success/<str:package_name>/", views.purchase_success, name="purchase_success"),
    path("purchase/failure/", views.purchase_failure, name="purchase_failure"),
    path("purchase/pending/", views.purchase_pending, name="purchase_pending")
]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)