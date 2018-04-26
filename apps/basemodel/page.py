# coding=utf-8
from django.core.paginator import Paginator
from django.core.paginator import PageNotAnInteger
from django.core.paginator import EmptyPage

class JuncheePaginator(Paginator):
    def __init__(self, object_list, per_page=10, range_num=4, orphans=0, allow_empty_first_page=True):
        Paginator.__init__(self, object_list, per_page, orphans, allow_empty_first_page)
        self.range_num = range_num

    def page(self, number):
        self.page_num = int(number)
        return super(JuncheePaginator, self).page(number)

    def _page_range_ext(self):
        num_count = 2 * self.range_num + 1  # 底部显示的页码数
        if self.num_pages <= num_count:
            return range(1, self.num_pages + 1)
        num_list = []
        num_list.append(self.page_num)
        for i in range(1, self.range_num + 1):
            if self.page_num - i <= 0:
                num_list.append(num_count + self.page_num - i)
            else:
                num_list.append(self.page_num - i)

            if self.page_num + i <= self.num_pages:
                num_list.append(self.page_num + i)
            else:
                num_list.append(self.page_num + i - num_count)
            num_list.sort()
        return num_list

    page_range_ext = property(_page_range_ext)

    def pagecomputer(self, page_num):
        try:
            pagedata = self.page(page_num)
        except PageNotAnInteger:
            pagedata = self.page(1)
        except EmptyPage:
            pagedata = self.page(self.num_pages)
        return pagedata, self.num_pages

