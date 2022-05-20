from matplotlib import font_manager, rc  # 한글 사용
import matplotlib.pyplot as plt  # 시각화 모듈
from wordcloud import WordCloud
from collections import Counter
from eunjeon import Mecab
from PIL import Image
import numpy as np

from modules.path_gatter import get_img_path

# 클래스: VzPie
# 기능  : 파이그래프 시각화
# 입력값: file_name=파일저장경로 | patent_db=DB커넥터 | data_list=시각화 할 데이터
class VzPie:
  def __init__(self, file_name:str):
    self.file_name = file_name
    self.__types = ["A", "B", "C", "D", "E", "F", "G", "H", "Y"]  # CPC 분류 리스트
    self.__explains = ["필수품", "운수", "화학", "섬유", "고정구조물(건물)", "기계공학", "물리", "전기", "상호참조기술"]  # CPC 분류 설명
    self.__lengths = []


  # 함수명: set_etc
  # 기능  : cpc 9개 항목 중 호출 된 값이 6개 이상일 경우 1~4위 제외, 5순위 이하 etc로 정리
  def set_etc(self):
    for idx, length in enumerate(self.__lengths):
      if not length:
        self.__types = self.__types[:idx]
        self.__explains = self.__explains[:idx]
        self.__lengths = self.__lengths[:idx]
        break
    if len(self.__lengths) > 5:
      etc = {
        "etc_key": self.__types[4:],
        "etc_explain": self.__explains[4:],
        "etc_len": sum(self.__lengths[4:]),
      }
      self.__types = self.__types[:4]
      self.__explains = self.__explains[:4]
      self.__lengths = self.__lengths[:4]
      self.__types.append(f'etc({", ".join(etc["etc_key"])})')
      self.__explains.append(f'etc({", ".join(etc["etc_explain"])})')
      self.__lengths.append(etc["etc_len"])


  # 함수명: sort_arrays
  # 기능  : 세 가지 리스트의 순서를 동일하게 맞추기 위한 buble sort
  def sort_arrays(self):
    n = len(self.__lengths)
    for i in range(n-1):
      for j in range(n-i-1):
        if self.__lengths[j] < self.__lengths[j+1]:
          self.__lengths[j], self.__lengths[j+1] = self.__lengths[j+1], self.__lengths[j]
          self.__types[j], self.__types[j+1] = self.__types[j+1], self.__types[j]
          self.__explains[j], self.__explains[j+1] = self.__explains[j+1], self.__explains[j]


  # 함수명: get_cpc_length
  # 기능  : db에서 cpc를 가져오는 함수
  def get_cpc_length(self):
    cpc_dict = {key:0 for key in self.__types}
    if self.data_list:  # 데이터가 있는 경우: 검색결과 시각화
      for data in self.data_list:
        for cpc in data["cpc"]:
          cpc_dict[cpc[0]] += 1
    else:  # 데이터가 없는 경우: 전체 시각화
      data_list = self.patent_db.select_db("cpc", "cpc")
      for data in data_list:
        if data["cpc"]:
          cpc_dict[data["cpc"][0]] += 1
    for type in self.__types:
      self.__lengths.append(cpc_dict[type])


  # 함수명: get_vz_pie
  # 기능  : 파이 그래프 이미지 생성, 저장, 출력
  def get_vz_pie(self, patent_db:object=None, data_list:list=[]):
    self.patent_db = patent_db
    self.data_list = data_list
    # 한글 폰트 세팅
    font_path = "C:/Windows/Fonts/gulim.ttc"
    font = font_manager.FontProperties(fname=font_path).get_name()
    rc("font", family=font)

    self.get_cpc_length()  # db에서 cpc를 가져오는 함수
    self.sort_arrays()  # 값 내림차순 정렬
    self.set_etc()  # 하위 5개 항목 etc로 통합

    labels = []  # key: value 형태의 문자열 레이블 만들기
    for key,val in zip(self.__types, self.__explains):
      if "etc" in key:
        labels.append(key)
      else:
        labels.append(f'{key}: {val}')

    # https://matplotlib.org/stable/tutorials/colors/colormaps.html
    cmap = plt.get_cmap("Pastel1")  # Pastel1 컬러맵
    colors = cmap(range(len(self.__types)))

    wedgeprops = {
      "width": 0.9,
      "edgecolor": "w",
      "linewidth": 2
    }
    plt.pie(  # 파이 그래프 옵션
      self.__lengths,
      labels=labels,
      autopct="%.2f%%",
      startangle=100,
      wedgeprops=wedgeprops,
      colors=colors
    )
    plt.legend(self.__explains, loc="lower left", fontsize=8, frameon=False)

    # 생성된 파이그래프 저장
    plt.savefig(self.file_name, dpi=200)
    plt.show()



