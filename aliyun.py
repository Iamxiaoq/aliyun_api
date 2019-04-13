# coding=utf-8

import time
from functools import partial
from operator import itemgetter
import hmac
import hashlib
from datetime import datetime
import random
import base64

import requests


AccessKeyId = ''
SecretKey = '' + '&'


common_form = {
    'Action': '',  # 是   API的名称。取值参阅API概览
    'Format': 'JSON',  # 否   返回值的类型，支持JSON与XML。默认为XML
    # 'Version': '2017-12-14',  # 是   API版本号，为日期形式：YYYY-MM-DD
    'AccessKeyId': AccessKeyId,  # 是   阿里云颁发给用户的访问服务所用的密钥ID。查询用户的站点
    # 'AccessKeyId': '',  # 是   阿里云颁发给用户的访问服务所用的密钥ID。查询用户的站点
    # 'Signature': '',  # 是   签名结果串，关于签名的计算方法，请参见签名机制。
    'SignatureMethod': 'HMAC-SHA1',  # 是   签名方式，目前支持HMAC-SHA1
    'Timestamp': '',  # 是   请求的时间戳。日期格式按照ISO8601标准表示，并需要使用UTC时间。格式为：YYYY-MM-ddTHH:mm:ssZ。例如，2016-05-23T12:00:00Z（为北京时间2016年5月23日20点0分0秒）
    'SignatureVersion': '1.0',  # 是   签名算法版本，目前版本是1.0
    'SignatureNonce': '',  # 是   唯一随机数，用于防止网络重放攻击。用户在不同请求间要使用不同的随机数值
}


# 签名参照 https://help.aliyun.com/document_detail/87971.html
quote = partial(requests.utils.quote, safe='-_.~')


def fill_signature(data):
    data['Timestamp'] = ts()
    data['SignatureNonce'] = str(random.random())
    querystr = '&'.join('{}={}'.format(k, quote(v)) for k, v in sorted(data.items(), key=itemgetter(0)))
    str2sign = 'GET&{}&{}'.format(quote('/'), quote(querystr))
    sign = hmac.new(SecretKey.encode('utf-8'), str2sign.encode('utf-8'), digestmod=hashlib.sha1).digest()
    data['Signature'] = base64.b64encode(sign)
    return data


def ts():
    now = datetime.utcnow()
    return '{0:%Y-%m-%d}T{0:%H:%M:%S}Z'.format(now)


def send_request(url, params, try_times=5):
    for i in range(try_times):
        try:
            params = fill_signature(params)
            res = requests.get(url, params=params, proxies={'http': 'http://localhost:8888'})
            json = res.json()
            if json.get('Code') and 'success' not in json['Code'].lower():
                print('error response:', json)
            else:
                return json
        except Exception as e:
            print('error', e)
        time.sleep(i * 0.5)
    raise Exception('Aliyun api is unavailable!!!')


business_url = 'http://business.aliyuncs.com'
business_version = '2017-12-14'
ecs_url = 'http://ecs.aliyuncs.com'
ecs_version = '2014-05-26'


def QueryInstanceBill(month, page=1, page_size=20):
    '''获取 month 账期 ECS 的账单'''
    url = business_url
    params = common_form.copy()
    params['Action'] = 'QueryInstanceBill'
    params['BillingCycle'] = month
    params['ProductCode'] = 'ecs'
    params['Version'] = business_version
    params['PageNum'] = str(page)
    params['PageSize'] = str(page_size)
    return send_request(url, params)


def DescribeInstances(region, page=1, page_size=20):
    '''获取 region 地区 ECS 实例列表信息'''
    url = ecs_url
    params = common_form.copy()
    params['Action'] = 'DescribeInstances'
    params['RegionId'] = region
    params['Version'] = ecs_version
    params['PageNumber'] = str(page)
    params['PageSize'] = str(page_size)
    return send_request(url, params)


if __name__ == '__main__':
    assert AccessKeyId, u'请先填写 AccessKeyId 和 SecretKey'
    print(QueryInstanceBill('2019-03'))
    print(DescribeInstances('cn-zhangjiakou'))
