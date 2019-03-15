import requests
from requests.adapters import HTTPAdapter
import json, time
from bs4 import BeautifulSoup
from urllib.request import urlopen
from urllib.parse import urlparse

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
        'Cookie': 'uvi=wU8tHtkSeVmpXsMnr0WqxB0JHiWSAOuzf7ThqRmKMsjS7i01; PHPSESSID=3demtdaaip4jni27r8p7lo3h1k',
        'X-Requested-With': 'XMLHttpRequest'
    }
    return headers

def post_request(origin_url, name, _id):
    parse = urlparse(origin_url)
    data = create_post_data(origin_url, name, _id)
    headers = create_headers(origin_url)
    info = '(表单: %s, 姓名: %s, 学号: %s)' % (origin_url, name, _id)
    
    if data == None:
        return '[%s] 查询失败! (%s)' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), info)
        return

    url = 'http://%s/handler/web/form_runtime/handleSubmit.php' % parse.hostname
    try:
        s = requests.Session()
        s.mount('http://', HTTPAdapter(max_retries=5))
        r = s.post(url, data=data, headers=headers, timeout=5)
        if r.status_code == 200 and r.text == '{"r":0}':
            return '[%s] 发送成功! (%s)' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), info)
        else:
            return '[%s] 发送失败. (%s)' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), info)
    except requests.ConnectionError as e:
        return '[%s] 连接失败. (%s)' % (time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()), info) + e.args

if __name__ == '__main__':
    origin_url = 'http://tk5rrvu0xdnrh3el.mikecrm.com/sVQqA5l'
    name = '陈海天'
    _id = '3150104457'
    print(post_request(origin_url, name, _id))