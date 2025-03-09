from django.db import models


class Customer(models.Model):
    name = models.CharField(max_length=255, verbose_name="名前")
    line_id = models.CharField(max_length=255, unique=True, verbose_name="LINE ID")
    password = models.CharField(max_length=255, verbose_name="認証パスワード")
    block = models.BooleanField(default=False, verbose_name="ブロック")

    updated_at = models.DateTimeField("更新日", auto_now=True)
    created_at = models.DateTimeField("作成日", auto_now_add=True)

    class Meta:
        verbose_name = "顧客"
        verbose_name_plural = "顧客"

    def __str__(self):
        return self.name


class QuestionMessage(models.Model):
    # マニュアルへの問い合わせを保存
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE, verbose_name="顧客")
    message = models.TextField(verbose_name="メッセージ")
    response = models.TextField(verbose_name="返信")
    updated_at = models.DateTimeField("更新日", auto_now=True)
    created_at = models.DateTimeField("作成日", auto_now_add=True)

    class Meta:
        verbose_name = "問い合わせ"
        verbose_name_plural = "問い合わせ"

    def __str__(self):
        return self.message