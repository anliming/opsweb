# _*_ coding: utf-8 _*_
import gitlab

from opsweb.settings import GITLAB_HTTP_URI, GITLAB_TOKEN
gl = gitlab.Gitlab(GITLAB_HTTP_URI, GITLAB_TOKEN)


def get_user_projects(request):
    """
    获取gitlab里所有的项目，和登录用户所拥有的项目,以及登录用户所拥有项目的项目成员
    :return: []
    """
    user_projects = []
    all_projects = gl.projects.list()

    # 查出所有项目中包含登录用户的项目,即查出当前用户所有的项目
    for project in all_projects:
        for member in project.members.list():
            if member.username == request.user.username:
                user_projects.append(project)
    # 查询用户所有组即组中所有的项目
    user_groups = request.user.groups.all()
    gitlab_user_groups = []
    for group in user_groups:
       gitlab_user_groups.extend(gl.groups.search(group.name))

    group_projects = []
    for group in gitlab_user_groups:
        group_projects.extend(group.projects.list())

    # 将两者去重
    for user_project in user_projects:
       for group_project in group_projects:
           if user_project.name == group_project.name:
               user_projects.remove(user_project)

    user_projects.extend(group_projects)

    # return all_projects, user_projects
    return user_projects


def get_project_versions(project_id):
    versions = gl.project_tags.list(project_id=project_id)
    return versions

