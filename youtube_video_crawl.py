import argparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import time
import youtube_comment_crawl as ycc

DEVELOPER_KEY = 'AIzaSyAIHs872FfLpSNNH57w_m6UoN3jn_xSS2Q'
YOUTUBE_API_SERVICE_NAME = 'youtube'
YOUTUBE_API_VERSION = 'v3'

class get_videos:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
    
    def __init__(self, q, part, order, maxResults, maxPage, part_c, order_c, maxResults_c, maxPage_c):
        self.q = q # 검색어
        self.part = part # 어떤 원소를 표시?
        self.order = order # 정렬 순서. date, rating, relevance, title, videoCount, viewCount
        self.maxResults = maxResults # 한 페이지의 최대 결과는 몇 개까지 표시?
        self.maxPage = maxPage # 최대 몇 페이지까지 탐색?
        self.part_c = part_c # comment 원소
        self.order_c = order_c # comment 정렬
        self.maxResults_c = maxResults_c # comment 최대결과
        self.maxPage_c = maxPage_c # comment 최대탐색페이지
        
    def save_json(self, data, filename):
        with open(filename+'.json', 'w') as outfile:
            json.dump(data, outfile)

    def crawl_videos(self, nextPageToken_pa=''):
        search_response = self.youtube.search().list(
            q=self.q,
            part=self.part, #'id,snippet'
            order=self.order,
            maxResults=self.maxResults,
            pageToken=nextPageToken_pa # 다음 페이지 토큰.
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
                ycc1.commentThreads_list = [] # 클래스 인스턴스의 comment 정보 초기화 
                video_dic['commentThreads'] = ycc1.get_main(videoId)
                self.save_json(video_dic,videoId)
        
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