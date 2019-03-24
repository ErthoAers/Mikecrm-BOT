import requests
from requests.adapters import HTTPAdapter
import json, time
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse
import argparse
import random

from apscheduler.schedulers.blocking import BlockingScheduler
from datetime import datetime, timedelta

def get_time(url):
    try:
        html = urlopen(url).read()
        soup = BeautifulSoup(html,"html.parser")
        titles = soup.select("head  script")
        if titles[0].text.strip().split('\n')[5].strip().startswith('var SOUL'):
            info = titles[0].text.strip().split('\n')[5].strip()[11:-1]
        else:
            info = titles[0].text.strip().split('\n')[6].strip()[11:-1]
        content = json.loads(info)
        date = content['se']['apf']
    except:
        date = None
    
    return date

def create_post_data(origin_url, name, _id):
    parse = urlparse(origin_url)

    html = urlopen(origin_url).read()
    soup = BeautifulSoup(html,"html.parser")
    titles = soup.select("head  script")
    info = titles[0].text.strip().split('\n')[5].strip()[11:-1]
    content = json.loads(info)

    try:
        cpo = content['cpo'].split(';')
        i = content['_m']['I']
        t = parse.path[1:]
        s = content['_m']['FRS']
        acc = content['_m']['ACC']
    except:
        return None

    post_data = {'cvs':{'i': i, 't': t, 's': s, 'acc': acc, 'r': '', 'c': {'cp': {cpo[0]: name, cpo[1]: _id}}}}
    data = {'d': json.dumps(post_data)}
    return data

def create_headers(origin_url):
    parse = urlparse(origin_url)
    
    headers = {
        'Accept': 'application/json, text/javascript, */*; q=0.01',
        'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
        'Origin': "http://%s" % parse.hostname,
        'Referer': origin_url,
        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_2) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.121 Safari/537.36',
        'X-Requested-With': 'XMLHttpRequest'
    }
    return headers

def get_table(name, _id, origin_url):
    back_log = 'back_log/back.json'
    with open(back_log) as f:
        table = json.load(f)
    for idx, info in enumerate(table):
        if name == info['name'] and _id == info['idnum'] and origin_url == info['url']:
            request_idx = idx
            break
    return (table, request_idx)

def post_request(origin_url, name, _id):
    back_log = 'back_log/back.json'
    parse = urlparse(origin_url)
    data = create_post_data(origin_url, name, _id)
    headers = create_headers(origin_url)
    info = '(表单: %s, 姓名: %s, 学号: %s)' % (origin_url, name, _id)
    
    if data == None:
        table, request_idx = get_table(name, _id, origin_url)
        table[request_idx]['status'] = 'fail'
        with open(back_log, 'w') as f:
            json.dump(table, f)
        print('[%s] 查询失败! (%s)' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), info))

    url = 'http://%s/handler/web/form_runtime/handleSubmit.php' % parse.hostname
    try:
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=5))
        r = s.post(url, data=data, headers=headers, timeout=5)
        if r.status_code == 200 and r.text == '{"r":0}':
            table, request_idx = get_table(name, _id, origin_url)
            table[request_idx]['status'] = 'success'
            print('[%s] 发送成功! (%s)' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), info))
        else:
            table, request_idx = get_table(name, _id, origin_url)
            table[request_idx]['status'] = 'fail'
            print('[%s] 发送失败. (%s)' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), info))
    except requests.ConnectionError as e:
        table, request_idx = get_table(name, _id, origin_url)
        table[request_idx]['status'] = 'fail'
        print('[%s] 连接失败. (%s)' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), info) + e.args)

    with open(back_log, 'w') as f:
        json.dump(table, f)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--url', type=str)
    parser.add_argument('--name', type=str)
    parser.add_argument('--id', type=str)

    opt = parser.parse_args()
    url = opt.url
    name = opt.name
    _id = opt.id
    
    t = datetime.strptime(get_time(url), "%Y-%m-%d %H:%M:%S")
    t = t + timedelta(seconds=random.randint(0, 7))
    scheduler = BlockingScheduler()
    scheduler.add_job(post_request, args=[url, name, _id], run_date=t)
    scheduler.start()
