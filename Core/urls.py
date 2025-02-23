from . import views
from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from .utils import get_multiplier,update_credits,lose_bet


urlpatterns = [
    path('jogo/', views.jogo, name='jogo'),
    path('spin/', views.spin, name='spin'),
    path('roleta/',views.roleta, name='roleta'),
    path('spin_roulette/',views.spin_roulette, name='spin_roulette'),
    path('get_multiplier/', get_multiplier, name='get_multiplier'),
    path('update_credits/', update_credits, name='update_credits'),
    path('lose_bet/',lose_bet ,name='lose_bet'),
    path('aviator/',views.aviator , name='aviator'),
    path('creditos/',views.creditos, name='creditos'),
    path('convert-credits/', views.convert_credits, name='convert_credits'),
    path('request_pix_withdrawal/',views.request_pix_withdrawal, name='request_pix_withdrawal'),
    path("purchase/<str:package_name>/", views.purchase_credits, name="purchase_credits"),
    path('livepix_webhook/',views.livepix_webhook, name='livepix_webhook')

]

urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)