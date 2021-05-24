# -*- codeing = utf-8 -*-
# @Time : 2021/4/4 0004 21:54
# @Author : 刘达勇
# @File : 04.梨视频爬取.py
# @Software : PyCharm
'''
分析网站:
    1. 数据来源
        - 静态加载:文字
        - 动态加载:图片、视频、音频
    2. 抓包分析(开发者工具),播放排行榜第28个视频,在Network找到对应AJAX包
        - Headers Request URL,https://www.pearvideo.com/videoStatus.jsp?contId=1725054&mrd=0.30478154697734494
        - Preview srcUrl(伪),https://video.pearvideo.com/mp4/adshort/20210331/1617548102137-15644026_adpkg-ad_hd.mp4
    3. 抓包分析(开发者工具),播放排行榜第28个视频,在Elements找到实际对应链接src
        - (真)https://video.pearvideo.com/mp4/adshort/20210331/cont-1725054-15644026_adpkg-ad_hd.mp4
    4. 抓包分析(开发者工具),滚动滑轮浏览排行榜,在Network中找到AJAX包,分析分页格式
        - Request URL,https://www.pearvideo.com/popular_loading.jsp?reqType=1&categoryId=&start=10&sort=9&mrd=0.11848974489173703
    5. ID+伪Url拼接获取zz真实URL
'''
import requests
import re
import os
import time
import asyncio
list_id = []
list_name = []
if not os.path.exists('./pearvideo'):
    os.mkdir('./pearvideo')

def save_video(video_url,video_name,video_id):
    headers = {
        # id号变化,防盗链,确定来路
        'Referer': 'https://www.pearvideo.com/video_{}'.format(video_id),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    }
    response = requests.get(url=video_url,headers=headers).content
    #检查文件名中的非法字符
    il_chars = ['<','>','/','\\','|',':','"','*','?']
    for i in range(len(il_chars)):
        if il_chars[i] in video_name:
            video_name = video_name.replace(il_chars[i],'')
    # video_name = video_name.replace('<','').replace('>','').replace('/','').replace('\\','').replace('|','').replace(':','').replace('"','').replace('*','').replace('?','')
    with open('./pearvideo/{}.mp4'.format(video_name),'wb') as fp:
        fp.write(response)

        print('{}.mp4,下载完毕!'.format(video_name))

    # os.rename('./pearvideo/{}.mp4'.format(video_id), './pearvideo/{}.mp4'.format(video_name))



def get_url(video_id):
    url = 'https://www.pearvideo.com/videoStatus.jsp?contId={}&mrd=0.30478154697734494'.format(video_id)

    headers = {
        #id号变化,防盗链,确定来路
        'Referer': 'https://www.pearvideo.com/video_{}'.format(video_id),
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/55.0.2883.87 Safari/537.36",
    }
    response = requests.get(url,headers=headers).json()
    url = response['videoInfo']['videos']['srcUrl']
    # print(url)
    url1 = re.findall(r'(h.*/)',url)
    # print(url1)
    url = url.split('/')[-1]
    # print(url)
    url2 = re.findall(r'(-.*4)',url)

    urs= 'cont-' + str(video_id)
    # print(url2)
    url = url1[0] + urs +url2[0]
    # print(url)
    return url
    # print(response.text['videoInfo']['videos']['srcUrl'])

def main():
    for page in range(0,100,10):
        url = 'https://www.pearvideo.com/popular_loading.jsp'
        params = {
            'reqType': '1',
            'categoryId': '',
            'start': '{}'.format(page),
            'sort': '9',
            'mrd': '0.11848974489173703'
        }
        response = requests.get(url,params=params)
        # print(response.text)
        #需要匹配的内容在括号中,'.*?'匹配汉字、数字、字母、符号,获取视频标题
        titles =re.findall('<h2 class="popularem-title">(.*?)</h2>',response.text)

        #获取视频ID,'\d+'匹配多个数字
        num_id = re.findall('<a href="video_(\d+)" class="popularembd actplay">', response.text)
        # print(titles)
        for i in range(len(num_id)):
            list_id.append(num_id[i])
            list_name.append(titles[i])
        # print(num_id)
        # get_url(num_id[0])
    # print(list_id)
    # print(len(list_id))
    time_start = time.time()
    for i in range(len(list_id)):
        url =get_url(list_id[i])
        save_video(url,list_name[i],list_id[i])

    time_end = time.time()

    print('共下载{}个视频,耗时:{}秒。'.format(len(list_id),int(time_end-time_start)))

if __name__ == '__main__':
    main()