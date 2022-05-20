import json

# 함수명: write_json
# 기능  : 제이슨 파일로 저장
# 입력값: file_name=파일명 | patent_db=DB커넥터(DB 저장하는 경우) | data_list=검색결과 저장하는 경우
def write_json(file_name:str, patent_db:object=None, data_list:list=[]):
  if not data_list and patent_db:
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

    for data in data_list:  # 검색어, cpc 추가
      app_num = data["application_number"]
      if not app_num in cpc_dict:
        data["cpc"] = [""]  # cpc가 없는 특허정보
      else:
        data["cpc"] = cpc_dict[app_num]
      data["keywords"] = keywords_dict[data["application_number"]]
  with open(file_name, "w", encoding="UTF-8") as file:
    json.dump(data_list, file, indent=2, ensure_ascii=False)