# 클래스: VzWordcloud
# 기능  : 워드클라우드 시각화
# 입력값: stopwords=불용어리스트 | file_name=파일저장경로
class VzWordcloud:
  def __init__(self, stopwords:list, file_name:str):
    self.__stopwords = stopwords
    self.file_name = file_name


  # 함수명: count_words
  # 기능  : 단어가 사용된 횟수 카운트
  # 입력값: text=불용어 리스트 제외 된 데이터
  # 반환값: counted_words(dict)={단어: n, } 형태의 카운트 된 딕셔너리
  def count_words(self, text:str):  # 명사를 추출하여 1개 이상이면 리턴하는 함수
    nouns = Mecab().nouns(text)
    words = [n for n in nouns if len(n) > 1]
    counted_words = Counter(words)
    return counted_words


  # 함수명: get_text
  # 기능  : 불용어를 제외한 텍스트 데이터
  # 반환값: result(str)=불용어 리스트를 제외한 title, summary 데이터
  def get_text(self):
    # if: 데이터가 있는 경우 -> 검색결과 시각화
    # else: 데이터가 없는 경우 -> 전체 시각화
    data_list = self.data_list if self.data_list else self.patent_db.select_db("title, summary")

    result = ""
    for dict in data_list:
      txt = dict["title"] + dict["summary"]
      for hide in self.__stopwords:
        txt = txt.replace(hide, "")  # 데이터내 불용어 리스트(stopwords) 제외
      result += txt
    return result


  # 함수명: color_func
  # 설명  : show_vz_wc 에서 사용하는 컬러펑션, return의 randint 입력값을 변경해 색을 조정할 수 있음
  # 참고  : https://www.w3schools.com/colors/colors_picker.asp  # hsl 좌표
  # 매개변수 없으면 에러
  def color_func(self, word,font_size,position,orientation,random_state=None,**kwargs):
    return(f'hsl({np.random.randint(0,25)},{np.random.randint(90,100)}%, {np.random.randint(40,60)}%)')


  # 함수명: get_vz_wc
  # 기능  : 워드클라우드 이미지 생성, 저장, 출력
  # 입력값: patent_db=DB커넥터 | data_list=시각화 할 데이터
  def get_vz_wc(self, patent_db:object=None, data_list:list=[]):
    self.patent_db = patent_db
    self.data_list = data_list
    text = self.get_text()  # 불용어 리스트를 제외한 데이터
    counted_words = self.count_words(text)  # 명사만 추출

    img = Image.open(get_img_path("./images/kipi.jpg"))  # 워드클라우드에 사용할 이미지 호출
    img_array = np.array(img)

    wc = WordCloud(  # 워드클라우드 옵션
      font_path="malgun",
      width=400,
      height=400,
      scale=2.0,
      max_font_size=250,
      mask=img_array,
      background_color="white",
      color_func=self.color_func
    )

    gen = wc.generate_from_frequencies(counted_words)  # 워드클라우드 생성
    plt.imshow(gen)
    plt.axis("off")

    plt.savefig(self.file_name, dpi=200)  # 생성된 워드클라우드 저장
    plt.show()
