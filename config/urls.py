from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path
from django.http import HttpResponse

def return_200(request):
    return HttpResponse("OK", status=200)


urlpatterns = [
    path("admin/", admin.site.urls),
    # アカウント認証
    path("accounts/", include("accounts.urls")),
    # 認証ライブラリ
    path("accounts/", include("allauth.urls")),
    # LINE
    path("line/", include("line.urls")),
    # health checkように200を返すだけのエンドポイント
    path("health/", return_200),
    path("", return_200),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)