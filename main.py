import os
from os import listdir
from os.path import isfile, join
import requests
import json
# from pprint import pprint
from pathlib import Path
BASE_DIR = Path(__file__).resolve().parent

# 存圖片資料夾
PIC_FOLDER = 'pic'
folder = BASE_DIR/PIC_FOLDER
folder.mkdir(exist_ok=True)

# 讀取api次數
TIMES = 30


# 看板名稱
FORUM = os.getenv("forum")
# tg設定
TOKEN = os.getenv("token")
CHAT_ID = os.getenv("chat_id")


def dl_or_send_pic(posts, folder):
    for p in posts:
        id = str(posts[p]['id'])
        cnt = 0
        for m in posts[p]['media']:
            cnt += 1
            pic_url = m['url']
            fn = id+f'_{cnt}_'+pic_url.rsplit('/', 1)[-1]
            pic_fn = folder/fn

            # download to {PIC_FOLDER}
            # dl_pic(url=pic_url, filename=pic_fn)

            # send to telegram bot
            send_to_tg(pic_url+'\n'+f'https://www.dcard.tw/f/{FORUM}/p/{id}')


def send_to_tg(text=''):
    url = f'https://api.telegram.org/bot{TOKEN}/sendMessage?chat_id={CHAT_ID}&text={text}'
    rq = requests.get(url)
    print(text, 'SEND!')


def dl_pic(url, filename):
    img = requests.get(url)
    with open(filename, 'wb') as f:
        f.write(img.content)
    print(filename, 'DL!')


def read_api(ba='before', postid=None):
    if not postid:
        url = f'https://www.dcard.tw/_api/forums/{FORUM}/posts'
    else:
        url = f'https://www.dcard.tw/_api/forums/{FORUM}/posts?{ba}={postid}'

    rq = requests.get(url).json()

    posts = {}  # 存API內容

    # 避免重複
    post_read = set([f.split('_')[0]
                     for f in listdir(PIC_FOLDER) if isfile(join(PIC_FOLDER, f))])

    for _ in rq:
        id = _['id']
        if _['gender'] == 'F' and _["media"]:
            if str(id) in post_read:
                pass
                # continue
            posts[id] = _
            post_read.add(id)

    min_id, max_id = rq[-1]['id'], rq[0]['id']
    print(min_id, '<', max_id)
    return posts, min_id, max_id


def main():
    time = TIMES - 1
    posts, postid, _ = read_api()
    if posts:
        dl_or_send_pic(posts=posts, folder=BASE_DIR/PIC_FOLDER)
    for i in range(time):
        posts, postid, _ = read_api(postid=postid)
        if posts:
            dl_or_send_pic(posts=posts, folder=BASE_DIR/PIC_FOLDER)


if __name__ == '__main__':
    main()
