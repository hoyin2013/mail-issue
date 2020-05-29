#!/usr/bin/env python
# -*- coding: utf-8 -*-
# Created by Hoyin on 2020/1/7
#

import email
import datetime
import hashlib
import time
import re
import os
import sys
import sqlite3
import logging
import imaplib
from config import CONFIG

imaplib._MAXLINE = 1000000

logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)

filepath, tmpfilename = os.path.split(__file__)
shotname, extension = os.path.splitext(tmpfilename)

rq = time.strftime('%Y%m%d%H%M', time.localtime(time.time()))[:-4]

log_path = os.path.join(filepath, 'logs')
if not os.path.exists(log_path): os.mkdir(log_path)

logfile = log_path + '/' + shotname + '_' + rq + '.log'
fh = logging.FileHandler(logfile, mode='a')
fh.setLevel(logging.DEBUG)  # 输出到file的log等级的开关

formatter = logging.Formatter("%(asctime)s - %(filename)s[line:%(lineno)d] - %(levelname)s: %(message)s")
fh.setFormatter(formatter)
logger.addHandler(fh)


def decode_str(s):
    """解码邮件标题"""
    value, charset = email.header.decode_header(s)[0]
    if charset:
        try:
            value = value.decode(charset)
        except Exception as e:
            logger.error('编码错误:%s' % e)
            return '编码错误'

    return value


def create_dir(dir_path):
    """
    如果文件夹不存在，则创建文件夹
    :param dir_path: 日期字符串：2019-12-09
    :return: True or False or None
    """
    if os.path.exists(dir_path):
        # print("文件夹已存在")
        return None
    else:
        try:
            os.mkdir(dir_path)
            # print("创建文件夹%s成功" % dir_path)
            return True
        except Exception as e:
            logger.error("创建文件夹失败:%s" % e)
            print("创建文件夹失败")
            return False


