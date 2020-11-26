import argparse
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError
import json
import time

with open('youtube_key.json') as json_file:
    API_INFO = json.load(json_file)
    DEVELOPER_KEY = API_INFO['DEVELOPER_KEY']
    YOUTUBE_API_SERVICE_NAME = API_INFO['YOUTUBE_API_SERVICE_NAME']
    YOUTUBE_API_VERSION = API_INFO['YOUTUBE_API_VERSION']

class get_commentThreads:
    youtube = build(YOUTUBE_API_SERVICE_NAME, YOUTUBE_API_VERSION,developerKey=DEVELOPER_KEY)
    commentThreads_list = []
    
    def __init__(self, part, order, maxResults, maxPage):
        self.part = part # 어떤 원소를 표시?
        self.order = order # 정렬 순서
        #self.videoId = videoId
        self.maxResults = maxResults # 한 페이지의 최대 결과는 몇 개까지 표시?
        self.maxPage = maxPage # 최대 몇 페이지까지 탐색?
    
    def save_json(self, data, filename):
        with open(filename+'.json', 'w') as outfile:
            json.dump(data, outfile)

    def crawl_commentThreads(self, videoId_pa, nextPageToken_pa=''):
        try : 
            commentThreads_response = self.youtube.commentThreads().list(
                part=self.part,
                #'snippet,replies'
                order=self.order,
                videoId=videoId_pa, # 계속 바뀌어야 하기 때문에, 클래스 변수가 아니고 함수의 인자로 받음
                maxResults=self.maxResults,
                pageToken=nextPageToken_pa
            ).execute()
        except :
            return None
        
        idx = 0
        for commentsThreads in commentThreads_response.get('items', []):
            replies = commentsThreads.get('replies')
            if commentsThreads['snippet']['topLevelComment']['kind'] == 'youtube#comment':
                get_commentThreads.commentThreads_list.append({'text':commentsThreads['snippet']['topLevelComment']['snippet']['textDisplay'],
                                            'author':commentsThreads['snippet']['topLevelComment']['snippet']['authorDisplayName'],
                                            'publishedAt' : commentsThreads['snippet']['topLevelComment']['snippet']['publishedAt'],
                                            'replies':[]})
            if replies != None:
                for each_reply in replies['comments']:
                    get_commentThreads.commentThreads_list[idx]['replies'].append({'text':each_reply['snippet']['textDisplay'],
                                                                'author':each_reply['snippet']['authorDisplayName'],
                                                                'publishedAt':each_reply['snippet']['publishedAt']})
            idx += 1

        # replies는 나중에 달린 댓글이 먼저 나오게 되는 구조다. 나중에 순서를 제대로 쓰려면, pop() 으로 꺼내는 게 좋겠다.

        return commentThreads_response.get('nextPageToken')
        
    def get_main(self, videoId):
        loopNum = 0
        checkValue = ''
        while (checkValue != None) and (loopNum < self.maxPage): #nextPageToken이 있나 검사
            checkValue = self.crawl_commentThreads(videoId, nextPageToken_pa=checkValue)
            loopNum += 1
            time.sleep(0.02)
        return get_commentThreads.commentThreads_list
        #self.save_json(get_commentThreads.commentThreads_list,self.videoId)
            