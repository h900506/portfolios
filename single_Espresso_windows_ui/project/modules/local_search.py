from sys import maxsize

from eunjeon import Mecab

# 함수명: get_data
# 기능  : DB 데이터 호출
# 입력값: patent_db=DB커넥터
# 반환값: result(list)={컬럼명:값, } 형태의 dict 가 포함 된 리스트
def get_data(patent_db:object) -> list:
  data_list = patent_db.select_db()  # db 데이터 호출

  keywords_dict = {}  # {출원번호:[검색어, 검색어, ...]} 형태의 dict
  for dict in patent_db.select_db(table="keywords"):
    app_num = dict["application_number"]
    if not app_num in keywords_dict:
      keywords_dict[app_num] = [dict["keyword"]]
    else:
      keywords_dict[app_num].append(dict["keyword"])

  cpc_dict = {}  # {출원번호:[cpc, cpc, ...]} 형태의 dict
  for cpc in patent_db.select_db(table="cpc"):
    app_num = cpc["application_number"]
    if not app_num in cpc_dict:
      cpc_dict[app_num] = [cpc["cpc"]]
    else:
      cpc_dict[app_num].append(cpc["cpc"])

  for data in data_list:  # 검색 기능을 위한 점수 부여 및 검색어, cpc 추가
    app_num = data["application_number"]
    if not app_num in cpc_dict:
      data["cpc"] = [""]  # cpc가 없는 특허정보
    else:
      data["cpc"] = cpc_dict[app_num]
    data["keywords"] = keywords_dict[data["application_number"]]
    data["point"] = 0
  return data_list


# 함수명: search
# 기능  : 로컬검색
# 입력값: patent_db=DB커넥터 | query=검색어 | stopwords=불용어
# 반환값: answers(list)=검색결과, 검색결과 없을 경우 []
def search(patent_db:object, query:str, stopwords:list[str]) -> list:
  mc = Mecab()
  keywords = mc.nouns(query)  # 명사만 추출
  keywords = list(filter(lambda n:len(n)>1, keywords))

  splited_query = query.split(" ")
  for _word in splited_query:  # 출원번호 검색을 위해 숫자일 경우 키워드에 추가
    if _word.isdecimal():
      keywords.append(_word)
    else:
      eng_word = ""
      for char in _word:
        if 64 < ord(char) < 91 or 96 < ord(char) < 123:  # 키워드에 영단어 추가
          if not eng_word:
            eng_word += " "
          eng_word += char
      if eng_word:
        keywords.append(eng_word + " ")

  for hide in stopwords:
    if hide in keywords:  # 불용어 삭제
      keywords.remove(hide)

  data_list = get_data(patent_db)

  for data in data_list:
    for _word in keywords:  # 검색어 연관성에 따라 점수 배점
      if _word == data["application_number"]:
        data["point"] += maxsize  # 출원번호와 일치하면 최대 점수 부여
      if (" "+" ".join(data["keywords"])+" ").find(_word) != -1:
        data["point"] += 1.2
      if (" "+data["title"]+" ").find(_word) != -1:
        data["point"] += 1.1
      if (" "+data["summary"]+" ").find(_word) != -1\
      or (" "+data["applicant"]+" ").find(_word) != -1:
        data["point"] += 1

  answers = list(filter(lambda data: data["point"] > 0, data_list))  # 검색 단어가 하나라도 있는 특허 필터
  answers = sorted(answers, key=lambda data: data["point"], reverse=True)  # 점수 순으로 정렬

  return answers
