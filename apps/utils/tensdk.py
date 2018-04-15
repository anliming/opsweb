# -*- coding: utf-8 -*-

'''
签名方法
https://www.qcloud.com/document/api/377/4214
'''

import json

from QcloudApi.qcloudapi import QcloudApi


class TenHandler(object):
    def __init__(self, region, secretId, secretKey, module):
        self.config = {'Region': region, 'secretId': secretId, 'secretKey': secretKey, 'method': 'get',
                       'Version': '2017-03-20'}
        self.module = module
        self.conn = None
        self.conn_image = None

    def connect(self):
        if self.conn or self.conn_image:
            return
        self.conn = QcloudApi(self.module, self.config)
        self.conn_image = QcloudApi("image", self.config)

    def get_regions(self):
        self.connect()

        params = {}
        region_unicode = self.conn.call('DescribeRegions', params)
        region_obj = json.loads(region_unicode)
        if region_obj['code'] == 0:
            return region_obj['regionSet'], True
        return None, False

    def get_instances(self, page, pagesize=100):
        self.connect()

        limit = pagesize
        offset = (page - 1) * limit

        response = self.conn.call('DescribeInstances', {'Offset': offset, 'Limit': limit})
        response = json.loads(response)
        response = response['Response']
        instance_set = []
        if 'InstanceSet' in response and response['InstanceSet']:
            instance_set = self._processInstanceResult(response['InstanceSet'])
        else:
            return instance_set, False, False
        return instance_set, True, response['TotalCount'] >= limit

    def get_instance(self, instance_id):
        self.connect()

        params = {'instanceIds.n': str(instance_id)}
        instances = self.conn.call('DescribeInstances', params)
        instances_obj = json.loads(instances)
        if instances_obj['code'] != 0:
            return None, False
        return self._processInstanceResult(instances_obj), True

    def get_hostinfo_from_hostname(self, hostname):
        params = {'instanceIds.n': str(hostname)}
        instances = self.conn.call('DescribeInstances', params)
        instances_obj = json.loads(instances)
        if instances_obj['code'] != 0:
            return None, False
        return self._processInstanceResult(instances_obj), True

    def _processInstanceResult(self, instances):
        ret = []
        for instance in instances:

            instance_status = self.get_instance_status(instance['InstanceId'])

            disks = []
            disk = instance['SystemDisk']
            temp = {
                'disk_id': disk['DiskId'],
                'device': '',
                'size': disk['DiskSize'],
                'type': 'system',
                'creation_time': instance['CreatedTime'].replace('T', ' ').rstrip('Z'),
                'expired_time': instance['ExpiredTime'].replace('T', ' ').rstrip('Z'),
            }
            disks.append(temp)

            for disk in instance['DataDisks']:
                temp = {
                    'disk_id': disk['DiskId'],
                    'device': '',
                    'size': disk['DiskSize'],
                    'type': 'data',
                    'creation_time': instance['CreatedTime'].replace('T', ' ').rstrip('Z'),
                    'expired_time': instance['ExpiredTime'].replace('T', ' ').rstrip('Z'),
                }
                disks.append(temp)
            temp = {
                'image_id': instance['ImageId'],
                'instance_id': instance['InstanceId'],
                'instance_name': instance['InstanceName'],
                'instance_type': instance['InstanceType'],
                'description': '',
                'hostname': instance['InstanceName'],
                'status': instance_status,
                'public_ip': instance['PublicIpAddresses'] if not instance['PublicIpAddresses'] else ','.join(
                    instance['PublicIpAddresses']),
                'private_ip': instance['PrivateIpAddresses'] if not instance['PrivateIpAddresses'] else ','.join(
                    instance['PrivateIpAddresses']),
                'creation_time': instance['CreatedTime'].replace('T', ' ').rstrip('Z'),
                'expired_time': instance['ExpiredTime'].replace('T', ' ').rstrip('Z'),
                'cpu': instance['CPU'],
                'memory': instance['Memory'],
                'os_name': instance['OsName'],
                'os_type': 'windows' if instance['OsName'][:7] == 'Windows' else 'linux',
                'region_id': '-'.join(instance['Placement']['Zone'].split('-')[:2]),
                'zone_id': instance['Placement']['Zone'],
                'disks': disks
            }
            ret.append(temp)
        return ret

    def get_instance_status(self, instance_id):
        self.connect()
        response = self.conn.call('DescribeInstancesStatus', {'InstanceIds.1': instance_id, 'Offset': 0, 'Limit': 1})
        instances_status = json.loads(response)
        if 'InstanceStatusSet' in instances_status['Response'] and instances_status['Response']['InstanceStatusSet']:
            return instances_status['Response']['InstanceStatusSet'][0]['InstanceState']
        else:
            return None

    def _fmt_device(self, device_info):
        return {'device_name': '', 'device_type': device_info['rootType'], 'device_size': device_info['rootSize']}

    def _fmt_disksinfo(self, systemdisk, datadisks=None):
        ret = []
        if systemdisk and isinstance(systemdisk, dict):
            temp = {'device_name': 'system disk', 'device_type': systemdisk['DiskType'],
                    'device_size': systemdisk['DiskSize']}
            ret.append(temp)

        if datadisks and isinstance(systemdisk, list):
            temp = [{'device_name': 'data disk', 'device_type': x['DiskType'], 'device_size': x['DiskSize']} for x in
                    datadisks if x]
            ret.extend(temp)

        return ret


    def get_describe_images(self, image_id):
        self.connect()

        params = {'ImageIds.1': image_id, 'Offset': 0, 'Limit': 1}
        response = self.conn_image.call('DescribeImages', params)
        images = json.loads(response)
        if 'ImageSet' in images['Response'] and images['Response']['ImageSet']:
            return images['Response']['ImageSet'][0]
        else:
            return None

    def modify_instanceName(self, instance_id, instance_name):
        self.connect()

        params = {'InstanceIds.1': instance_id, 'InstanceName': instance_name, 'Version': '2017-03-12'}
        try:
            instances = self.conn.call('ModifyInstancesAttribute', params)
        except Exception as e:
            return e.args, False
        else:
            return json.loads(instances), True


if __name__ == '__main__':
    handler = TenHandler('', '', '', "")
