# encoding: utf-8
import ansible.runner
import ansible.playbook
import ansible.inventory
from ansible import callbacks
from ansible import utils


class AnsiblePlaybookAPI(object):
    """1.9.x 上通过测试 """
    def __init__(self, playbook, extra_vars={}):   # 初始化参数
        self.stats = callbacks.AggregateStats()
        self.playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        self.extra_vars = extra_vars
        self.playbook = playbook
        self.setbook = self.book_set()

    def book_set(self):
        #runner_cb = callbacks.PlaybookRunnerCallbacks(self.stats, verbose=utils.VERBOSITY)
        runner_cb = callbacks.PlaybookRunnerCallbacks(self.stats, verbose=2)
        self.pb = ansible.playbook.PlayBook(
            playbook=self.playbook,
<<<<<<< HEAD
            stats=self.stats,
=======
            stats =self.stats,
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
            extra_vars=self.extra_vars,
            callbacks=self.playbook_cb,
            runner_callbacks=runner_cb
        )

    def run(self):
        """
        playbook执行
        """

        simple = self.pb.run()
        # 将最新的一条playbook执行详细结果存入临时文件，然后数据库
<<<<<<< HEAD
        with open('/tmp/ansible/ansible.log.tmp', 'r') as f:
            detail = f.read()

        # 入库之后将临时文件清空
        with open('/tmp/ansible/ansible.log.tmp', 'w') as f:
            pass
        # 将任务执行的状态和详细信息入库
        return {'simple': simple, 'detail': detail}
=======
        with open('/var/log/ansible/ansible.log.tmp', 'r') as f:
            detail = f.read()

        # 入库之后将临时文件清空
        with open('/var/log/ansible/ansible.log.tmp', 'w') as f:
            pass
        # 将任务执行的状态和详细信息入库
        return {'simple': simple, 'detail': detail}
>>>>>>> 0806a45f79e0ae7f8f862b7984b0ba58c1c14aa5
