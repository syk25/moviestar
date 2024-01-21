from datetime import datetime
import re
import random
from pymongo import MongoClient
import requests
from bs4 import BeautifulSoup

client = MongoClient('mongodb://jungle:jungle@localhost:27017/dbjungle')
db = client.dbjungle


def insert_all():
    # URL을 읽어서 HTML를 받아오고,
    headers = {'User-Agent' : 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'}
    data = requests.get('https://www.moviechart.co.kr/rank/realtime/index/image', headers=headers)

    # HTML을 BeautifulSoup이라는 라이브러리를 활용해 검색하기 용이한 상태로 만듦
    soup = BeautifulSoup(data.text, 'html.parser')

    # select를 이용해서, li들을 불러오기
    movies = soup.find_all("li", class_="movieBox-item")
    print(len(movies))

    # movies (li들) 의 반복문을 돌리기
    for movie in movies:
        # 영화 제목
        title = movie.find("img")["alt"]

        # 년,월,일
        release_date = re.search(r'\d{4}\.\d{2}\.\d{2}', movie.find("li", class_="movie-launch").text).group(0)
        date_obj = datetime.strptime(release_date, '%Y.%m.%d')
        year = date_obj.year
        month = date_obj.month
        day = date_obj.day
        
        # 영화 정보 URL 을 추출한다.
        info_url = f"https://www.moviechart.co.kr/{movie.find('a')['href']}"
        
        # 누적 관객 수
        detail_data = requests.get(info_url, headers=headers)
        detail_soup = BeautifulSoup(detail_data.text, 'html.parser')
        viewer_count_tag = detail_soup.find('dt', text=lambda t: "명" in t)
        if viewer_count_tag:
            viewers = int(viewer_count_tag.get_text(strip=True).split('명')[0].replace(',',''))
        else:
            viewers = "Not found"

        # 영화 포스터 이미지 URL 을 추출한다.
        poster_url = re.search(r'https://.*?\.jpg', f"{movie.find('img')['src']}").group(0)

        # 좋아요를 random 으로 정한다 [0, 100)
        likes = random.randrange(0, 100)

        doc = {
            'title': title,
            'open_date': release_date,
            'open_year': year,
            'open_month': month,
            'open_day': day,
            'viewers': viewers,
            'poster_url': poster_url,
            'info_url': info_url,
            'likes': likes,
            'trashed': False,
        }
        db.movies.insert_one(doc)
        print('완료: ', title, release_date, year, month, day, viewers, poster_url, info_url)


if __name__ == '__main__':
    # 기존의 movies 콜렉션을 삭제하기
    db.movies.drop()

    # 영화 사이트를 scraping 해서 db 에 채우기
    insert_all()
