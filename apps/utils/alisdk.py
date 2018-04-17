# encoding: utf-8

import json
from aliyunsdkcore.client import AcsClient
from aliyunsdkecs.request.v20140526 import DescribeInstancesRequest
from aliyunsdkecs.request.v20140526 import DescribeRegionsRequest
from aliyunsdkecs.request.v20140526 import ModifyInstanceAttributeRequest
from aliyunsdkecs.request.v20140526 import DescribeDisksRequest
from aliyunsdkecs.request.v20140526 import DescribeImagesRequest


class ECSHandler(object):

    def __init__(self, access_key_id, secret_access_key, region_id="cn-shanghai"):
        self.access_key_id = access_key_id
        self.secret_access_key = secret_access_key
        self.region_id = region_id
        self.clt = None
        self.amiMap = {}

    def connect(self):
        if self.clt:
            return
        self.clt = AcsClient(self.access_key_id, self.secret_access_key, self.region_id)

    # 获取区域信息
    def get_region_ids(self):
        self.connect()

        request = DescribeRegionsRequest.DescribeRegionsRequest()
        request.set_accept_format("json")
        try:
            response_string = self.clt.do_action_with_exception(request)
        except Exception as e:
            return e.args, False
        else:
            response_obj = json.loads(response_string)
            return response_obj['Regions']['Region'], True

    # 获取某个实例信息
    def get_instance(self, instance_id):
        self.connect()

        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format("json")
        request.set_PageSize(100)
        request.set_InstanceIds(InstanceIds=[str(instance_id)])
        try:
            response_string = self.clt.do_action_with_exception(request)
        except Exception as e:
            return e.args, False
        else:
            response_obj = json.loads(response_string)
            data = response_obj['Instances']['Instance']
            if data:
                return self._processInstanceResult(data[0]), True

            else:
                return None, False

    # 获取hostname
    def get_host_info_from_hostname(self, hostname):
        self.connect()

        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format("json")
        request.set_PageSize(100)
        request.set_InstanceName(InstanceName=hostname)
        try:
            response_string = self.clt.do_action_with_exception(request)
        except Exception as e:
            return e.args, False
        else:
            response_obj = json.loads(response_string)
            data = response_obj['Instances']['Instance']
            if data:
                return self._processInstanceResult(data[0]), True
            else:
                return None, False

    def get_instances(self, num=1):
        self.connect()

        request = DescribeInstancesRequest.DescribeInstancesRequest()
        request.set_accept_format("json")
        request.set_PageSize(100)
        request.set_PageNumber(num)
        try:
            response_string = self.clt.do_action_with_exception(request)
        except Exception as e:
            return e.args, False, True
        else:
            response_obj = json.loads(response_string)
            retdata = []
            instances = response_obj['Instances']['Instance']
            for instance_obj in instances:
                tmp = self._processInstanceResult(instance_obj)
                retdata.append(tmp)
            return retdata, True, len(instances) >= 100

    # 获取实例的具体信息
    def _processInstanceResult(self, instance):

        if instance['InstanceNetworkType'] == 'vpc':
            public_ip = instance['EipAddress']['IpAddress']
            private_ip = ",".join(instance['VpcAttributes']['PrivateIpAddress']['IpAddress'])

        elif instance['InstanceNetworkType'] == 'classic':
            public_ip = ','.join(instance['PublicIpAddress']['IpAddress'])
            private_ip = ",".join(instance['InnerIpAddress']['IpAddress'])

        else:
            public_ip, private_ip = None, None

        instance_id = instance['InstanceId']
        diskinfo = self.get_diskinfo(instance_id)

        image_id = instance['ImageId']
        _ami_map = self.get_amis(image_id)
        image_name = _ami_map.get(image_id, '')
        return {
            'image_id': image_id,
            'instance_id': instance_id,
            'instance_name': instance['InstanceName'],
            'instance_type': instance['InstanceType'],
            "instance_charge_type": instance['InstanceChargeType'],
            'description': instance['Description'],
            'hostname': instance['HostName'],
            'status': instance['Status'],
            'public_ip': public_ip,
            'private_ip': private_ip,
            'creation_time': instance['CreationTime'].replace('T', ' ').rstrip('Z'),
            'expired_time': instance['ExpiredTime'].replace('T', ' ').rstrip('Z'),
            'os_type': instance['OSType'],
            'os_name': instance['OSName'],
            "memory": instance['Memory'] / 1024,
            "cpu": instance['Cpu'],
            'region_id': instance['RegionId'],
            'zone_id': instance['ZoneId'],
            'disks': diskinfo,
        }

    def modify_instance_name(self, instance_id, instance_name):
        self.connect()

        try:
            request = ModifyInstanceAttributeRequest.ModifyInstanceAttributeRequest()
            request.set_InstanceId(InstanceId=instance_id)
            request.set_InstanceName(InstanceName=instance_name)
            response = self.clt.do_action_with_exception(request)

        except Exception as e:
            return e.args, False
        else:
            return response, True

    def get_disksinfo(self):
        self.connect()

        retdisks = []
        for num in range(1, 4):
            request = DescribeDisksRequest.DescribeDisksRequest()
            request.set_accept_format("json")
            request.set_PageSize(100)
            request.set_PageNumber(num)
            response_string = self.clt.do_action_with_exception(request)

            response = json.loads(response_string)
            diskinfos = response['Disks']['Disk']
            if len(diskinfos) == 0:
                break
            retdisks.extend(diskinfos)


        ret = {}
        for x in retdisks:
            instance_id = x['InstanceId']
            device_size = x['Size']
            device_name = x['Device']
            tmp = {'device_size': device_size, 'device_name': device_name, 'device_type': ''}
            if instance_id in ret:
                ret[instance_id].append(tmp)
                ret[instance_id] = ret[instance_id]
            else:
                ret[instance_id] = [tmp]
        return ret

    def get_diskinfo(self, instance_id):
        request = DescribeDisksRequest.DescribeDisksRequest()
        request.set_accept_format("json")
        request.set_InstanceId(InstanceId=instance_id)
        response_string = self.clt.do_action_with_exception(request)
        response = json.loads(response_string)
        disks = []
        for disk in response['Disks']['Disk']:
            temp = {
                'disk_id': disk['DiskId'],
                'device': disk['Device'],
                'size': disk['Size'],
                'type': disk['Type'],
                'creation_time': disk['CreationTime'].replace('T', ' ').rstrip('Z'),
                'expired_time': disk['ExpiredTime'].replace('T', ' ').rstrip('Z')
            }
            disks.append(temp)
        return disks

    def get_amis(self, ami_id=None):
        self.connect()

        request = DescribeImagesRequest.DescribeImagesRequest()
        request.set_accept_format("json")
        request.set_PageSize(100)
        if ami_id:
            request.set_ImageId(ami_id)
        request.set_ImageOwnerAlias('self')

        try:
            response_string = self.clt.do_action_with_exception(request)
            response = json.loads(response_string)
        except Exception as e:
            return {}
        else:
            return {str(x['ImageId']): str(x['ImageName']) for x in response['Images']['Image']}


if __name__ == '__main__':
    handler = ECSHandler('L', 'I', 'cn-hongkong')
    instances, is_success, next_page = handler.get_instances(1)
    print instances
    print is_success
    print next_page



