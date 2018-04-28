# encoding: utf-8
import json
import datetime
import ansible.runner
import ansible.playbook
import ansible.inventory
from ansible import callbacks
from ansible import utils

class AllStats(callbacks.AggregateStats):
    def __init__(self):
        self.results = {}
        super(AllStats, self).__init__()

    def compute(self, runner_results, setup=False, poll=False, ignore_errors=False):
        super(AllStats, self).compute(runner_results, setup=False, poll=False, ignore_errors=False)
        for host, value in runner_results.get('contacted', {}).iteritems():
            executed = value.pop("invocation", None)
            host_details = self.results.setdefault(host, {})
            task_done = host_details.setdefault('details', [])
            task_done.append({"executed": executed, "log": value,
                              "@timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

        for host, value in runner_results.get('dark', {}).iteritems():
            host_details = self.results.setdefault(host, {})
            task_done = host_details.setdefault('details', [])
            task_done.append({"executed": None, "log": value,
                              "@timestamp": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")})

    def summarize(self, host):
        summary = super(AllStats, self).summarize(host)
        summary.update(self.results.get(host, {}))
        return summary


class AnsiblePlaybookAPI(object):
    """1.9.x 上通过测试 """
    def __init__(self, playbook, extra_vars={}):   # 初始化参数
        self.stats = AllStats()
        self.playbook_cb = callbacks.PlaybookCallbacks(verbose=utils.VERBOSITY)
        self.runner_cb = callbacks.PlaybookRunnerCallbacks(self.stats, verbose=2)
        self.extra_vars = extra_vars
        self.playbook = playbook
        self.setbook = self.book_set()

    def book_set(self):
        self.pb = ansible.playbook.PlayBook(
            playbook=self.playbook,
            stats =self.stats,
            extra_vars=self.extra_vars,
            callbacks=self.playbook_cb,
            runner_callbacks=self.runner_cb
        )

    def run(self):
        """
        playbook执行
        """
        results = self.pb.run()
        simple = {}
        detail = {}
        for host, summary in results.iteritems():
            detail[host] = summary.pop('details', {})
            simple[host] = summary
        return {'simple': simple, 'detail': json.dumps(detail, indent=4)}
