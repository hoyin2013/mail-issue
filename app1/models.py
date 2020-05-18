# coding:utf-8
from django.db import models
import uuid


class Emails(models.Model):
    msg_id = models.CharField('邮件ID', max_length=100)
    subjects = models.CharField('邮件标题', max_length=250, null=True, blank=True)
    sender = models.EmailField('发送方', null=True, blank=True)
    receiver = models.CharField('接收方', max_length=500, null=True, blank=True)
    send_date = models.DateTimeField('发送时间', null=True, blank=True)
    cc = models.CharField('抄送', max_length=500, null=True, blank=True)
    status = models.CharField('状态', max_length=50, null=True, blank=True)
    result = models.CharField('结果', max_length=50, null=True, blank=True)
    is_execute = models.NullBooleanField('是否处理', null=True, blank=True)
    operator = models.CharField('执行人', max_length=20, null=True, blank=True)
    execute_time = models.DateTimeField('处理时间', null=True, blank=True)
    update_time = models.DateTimeField('修改时间', null=True, blank=True)
    attaches = models.CharField('附件', max_length=500, null=True, blank=True)
    comment = models.TextField('备注', max_length=500, null=True, blank=True)

    class Meta:
        verbose_name = '邮件列表'
        verbose_name_plural = verbose_name

    def __str__(self):
        return self.msg_id

