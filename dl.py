from dataclasses import dataclass
import os
import csv
import xlsxwriter
import sys

import googleapiclient.discovery


@dataclass
class Comment:
    id: str
    date: str
    author: str
    text: str
    replies: list


@dataclass
class Reply:
    id: str
    date: str
    author: str
    text: str


@dataclass
class CsvRow:
    id: str
    parent_id: str
    date: str
    author: str
    text: str


def main():
    with open('.secrets') as f:
        for line in f:
            if line.startswith('apiKey='):
                api_key = line.split('=')[1].strip()
                break
    video_url = input("Enter video url: ")
    video_id = extract_video_id(video_url)

    if not os.path.exists('comments'):
        os.mkdir('comments')
    filename = os.path.join('comments', f'comments-{video_id}.xlsx')
    print(f"Downloading comments for video {video_id} to {filename}")
    youtube = build_client(api_key)
    comments = get_comments(youtube, video_id)
    comments.sort(key=lambda x: x.date)
    to_xlsx(filename, comments)
    print("Done!")


def extract_video_id(url):
    return url.split('=')[1]


def print_comments(comments):
    comments.sort(key=lambda x: x.date)
    for comment in comments:
        print(f' - {comment.date}: {comment.author}: {comment.text}'.encode('utf-8'))
        comment.replies.sort(key=lambda x: x.date)
        for reply in comment.replies:
            print(f'   - {reply.date}: {reply.author}: {reply.text}'.encode('utf-8'))


def to_xlsx(filename, comments):
    workbook = xlsxwriter.Workbook(filename)
    worksheet = workbook.add_worksheet()
    row = 0
    for col, header in enumerate(['id', 'parent_id', 'date', 'author', 'text']):
        worksheet.write(row, col, header)
    for comment in comments:
        row += 1
        worksheet.write(row, 0, comment.id)
        worksheet.write(row, 1, '')
        worksheet.write(row, 2, comment.date)
        worksheet.write(row, 3, comment.author)
        worksheet.write(row, 4, comment.text)
        comment.replies.sort(key=lambda x: x.date)
        for reply in comment.replies:
            row += 1
            worksheet.write(row, 0, reply.id)
            worksheet.write(row, 1, comment.id)
            worksheet.write(row, 2, reply.date)
            worksheet.write(row, 3, reply.author)
            worksheet.write(row, 4, reply.text)
    workbook.close()


def build_client(api_key):
    # Disable OAuthlib's HTTPS verification when running locally.
    # *DO NOT* leave this option enabled in production.
    os.environ["OAUTHLIB_INSECURE_TRANSPORT"] = "1"

    api_service_name = "youtube"
    api_version = "v3"
    # DEVELOPER_KEY = "AIzaSyBX2Pp5toKkHcD32PPVybyW8dmiMOiHT2Q"

    return googleapiclient.discovery.build(
        api_service_name, api_version, developerKey = api_key)


def get_comments(youtube, video_id, comments=[], token=''):
    video_response = youtube.commentThreads().list(
         part='id,snippet,replies',
         videoId=video_id,
         pageToken=token).execute()

    for item in video_response['items']:
        id = item['id']
        cmt = item['snippet']['topLevelComment']
        date = cmt['snippet']['publishedAt']
        author = cmt['snippet']['authorDisplayName']
        text = cmt['snippet']['textOriginal']
        comment = Comment(id, date, author, text, [])
        if 'replies' in item.keys():
            for reply in item['replies']['comments']:
                comment.replies.append(Reply(
                    reply['id'],
                    reply['snippet']['publishedAt'],
                    reply['snippet']['authorDisplayName'],
                    reply['snippet']['textOriginal']))
        comments.append(comment)
    if "nextPageToken" in video_response:
        return get_comments(youtube, video_id, comments, video_response['nextPageToken'])
    else:
        return comments


if __name__ == "__main__":
    main()
