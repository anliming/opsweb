# _*_ coding: utf-8 _*_
from django.contrib.auth.models import Group, Permission, ContentType
from dashboard.models import UserProfile


def global_variable(request):
    all_content_type = ContentType.objects.all()
    all_group = Group.objects.all()
    all_perm = Permission.objects.all()
    user_total_nums = UserProfile.objects.all().count()
    user_active_nums = UserProfile.objects.filter(is_active=True).count()

    dic = {
        'all_group': all_group,
        'all_perm': all_perm,
        'all_content_type': all_content_type,
        'group_total_nums': len(all_group),
        'user_total_nums': user_total_nums,
        'user_active_nums': user_active_nums
    }

    return dic
