from django.urls import path
from .Account import views as account_views
from .Others import views as other_views
from .Matching import views as matching_views

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
    path('close/<str:user_id>/', account_views.CloseAccountView.as_view(), name='close-account'), # アカウント削

    path('generate-questions/<str:user_id>/', other_views.generate_questions, name='generate_questions'),
    path('generate-profile/<str:user_id>/', other_views.generate_profile, name='generate_profile'),

    path('matching/', matching_views.match_user, name='matching'),
    path('get_matched_users/', matching_views.get_matched_users, name='matching-list'),

    path('update_profile_with_feedback/<str:user_id>/', other_views.update_profile_with_feedback, name='feedback'),

    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # JWTトークンの取得
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'), # JWTトークンのリフレッシュ
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)