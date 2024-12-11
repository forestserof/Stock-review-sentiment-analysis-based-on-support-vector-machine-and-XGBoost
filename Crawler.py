import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import random
# TODO 下载这个包
from fake_useragent import UserAgent

# 设置基础 URL
base_url = 'https://guba.eastmoney.com/list,000977_{}.html'
"""
建设银行：601939  18-74
中国银行：601988  21-83
交通银行：601328  15-68
招商银行：600036  20-81
中国软件：600526  50-109
中国卫星：600118  21-48
广电运通：002152  27-43
朋友网络：600588  28-64
浪潮信息：000977  75-192
"""

# 使用fake_useragent获取随机的User-Agent
ua = UserAgent()

# 创建一个列表来存储所有页面的股评标题和更新时间
all_titles = []

# 设置要爬取的页数范围，例如前 2 页
# TODO 改成自己的页码
start_page = 161
end_page = 192

# 每800条数据写入一次文件，并休眠1分钟
# TODO 改成自己的写入间隔
write_interval = 800
data_count = 0

# 使用会话
session = requests.Session()

# 隧道域名:端口号
# TODO 改成自己的隧道域名和端口号
tunnel = "e388.kdltps.com:15818"

# 用户名密码方式
# TODO 改成自己的用户名和密码
username = "t13124459775452"
password = "t0xnx6d4"
proxies = {
    "http": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel},
    "https": "http://%(user)s:%(pwd)s@%(proxy)s/" % {"user": username, "pwd": password, "proxy": tunnel}
}

for page_num in range(start_page, end_page + 1):
    # 构造当前页的 URL
    url = base_url.format(page_num)
    print(f'正在抓取第 {page_num} 页: {url}')

    # 设置随机请求头
    headers = {
        'User-Agent': ua.random,
        'Accept': 'text/html,application/xhtml+xml,application/xml',
        'Accept-Language': 'en-US,en;q=0.5',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1'
    }

    # 增加请求重试机制
    for attempt in range(3):  # 最多重试3次
        try:
            # 发送请求并获取页面内容
            response = session.get(url, headers=headers, proxies=proxies, timeout=10)  # 设置10秒超时
            response.encoding = 'utf-8'
            break  # 如果请求成功，跳出重试循环
        except requests.exceptions.ChunkedEncodingError as e:
            print(f'ChunkedEncodingError: {e} - 正在重试 ({attempt + 1}/3)')
            time.sleep(5)  # 等待几秒后再重试
        except requests.exceptions.RequestException as e:
            print(f'请求失败: {e} - 正在重试 ({attempt + 1}/3)')
            time.sleep(5)
    else:
        print(f"第 {page_num} 页在3次尝试后无法访问，跳过该页。")
        continue  # 跳过到下一页

    # 解析页面内容
    soup = BeautifulSoup(response.text, 'html.parser')

    # 找到所有包含标题和更新时间的行
    rows = soup.find_all('tr', class_='listitem')

    # 提取每行的标题和最后更新时间
    for row in rows:
        # 提取标题
        title_div = row.find('div', class_='title')
        title_text = title_div.find('a').get_text(strip=True) if title_div else "N/A"

        # 提取更新时间
        update_div = row.find('div', class_='update')
        update_text = update_div.get_text(strip=True) if update_div else "N/A"

        # 添加到列表
        all_titles.append({'title': title_text, 'update_time': update_text})

        # 增加计数器
        data_count += 1

        # 当计数器达到800时，写入文件、休眠1分钟并重置计数器
        if data_count % write_interval == 0:
            df = pd.DataFrame(all_titles)
            df.to_csv('stock_titles.csv', index=False, encoding='utf-8', mode='a', header=not data_count)  # 控制表头的写入
            print(f'已写入 {data_count} 条数据到文件')
            time.sleep(random.randint(60, 120))  # 休眠1-2分钟
            all_titles = []

    # 设置一个抓取间隔，避免触发反爬虫机制
    time.sleep(random.uniform(4, 5))  # 随机休眠1-3秒

# 检查是否有剩余数据未写入
if all_titles:
    df = pd.DataFrame(all_titles)
    df.to_csv('stock_titles.csv', index=False, encoding='utf-8', mode='a', header=False)
    print(f'已写入剩余 {len(all_titles)} 条数据到文件')

print(f'共抓取了 {data_count} 条数据')
