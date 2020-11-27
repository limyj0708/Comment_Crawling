import argparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import time
import os.path
import csv
import re

import youtube_comment_crawl as ycc

with open('youtube_key.json') as json_file:
    API_INFO = json.load(json_file)
    DEVELOPER_KEY = API_INFO['DEVELOPER_KEY']
    YOUTUBE_API_SERVICE_NAME = API_INFO['YOUTUBE_API_SERVICE_NAME']
    YOUTUBE_API_VERSION = API_INFO['YOUTUBE_API_VERSION']

class get_videos:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
    
    def __init__(self, query, part, order, maxResults, maxPage, part_c, order_c, maxResults_c, maxPage_c, publishedAfter, publishedBefore):
        self.q = query # 검색어
        self.part = part # 어떤 원소를 표시?
        self.order = order # 정렬 순서. date, rating, relevance, title, videoCount, viewCount
        self.maxResults = maxResults # 한 페이지의 최대 결과는 몇 개까지 표시?
        self.maxPage = maxPage # 최대 몇 페이지까지 탐색?
        self.part_c = part_c # comment 원소
        self.order_c = order_c # comment 정렬
        self.maxResults_c = maxResults_c # comment 최대결과
        self.maxPage_c = maxPage_c # comment 최대탐색페이지
        self.publishedAfter = publishedAfter # 이 시점 이후로 업로드 됨
        self.publishedBefore = publishedBefore # 이 시점 이전에 업로드 됨
        
    def replace_html_charEntity(self, text):
        text = re.sub('<[^<]+?>', '', text)
        text = text.replace('&nbsp;', ' ')
        text = text.replace('&quot;', ' ')
        text = text.replace('&amp;', '&')
        text = text.replace('&lt;', '<')
        text = text.replace('&gt;', '>')
        text = text.replace('&#39;', "'")
        return text
        
    def save_json(self, data, filename):
        with open(filename+'.json', 'w') as outfile:
            json.dump(data, outfile)
            
    def save_csv(self, write_list):
        filename = self.q + '_' +self.publishedAfter.replace(':','') + '_' +self.publishedBefore.replace(':','') + '.csv'
        file_exists = os.path.isfile(filename)
        with open(filename, 'a', newline='', encoding='UTF-8') as csvfile:
            writer = csv.writer(csvfile, delimiter='|')
            if not file_exists:
                headers = ['videoUrl', 'channelId', 'vidTitle', 'vidPublishedAt'
                           ,'commmentText', 'commentPublishedAt', 'commentAuthor']
                writer.writerow(headers)
            writer.writerow(write_list)

    def crawl_videos(self, nextPageToken_pa=''):
        search_response = self.youtube.search().list(
            q = self.q
            ,part = self.part #'id,snippet'
            ,order = self.order
            ,maxResults = self.maxResults
            ,pageToken = nextPageToken_pa # 다음 페이지 토큰.
            ,publishedAfter = self.publishedAfter
            ,publishedBefore = self.publishedBefore
        ).execute()
        
        ycc1 = ycc.get_commentThreads(self.part_c, self.order_c, self.maxResults_c, self.maxPage_c)
    
        for each_video in search_response.get('items', []):
            video_dic = {'title':'', 'videoId':'', 'channelId':'', 'publishedAt':'','commentThreads':''}
            # 비디오 1개 당 json 파일 1개로 개별저장.
            if each_video['id']['kind'] == 'youtube#video':
                video_dic['title'] = each_video['snippet']['title']
                videoId = each_video['id']['videoId'] # comment_crawl의 argument로 사용해야 하기 때문에 따로 변수에 할당
                video_dic['videoId'] = videoId
                video_dic['channelId'] = each_video['snippet']['channelId']
                video_dic['publishedAt'] = each_video['snippet']['publishedAt']
                video_dic['commentThreads'] = ycc1.get_main(videoId)
                ycc1.commentThreads_list = [] # 클래스 인스턴스의 comment 정보 초기화 
                self.save_json(video_dic,video_dic['publishedAt'].replace(':', '') + '_' + videoId)
                for each_comment in video_dic['commentThreads']:
                    csv_write_list = ['https://www.youtube.com/watch?v='+video_dic['videoId'], video_dic['channelId'], self.replace_html_charEntity(video_dic['title']), video_dic['publishedAt']]
                    csv_write_list.extend([self.replace_html_charEntity(each_comment['text']), each_comment['publishedAt'], each_comment['author']])
                    self.save_csv(csv_write_list)
                    for each_reply in each_comment['replies']:
                        csv_write_list = ['https://www.youtube.com/watch?v='+video_dic['videoId'], video_dic['channelId'], self.replace_html_charEntity(video_dic['title']), video_dic['publishedAt']]
                        csv_write_list.extend([self.replace_html_charEntity(each_reply['text']), each_reply['publishedAt'], each_reply['author']])
                        self.save_csv(csv_write_list)
        return search_response.get('nextPageToken')
    
    def get_main(self):
        loopNum = 0
        checkValue = ''
        while (checkValue != None) and (loopNum < self.maxPage):
            checkValue = self.crawl_videos(nextPageToken_pa=checkValue)
            loopNum += 1
            time.sleep(0.05)
    
'''
if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--q', help='Search term', default='Google')
    parser.add_argument('--max-results', help='Max results', default=30)
    args = parser.parse_args()

try:
    youtube_search(args)
except HttpError as e:
    print ('An HTTP error %d occurred:\n%s' % (e.resp.status, e.content))
    '''