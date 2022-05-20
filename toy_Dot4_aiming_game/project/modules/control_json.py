import os, json

FILE_NAME = "./scoreboard.json"

def check_json():
  if os.path.isfile(FILE_NAME):
    with open(FILE_NAME, "r", encoding="UTF-8") as file:
      scoreboard = json.load(file)
  else:
    scoreboard = []
    with open(FILE_NAME, "w", encoding="UTF-8") as file:
      json.dump(scoreboard, file, ensure_ascii=False)
  return scoreboard


def update_json(scoreboard:list[dict]) -> None:
  with open(FILE_NAME, "w", encoding="UTF-8") as file:
    json.dump(scoreboard[:10], file, ensure_ascii=False)
