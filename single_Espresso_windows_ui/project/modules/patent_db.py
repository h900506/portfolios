SQL = """SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0;
SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0;
SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='ONLY_FULL_GROUP_BY,STRICT_TRANS_TABLES,NO_ZERO_IN_DATE,NO_ZERO_DATE,ERROR_FOR_DIVISION_BY_ZERO,NO_ENGINE_SUBSTITUTION';
CREATE SCHEMA IF NOT EXISTS `patent_data` DEFAULT CHARACTER SET utf8 ;
USE `patent_data` ;
CREATE TABLE IF NOT EXISTS `patent_data`.`patents` (
  `application_number` CHAR(13) NOT NULL,
  `applicant` VARCHAR(1000) NOT NULL,
  `summary` VARCHAR(10000) NOT NULL,
  `title` VARCHAR(1000) NOT NULL,
  PRIMARY KEY (`application_number`))
ENGINE = InnoDB;
CREATE TABLE IF NOT EXISTS `patent_data`.`cpc` (
  `cpc` VARCHAR(1000) NOT NULL,
  `application_number` CHAR(13) NOT NULL,
  CONSTRAINT `cpc_application_number`
    FOREIGN KEY (`application_number`)
    REFERENCES `patent_data`.`patents` (`application_number`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;
CREATE TABLE IF NOT EXISTS `patent_data`.`keywords` (
  `keyword` VARCHAR(1000) NOT NULL,
  `application_number` CHAR(13) NOT NULL,
  CONSTRAINT `keywords_application_number`
    FOREIGN KEY (`application_number`)
    REFERENCES `patent_data`.`patents` (`application_number`)
    ON DELETE CASCADE
    ON UPDATE CASCADE)
ENGINE = InnoDB;
SET SQL_MODE=@OLD_SQL_MODE;
SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS;
SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS;"""

import pymysql

# 클래스: patentDB
# 기능  : 데이터베이스 모듈
# 입력값: user=mysql 사용자 계정 정보 | ischecked=테이블이 생성 되어 있는지 여부
class PatentDB:
  def __init__(self, user:dict, ischecked:bool=False) -> None:
    if not ischecked:
      self.check_db(user)
    self.__db = pymysql.connect(
      user=user["id"],
      passwd=user["pw"],
      host="127.0.0.1",
      db="patent_data",
      charset="UTF8",
      autocommit=True
    )
    self.__cursor = self.__db.cursor(pymysql.cursors.DictCursor)


  # 함수명: check_db
  # 기능  : 데이터베이스, 테이블이 없는 경우 생성
  # 입력값: user=mysql 사용자 계정 정보
  def check_db(self, user:dict) -> None:
    db_checker = pymysql.connect(
      user=user["id"],
      passwd=user["pw"],
      host="127.0.0.1",
      charset="UTF8",
    ).cursor()
    commends = SQL.split(";")[:-1]
    for cmd in commends:
      db_checker.execute(cmd)
    db_checker.close()


  # 함수명: insert_db
  # 기능  : database insert
  # 입력값: table=테이블명 | data={컬럼명:값, } 형태의 insert 할 데이터
  def insert_db(self, table:str, data:dict) -> None:
    sql = f'''
      INSERT IGNORE INTO `{table}` ({",".join(data.keys())})
      VALUES ('{"','".join(data.values())}');
    '''
    self.__cursor.execute(sql)


  # 함수명: select_db
  # 기능  : database select
  # 입력값: query=컬럼명 | table=테이블명 | where=조건
  # 반환값: result(list)={컬럼명:값, } 형태의 dict 가 포함 된 리스트
  def select_db(self, query:str="*", table:str="patents", where:str="") -> list:
    sql = f'SELECT {query} FROM `{table}` {"WHERE "+where if where else ""};'
    self.__cursor.execute(sql)
    result = self.__cursor.fetchall()
    return result


  # 함수명: delete_db
  # 기능  : database delete
  # 입력값: table=테이블명 | query=출원번호(PK)
  def delete_db(self, table:str, query:str) -> None:
    sql = f'''
      DELETE FROM `{table}`
      WHERE application_number = {query}
    '''
    self.__cursor.execute(sql)


  # 함수명: close_db
  # 기능  : 데이터 베이스 연결 해제, 모듈을 사용한 곳에서 DB 사용이 끝난 후 호출
  def close_db(self) -> None:
    self.__db.close()
