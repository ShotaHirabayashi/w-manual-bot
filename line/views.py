from django.conf import settings
from django.http.response import (
    HttpResponse,
    HttpResponseBadRequest,
    HttpResponseServerError,
)
from django.shortcuts import render, redirect
from django.urls import reverse
from django.utils.decorators import method_decorator
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import View

from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError, LineBotApiError
from linebot.models import (
    FollowEvent,
    MessageEvent,
    PostbackEvent,
    TextMessage,
    UnfollowEvent,
)

from .forms import CustomerForm
from .models import Customer, QuestionMessage
from .line_messages import send_menu_message
from .open_ai_views import open_ai_chat

line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)
handler = WebhookHandler(settings.CHANNEL_SECRET)


# LINEコールバック
class CallbackView(View):
    def get(self, request):
        return HttpResponse("OK")

    def post(self, request):
        signature = request.META["HTTP_X_LINE_SIGNATURE"]
        body = request.body.decode("utf-8")

        try:
            handler.handle(body, signature)
        except InvalidSignatureError:
            return HttpResponseBadRequest()
        except LineBotApiError as e:
            print(e)
            return HttpResponseServerError()

        return HttpResponse("OK")

    @method_decorator(csrf_exempt)
    def dispatch(self, *args, **kwargs):
        return super(CallbackView, self).dispatch(*args, **kwargs)

    # 友達追加
    @handler.add(FollowEvent)
    def handle_follow(event):
        line_id = event.source.user_id

        # 既存のユーザーをチェック
        if not Customer.objects.filter(line_id=line_id).exists():
            try:
                # LINEユーザー情報を取得
                profile = line_bot_api.get_profile(line_id)
                # LINEユーザー名
                name = profile.display_name

                # 顧客登録
                Customer.objects.create(name=name, line_id=line_id)
                print("新しい友達追加: ", name)
            except LineBotApiError as e:
                print("新しい友達追加エラー: ", e)
        else:
            print("ユーザーはすでに登録されています。")

    # 友達解除
    @handler.add(UnfollowEvent)
    def handle_unfollow(event):
        line_id = event.source.user_id
        # 対応する顧客を見つけて削除
        try:
            user = Customer.objects.get(line_id=line_id)
            user.delete()
            print("友達解除されたユーザーを削除しました: ", line_id)
        except Customer.DoesNotExist:
            print("削除するユーザーが見つかりませんでした。", line_id)

    # テキストメッセージ
    @handler.add(MessageEvent, message=TextMessage)
    def text_message(event):
        try:
            line_id = event.source.user_id

            customer = Customer.objects.get(line_id=line_id)

            if customer.block == True:
                # ブロックされたユーザーの場合、メッセージを送信しない
                return send_text_message(line_id, "ブロックされています")

            if 'プロフィール変更' in event.message.text:
                # プロフィール変更を促す
                return send_menu_message(line_id)

            if customer.password != 'R105':
                # プロフィール変更を促す
                return send_menu_message(line_id)

            # 情報やブロック要素に問題がなければマニュアル情報を提供する
            # 情報を保存
            chat_manual_res = open_ai_chat(event.message.text)
            QuestionMessage.objects.create(customer=customer, message=event.message.text, response=chat_manual_res)
            return send_text_message(line_id, chat_manual_res)

        except Exception as e:
            print(e)

    # ポストバック
    @handler.add(PostbackEvent)
    def on_postback(event):
        pass

# テキストメッセージ送信
def send_text_message(line_id, message):
    liff_json = {"type": "text", "text": message}
    result = TextMessage.new_from_json_dict(liff_json)
    try:
        line_bot_api.push_message(line_id, messages=result)
    except Exception:
        print("テキストメッセージを送信できませんでした")


@method_decorator(csrf_exempt, name="dispatch")
class IndexView(View):
    def get(self, request):
        line_id = request.GET.get("line_id")

        if not line_id:
            # liff.state から line_id を取得
            liff_state = request.GET.get("liff.state")
            if liff_state and "line_id=" in liff_state:
                line_id = liff_state.split("line_id=")[-1]
                print("line_id: ", line_id)

        customer = Customer.objects.get(line_id=line_id)
        form = CustomerForm(instance=customer)
        return render(request, "line/info_form.html", {"form": form, "liff_id": settings.LIFF_ID,})

    def post(self, request):

        line_id = request.GET.get("line_id")

        if not line_id:
            # liff.state から line_id を取得
            liff_state = request.GET.get("liff.state")
            if liff_state and "line_id=" in liff_state:
                line_id = liff_state.split("line_id=")[-1]
                print("line_id: ", line_id)


        customer = Customer.objects.get(line_id=line_id)
        form = CustomerForm(request.POST, instance=customer)

        if form.is_valid():
            form.save()
            # line_id を引き継ぐ
            confirm_url = reverse("line:confirm") + f"?line_id={line_id}"

            return redirect(confirm_url)

        return render(request, "line/info_form.html", {"form": form})


# 予約内容確認
@method_decorator(csrf_exempt, name="dispatch")
class ConfirmView(View):
    def get(self, request):

        line_id = request.GET.get("line_id")

        if not line_id:
            # liff.state から line_id を取得
            liff_state = request.GET.get("liff.state")
            if liff_state and "line_id=" in liff_state:
                line_id = liff_state.split("line_id=")[-1]
                print("line_id: ", line_id)

        customer = Customer.objects.get(line_id=line_id)

        return render(
            request,
            "line/info_confirm.html",
            {"customer": customer},
        )

    def post(self, request):
        line_id = request.GET.get("line_id")
        customer = Customer.objects.get(line_id=line_id)

        if customer is None:
            send_text_message(line_id, "存在しないユーザーです。")
        else:
            send_text_message(line_id, "ユーザー情報を更新しました。")
        return redirect("line:done")


class DoneView(View):
    def get(self, request):
        return render(request, "line/done.html")
