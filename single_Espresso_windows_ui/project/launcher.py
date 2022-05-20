from pkg_resources import DistributionNotFound, get_distribution
import sys
import subprocess


# 함수명: install_pkg
# 기능  : 패키지 설치
# 입력값: pkg=패키지명 | ver=패키지 버전
def install_pkg(pkg:str, ver:str):  # JPype1 은 윈도우에서 pip install 되지 않기때문에 파일로 설치
  package = f'{pkg}=={ver}' if pkg != "JPype1" else "./setting/JPype1-1.3.0-cp310-cp310-win_amd64.whl"
  subprocess.check_call([sys.executable,"-m", "pip", "install", package])


# 함수명: check_pkgs
# 기능  : 설치된 패키지를 확인하고 버전이 다르거나 설치되지 않은 경우 설치
def check_pkgs():
  subprocess.check_call([sys.executable,"-m", "pip", "install", "--upgrade", "pip"])
  packages = {   # 프로그램에 사용 된 패키지 목록
    "JPype1": "1.3.0",
    "beautifulsoup4": "4.10.0",
    "eunjeon": "0.4.0",
    "matplotlib": "3.5.1",
    "matplotlib-inline": "0.1.3",
    "numpy": "1.22.2",
    "PyMySQL": "1.0.2",
    "selenium": "4.1.0",
    "webdriver-manager": "3.5.3",
    "wordcloud": "1.8.1",
    "PyQt5": "5.15.6",
    "pyinstaller": "5.1",
  }
  print("\n◆  패키지 확인 및 설치를 시작합니다 ◆")
  print("\n───────────────────────────────────────────────────────────────────────────────────────────")
  for pkg, ver in packages.items():
    try:
      ver_checker = get_distribution(pkg).version  # 패키지 버전 확인, 설치 되어 있지 않은 경우 에러
      if ver_checker != ver:
        raise DistributionNotFound  # try문 같이 활용하기 위해 버전이 다른 경우도 에러 띄움
    except DistributionNotFound:
      install_pkg(pkg, ver)
      print(f'\n{pkg}_{ver} 패키지가 설치 되었습니다.')
    else:
      print(f'\n{pkg}_{ver} 패키지가 설치 되어 있습니다.')
  print("\n───────────────────────────────────────────────────────────────────────────────────────────")
  print("\n◆  모든 패키지가 확인 및 설치 되었습니다 ◆")

  from espresso import Espresso
  Espresso()


check_pkgs()
