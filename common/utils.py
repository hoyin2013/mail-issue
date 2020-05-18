#!/usr/bin/env python3
# -*- coding: utf-8 -*-
# Created by Hoyin on 2020/1/7
#

import datetime
import time
from datetime import timedelta


class TimeUtils:
    def __init__(self):
        self.now = datetime.date.today()

    def get_today(self):
        # 今天
        return self.now

    def get_yesterday(self):
        # 昨天
        return self.now - timedelta(days=1)

    def get_tomorrow(self):
        # 明天
        return self.now + timedelta(days=1)

    def get_now_quarter(self):
        # 当前季度
        return self.now.month / 3 if self.now.month % 3 == 0 else self.now.month / 3 + 1

    def get_this_week_start(self):
        # 本周第一天
        return self.now - timedelta(days=self.now.weekday())

    def get_this_week_end(self):
        # 本周最后一天
        return self.now + timedelta(days=6-self.now.weekday())

    def get_last_week_start(self):
        # 上周第一天
        return self.now - timedelta(days=self.now.weekday()+7)

    def get_last_week_end(self):
        # 上周最后一天
        return self.now - timedelta(days=self.now.weekday()+1)

    def get_this_month_start(self):
        # 本月第一天
        return datetime.datetime(self.now.year, self.now.month, 1)

    def get_this_month_end(self):
        # 本月最后一天
        return datetime.datetime(self.now.year, self.now.month + 1, 1) - timedelta(days=1)

    def get_last_month_end(self):
        # 上月第一天
        return self.get_this_month_start() - timedelta(days=1)

    def get_last_month_start(self):
        # 上月最后一天
        return datetime.datetime(self.get_last_month_end().year, self.get_last_month_end().month, 1)

    def get_this_quarter_start(self):
        # 本季第一天
        month = (self.now.month - 1) - (self.now.month - 1) % 3 + 1
        this_quarter_start = datetime.datetime(self.now.year, month, 1)
        return this_quarter_start

    def get_this_quarter_end(self):
        # 本季最后一天
        month = (self.now.month - 1) - (self.now.month - 1) % 3 + 1
        this_quarter_end = datetime.datetime(self.now.year, month + 3, 1) - timedelta(days=1)
        return this_quarter_end

    def get_last_quarter_start(self):
        # 上季第一天
        last_quarter_start = datetime.datetime(self.get_last_quarter_end().year, self.get_last_quarter_end().month - 2, 1)
        return last_quarter_start

    def get_last_quarter_end(self):
        # 上季最后一天
        last_quarter_end = self.get_this_quarter_start() - timedelta(days=1)
        return last_quarter_end

    def get_this_year_start(self):
        # 本年第一天
        this_year_start = datetime.datetime(self.now.year, 1, 1)
        return this_year_start

    def get_this_year_end(self):
        # 本年最后一天
        this_year_end = datetime.datetime(self.now.year + 1, 1, 1) - timedelta(days=1)
        return this_year_end

    def get_last_year_end(self):
        # 去年最后一天
        last_year_end = self.get_this_year_start() - timedelta(days=1)
        return last_year_end

    def get_last_year_start(self):
        # 去年第一天
        last_year_start = datetime.datetime(self.get_last_year_end().year, 1, 1)
        return last_year_start


if __name__ == '__main__':
    print(TimeUtils().get_yesterday())

