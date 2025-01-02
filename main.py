import requests  # HTTP 요청을 보내기 위한 라이브러리 (TMDB API 호출에 사용)
import pandas as pd  # 데이터 처리 및 분석을 위한 라이브러리
import matplotlib.pyplot as plt  # 데이터 시각화를 위한 라이브러리
from matplotlib import rcParams  # Matplotlib의 런타임 설정을 위한 모듈 (폰트 설정 등)
from matplotlib.font_manager import FontProperties  # 폰트 설정을 위한 모듈 (한글 폰트 적용 시 사용)

API_KEY = ' '  # TMDB API 키 (영화 데이터 요청 시 사용)

# 한글 폰트 설정 (Windows 환경 기준)
font_path = "C:/Windows/Fonts/malgun.ttf"  # 맑은 고딕 폰트 경로 설정
font_prop = FontProperties(fname=font_path)  # 지정된 폰트를 로드하여 FontProperties 객체 생성
rcParams['font.family'] = font_prop.get_name()  # Matplotlib에서 한글 폰트 사용 설정

# 2. TMDB에서 현재 상영중인 영화 목록 불러오기 (페이지별 요청 가능)
def fetch_movies_from_tmdb(page=1):
    url = f'https://api.themoviedb.org/3/movie/now_playing?api_key={API_KEY}&language=ko-KR&page={page}'  # TMDB API URL 설정
    response = requests.get(url)  # API 요청 실행
    
    if response.status_code == 200:  # 요청 성공 시
        data = response.json()  # JSON 데이터로 변환
        return data['results']  # 영화 데이터 리스트 반환
    else:
        print("API 요청 실패:", response.status_code)  # 요청 실패 시 오류 코드 출력
        return []

# 3. 여러 페이지에서 영화 데이터 수집 (현재 상영중인 영화 기준, 5페이지)
all_movies = []  # 영화 데이터를 저장할 리스트 초기화
for page in range(1, 6):  # 1~5페이지까지 반복하여 데이터 수집
    movies = fetch_movies_from_tmdb(page)  # 각 페이지에서 영화 데이터 불러오기
    all_movies.extend(movies)  # 전체 영화 데이터 리스트에 추가

# 4. 데이터프레임으로 변환 (pandas 사용)
df = pd.DataFrame(all_movies)  # 수집한 데이터를 데이터프레임으로 변환

# 5. 2024년 12월에 개봉한 영화만 필터링
df['release_date'] = pd.to_datetime(df['release_date'])  # release_date 컬럼을 날짜 형식으로 변환
df_december = df[df['release_date'].dt.year == 2024]  # 2024년 개봉 영화 필터링
df_december = df_december[df_december['release_date'].dt.month == 12]  # 12월 개봉 영화만 필터링

# 6. 데이터 확인 (필터링된 데이터 미리보기)
print(df_december.head())  # 상위 5개 행 출력

# 1. 상영관 수 분석 (상영관 수가 포함된 경우 vote_count 기준 분석)
if 'vote_count' in df_december.columns:
    plt.figure(figsize=(10, 6))  # 그래프 크기 설정
    plt.hist(df_december['vote_count'], bins=20, edgecolor='black', color='steelblue')  # 히스토그램으로 상영관 수 분포 시각화
    plt.title('2024년 12월 개봉 영화 상영관 수 분포')  # 그래프 제목 설정
    plt.xlabel('상영관 수 (투표 수 기준)')  # x축 라벨 설정
    plt.ylabel('영화 수')  # y축 라벨 설정
    plt.grid(True)  # 격자 보이기
    plt.show()  # 그래프 출력
else:
    print("'vote_count' 컬럼이 없습니다. 상영관 데이터가 포함되지 않았습니다.")  # 데이터에 vote_count가 없을 경우 안내

# 2. 가장 인기 있는 영화 (인기도 기준 상위 10개 영화 출력)
top_popular_movies = df_december.sort_values(by='popularity', ascending=False).head(10)  # popularity 기준 정렬 후 상위 10개 선택
print("2024년 12월 개봉 영화 중 가장 인기 있는 상위 10개 영화:")
print(top_popular_movies[['title', 'popularity']])  # 인기 영화 제목과 인기도 출력

# 4. 월별 평균 평점 변화 추이 (전체 데이터 기준 분석)
df['release_month'] = df['release_date'].dt.to_period('M')  # 개봉 날짜를 월 단위로 변환 (2024-12 등으로 표기)
monthly_avg_rating = df.groupby('release_month')['vote_average'].mean().reset_index()  # 월별 평균 평점 계산

plt.figure(figsize=(12, 6))  # 그래프 크기 설정
plt.plot(monthly_avg_rating['release_month'].astype(str), monthly_avg_rating['vote_average'], marker='o', color='purple')  # 월별 평점 그래프 생성
plt.title('월별 평균 평점 변화 추이')  # 그래프 제목 설정
plt.xlabel('개봉 월')  # x축 라벨 설정
plt.ylabel('평균 평점')  # y축 라벨 설정
plt.xticks(rotation=45)  # x축 라벨 회전
plt.grid(True)  # 격자 보이기
plt.show()  # 그래프 출력

# 7. 상위 10개 인기 영화 시각화 (시각적 표현을 위한 바 그래프)
plt.figure(figsize=(10, 6))  # 그래프 크기 설정
plt.barh(top_popular_movies['title'], top_popular_movies['popularity'], color='orange')  # 바 그래프로 인기 영화 시각화
plt.title('2024년 12월 개봉 영화 중 상위 10개 인기 영화')  # 그래프 제목 설정
plt.xlabel('인기도')  # x축 라벨 설정
plt.ylabel('영화 제목')  # y축 라벨 설정
plt.gca().invert_yaxis()  # y축 반전 (인기 영화가 위에서 아래로 정렬)
plt.grid(True)  # 격자 보이기
plt.show()  # 그래프 출력
