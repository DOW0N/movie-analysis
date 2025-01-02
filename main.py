import requests
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib import rcParams
from matplotlib.font_manager import FontProperties

API_KEY = ''  # TMDB API 키

# 한글 폰트 설정 (Windows의 경우)
font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 폰트 경로
font_prop = FontProperties(fname=font_path)
rcParams['font.family'] = font_prop.get_name()

# 2. TMDB에서 현재 상영중인 영화 목록 불러오기
def fetch_movies_from_tmdb(page=1):
    url = f'https://api.themoviedb.org/3/movie/now_playing?api_key={API_KEY}&language=ko-KR&page={page}'
    response = requests.get(url)
    
    if response.status_code == 200:
        data = response.json()
        return data['results']  # 영화 데이터 리스트 반환
    else:
        print("API 요청 실패:", response.status_code)
        return []

# 3. 여러 페이지에서 영화 데이터 수집 (현재 상영중인 영화만)
all_movies = []
for page in range(1, 6):  # 5페이지(100개) 데이터 수집
    movies = fetch_movies_from_tmdb(page)
    all_movies.extend(movies)

# 4. 데이터프레임으로 변환
df = pd.DataFrame(all_movies)

# 5. 2024년 12월에 개봉한 영화만 필터링
df['release_date'] = pd.to_datetime(df['release_date'])  # release_date를 날짜 형식으로 변환
df_december = df[df['release_date'].dt.year == 2024]
df_december = df_december[df_december['release_date'].dt.month == 12]  # 12월에 개봉한 영화만 필터링

# 6. 데이터 확인
print(df_december.head())  # 데이터 미리보기

# 7. 예시 분석

# 영화의 평균 평점 구하기
average_rating = df_december['vote_average'].mean()
print(f"2024년 12월 개봉 영화의 평균 평점: {average_rating}")

# 장르별로 영화 그룹화 (장르 ID 기준)
# 'genre_ids' 컬럼은 영화의 장르 ID 리스트로 되어 있기 때문에 이를 분해하여 각 장르에 대해 카운트를 셈
genres = pd.DataFrame(df_december['genre_ids'].explode().value_counts())
print("2024년 12월 개봉 영화의 장르별 영화 수:")
print(genres)

# 8. 평점 분포 시각화
plt.figure(figsize=(10, 6))
plt.hist(df_december['vote_average'], bins=20, edgecolor='black', color='skyblue')
plt.title('2024년 12월 개봉 영화 평점 분포')
plt.xlabel('평점')
plt.ylabel('영화 수')
plt.grid(True)
plt.show()

# 9. 장르별 평균 평점 계산
df_december['genre_ids'] = df_december['genre_ids'].apply(lambda x: ', '.join(map(str, x)))  # 장르 ID를 문자열로 변환
genre_avg_rating = df_december.groupby('genre_ids')['vote_average'].mean().reset_index()

# 장르별 평균 평점 출력
print("2024년 12월 개봉 영화의 장르별 평균 평점:")
print(genre_avg_rating.sort_values(by='vote_average', ascending=False))

# 10. 장르별 영화 수 시각화
genre_counts = df_december['genre_ids'].value_counts()

# 장르별 영화 수 시각화
plt.figure(figsize=(10, 6))
genre_counts.plot(kind='bar', color='lightcoral')
plt.title('2024년 12월 개봉 영화의 장르별 영화 수')
plt.xlabel('장르')
plt.ylabel('영화 수')
plt.xticks(rotation=90)
plt.grid(True)
plt.show()

# 11. 평점이 높은 상위 10개 영화
top_rated_movies = df_december.sort_values(by='vote_average', ascending=False).head(10)
print("2024년 12월 개봉 영화의 평점이 높은 상위 10개 영화:")
print(top_rated_movies[['title', 'vote_average']])

# 12. 영화 제목과 평점 시각화
top_movies = df_december[['title', 'vote_average']].head(10)
plt.figure(figsize=(10, 6))
plt.barh(top_movies['title'], top_movies['vote_average'], color='seagreen')
plt.title('2024년 12월 개봉 영화의 평점이 높은 상위 10개 영화')
plt.xlabel('평점')
plt.ylabel('영화 제목')
plt.grid(True)
plt.show()

# 13. 수익과 평점 간의 관계 분석 (2024년 12월 개봉 영화에서만 확인)
if 'revenue' in df_december.columns:
    plt.figure(figsize=(10, 6))
    plt.scatter(df_december['revenue'], df_december['vote_average'], alpha=0.5, color='orange')
    plt.title('수익과 평점 간의 관계 (2024년 12월 개봉 영화)')
    plt.xlabel('수익')
    plt.ylabel('평점')
    plt.grid(True)
    plt.show()
else:
    print("'revenue' 컬럼이 없습니다. 2024년 12월 개봉 영화에는 수익 데이터가 포함되지 않을 수 있습니다.")