class Imapmail(object):

    def __init__(self):  # 初始化数据
        self.serveraddress = None
        self.user = None
        self.passwd = None
        self.prot = None
        self.ssl = None
        self.timeout = None
        self.savepath = None
        self.server = None
        self.sqlite = 'db.sqlite3'

    def _parse_message_header(self, msg):
        send_email_to = send_email_cc = []

        for header in ['From', 'To', 'Cc', 'Subject', 'Date']:
            value = msg.get(header, '')
            if value:
                if header == 'Subject':
                    _subjects = self._str_filter(decode_str(value))
                elif header == 'Date':
                    email_date = email.utils.parsedate(msg.get("Date"))
                else:
                    # print(value)
                    if isinstance(value, email.header.Header):
                        continue
                    else:
                        value01 = value.split(', ')

                    for item in value01:
                        _, emailAdr = email.utils.parseaddr(item)
                        if header == 'From':
                            send_email_from = emailAdr
                        elif header == 'To':
                            send_email_to.append(emailAdr)
                        elif header == 'Cc':
                            send_email_cc.append(emailAdr)

        try:
            # 生成邮件ID
            msg_id = hashlib.md5((send_email_from + str(email_date)).encode("utf-8")).hexdigest()
        except UnboundLocalError:
            msg_id = 0

        try:
            
            email_header = {
                'send_email_from': send_email_from,
                'send_email_to': send_email_to,
                'send_email_cc': send_email_cc,
                'subjects': _subjects,
                'email_date': email_date,
                'msg_id': msg_id,
                'attaches': ''
            }
        except UnboundLocalError:
            email_header = {
                'send_email_from': "UnboundLocalError",
                'send_email_to': send_email_to,
                'send_email_cc': send_email_cc,
                'subjects': "UnboundLocalError",
                'email_date': email_date,
                'msg_id': msg_id,
                'attaches': ''
            }

        return email_header

    def _str_filter(self, _str):
        """
        :param _str: 处理邮件标题中的"回复"
        :return: 处理完的邮件标题
        """
        _str = _str.strip()

        if not re.findall('^Fw|^Re|^回复|^转发', _str):
            return _str
        else:
            _str = _str[3:]
            return self._str_filter(_str)

    @staticmethod
    def _get_attatches(msg_in, attach_path):
        """
        msg_in:messages
        """
        # 解析邮件附件
        attachment_files = []
        for part in msg_in.walk():
            # 获取附件名称类型
            file_name = part.get_filename()
            # contType = part.get_content_type()
            if file_name:
                h = email.header.Header(file_name)
                # 对附件名称进行解码
                dh = email.header.decode_header(h)
                filename = dh[0][0]
                if dh[0][1]:
                    # 将附件名称可读化
                    filename = decode_str(str(filename, dh[0][1]))
                    # print(filename)
                    # filename = filename.encode("utf-8")
                # 下载附件
                data = part.get_payload(decode=True)

                # 只下载后缀为".txt" 和 ".sql"的附件
                if filename.endswith('.txt') or filename.endswith('.sql') or filename.endswith(
                        '.zip') or filename.endswith('.rar'):
                    try:
                        # 在指定目录下创建文件，注意二进制文件需要用wb模式打开
                        att_file = open(attach_path + '/' + filename, 'wb')
                        attachment_files.append(filename)
                        att_file.write(data)  # 保存附件
                        att_file.close()
                    except Exception as e:
                        logger.error("保存附件失败！:%s" % e)

        return attachment_files

    def client(self):
        """
        登陆
        """
        try:
            self.server = imaplib.IMAP4(self.serveraddress)
            self.server.login(self.user, self.passwd)
            return self.server
        except BaseException as e:
            logger.error(str(e))
            return "ERROR: >>> " + str(e)

    def logout(self):
        """
        退出
        """
        self.server.close()
        self.server.logout()
        logger.info('退出成功！')

    def getmaildir(self):
        """# 获取目录列表 [((), b'/', 'INBOX'), ((b'\\Drafts',), b'/', '草稿箱'),]"""
        dirlist = self.server.list()
        return dirlist

    def getallmail(self, mbox_name="INBOX", search="ALL"):
        """ 返回邮件id
        search=
        """
        # print(self.server)
        typ, data = self.server.select('"{}"'.format(mbox_name), readonly=True)

        status, ids = self.server.search(None, search)

        # ids = ids[0].split(b' ')
        ids = ids[0].split()
        # print(ids)
        return ids

    def get_mail_info(self, _mid):
        status, data = self.server.fetch(_mid, "(RFC822)")
        data_body = data[0][1]

        messages = email.message_from_bytes(data_body)
        # print(messages)
        _mailinfo = self._parse_message_header(messages)

        # 创建邮件附件存储文件夹
        str_date = time.strftime('%Y-%m-%d', _mailinfo['email_date'])
        attach_path = self.savepath + '/' + str_date
        create_dir(attach_path)

        # 保存附件
        attach = self._get_attatches(messages, attach_path)

        if attach:
            attach = ['[' + str_date + ']' + x for x in attach]
            att_list = ','.join(attach)
            logger.info("成功保存附件：%s" % att_list)
        else:
            att_list = ''

        _mailinfo['attaches'] = att_list

        return _mailinfo

    def save_sqlite(self, m):
        try:
            # 连接sqlite3数据库
            conn = sqlite3.connect(self.sqlite)
            cursor = conn.cursor()
        except Exception as e:

            logger.error("连接sqlite失败！:%s" % e)
            sys.exit()

        # 检查邮件是否已经收取
        cursor.execute("select msg_id from app1_emails where msg_id=?", (m['msg_id'],))
        if cursor.fetchall():
            print("邮件%s已收取!" % m['msg_id'])
            logger.info("邮件%s已收取!" % m['msg_id'])
        else:
            try:
                # 保存到数据库
                msg_id = m['msg_id']
                email_date = time.strftime("%Y-%m-%d %H:%M:%S", m['email_date'])
                send_email_from = m['send_email_from']

                send_email_to = send_email_cc = ''

                if len(m['send_email_to']) < 1:
                    send_email_to = ''
                elif len(m['send_email_to']) == 1:
                    send_email_to = m['send_email_to'][0]
                elif len(m['send_email_to']) > 1:
                    send_email_to = ';'.join(m['send_email_to'])

                if len(m['send_email_cc']) < 1:
                    send_email_cc = ''
                elif len(m['send_email_cc']) == 1:
                    send_email_cc = m['send_email_cc'][0]
                elif len(m['send_email_cc']) > 1:
                    send_email_cc = ';'.join(m['send_email_cc'])

                subjects = m['subjects']
                attaches = m['attaches']

                if send_email_from != 'ops_notice@nucc.com' and send_email_from != 'operation@xdjk.com':
                    isql = "insert into app1_emails(msg_id,sender,receiver,send_date,subjects,attaches) " \
                           "values ('{}','{}','{}','{}','{}','{}')" \
                        .format(msg_id, send_email_from, send_email_to, email_date, subjects, attaches)
                    print(isql)
                    logger.info(isql)
                    cursor.execute(isql)
                    logger.info("插入{}行".format(cursor.rowcount))
                    conn.commit()


                    # 自动更新执行状态
                    update_status_3 = "update app1_emails set status='已审批' " \
                                  "where subjects in (select subjects from app1_emails " \
                                  "where sender='wangjd@mfhcd.com') and status is null and is_execute is null and attaches<>''"

                    logger.info(update_status_3)
                    cursor.execute(update_status_3)
                    logger.info("插入{}行".format(cursor.rowcount))
                    conn.commit()


  
                    # 自动更新执行状态
                    update_status_1 = "update app1_emails set is_execute=1,operator='尹红斌',execute_time=datetime('now') " \
                                      "where subjects in (select subjects from app1_emails " \
                                      "where sender='yinhb@mfhcd.com') and is_execute is null and attaches<>''"

                    logger.info(update_status_1)
                    cursor.execute(update_status_1)
                    logger.info("插入{}行".format(cursor.rowcount))
                    conn.commit()

                    update_status_2 = "update app1_emails set is_execute=1,operator='刘韬',execute_time=datetime('now')" \
                                      "where subjects in (select subjects from app1_emails " \
                                      "where sender='liutao-yunwei@mfhcd.com') " \
                                      "and is_execute is null and attaches<>''"

                    logger.info(update_status_2)
                    cursor.execute(update_status_2)
                    logger.info("插入{}行".format(cursor.rowcount))
                    conn.commit()


            except Exception as e:
                print(e)


if __name__ == "__main__":

    imap = Imapmail()

    imap.serveraddress = CONFIG["serveraddress"]
    imap.user = CONFIG["user"]
    imap.passwd = CONFIG["passwd"]
    imap.savepath = CONFIG["savepath"]
    imap.sqlite = CONFIG["sqlite"]
    imap.client()

    #print(imap.getmaildir())  # 获取邮箱列表

    def download(num, box):
        # 获取几封邮件

        i = 0
        for mid in reversed(box):
            print(mid)
            mailinfo = imap.get_mail_info(mid)
            # print(mailinfo)

            # 保存到sqlite
            imap.save_sqlite(mailinfo)
            i += 1
            if i >num:
                break


    # 一次收取数量
    recv_num = CONFIG["email_num"]

    # 收件箱
    inbox_ids = imap.getallmail()
    download(recv_num, inbox_ids)

    # 发件箱
    send_ids = imap.getallmail(mbox_name="Sent Messages", search="ALL")
    #download(len(send_ids), send_ids)
    download(recv_num, send_ids)


    # 退出
    imap.logout()
