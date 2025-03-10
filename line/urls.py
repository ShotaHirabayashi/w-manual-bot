from django.urls import path

from line import views

app_name = "line"

urlpatterns = [
    # LINEコールバック
    path("callback/", views.CallbackView.as_view(), name="callback"),
    # トップページ
    path("", views.IndexView.as_view(), name="index"),
    # 予約内容確認
    path("confirm/",views.ConfirmView.as_view(),name="confirm",),
    # 予約完了
    path("done/", views.DoneView.as_view(), name="done"),
    path('description/', views.DescriptionView.as_view(), name='description'),
]
