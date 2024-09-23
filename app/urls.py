from django.urls import path
from .Account import views as account_views
from .matching import views as matching_view

from django.conf import settings
from django.conf.urls.static import static

from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    path('signup/', account_views.RegisterView.as_view(), name='user-signup'), # 新規登録
    path('login/', account_views.LoginView.as_view(), name='user-login'), # ログイン
    path('users/<str:user_id>/', account_views.UserDetailView.as_view(), name='user-detail'), # ユーザ情報取得
    path('update/', account_views.UserUpdateView.as_view(), name='user-update'), # ユーザ情報更新
    path('close/<str:user_id>/', account_views.CloseAccountView.as_view(), name='close-account'), # アカウント削徐

    path('user/<str:user_id>/match/', matching_view.UserMatchingView.as_view(), name='user_matching'), # マッチング

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWTトークンの取得
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # JWTトークンのリフレッシュ
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)