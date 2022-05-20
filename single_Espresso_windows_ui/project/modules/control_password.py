# 간단한 형태의 카이사르 암호화

# 함수명: encryption
# 기능  : 암호화
# 입력값: 사용자의 DB 비밀번호
# 반환값: 암호화된 비밀번호
def encryption(pw:str) -> str:
  encrypted = ""
  for k in pw:
    encrypted += chr(ord(k)+39)
  return encrypted

# 함수명: decryption
# 기능  : 복호화
# 입력값: 사용자의 DB 비밀번호
# 반환값: 복호화된 비밀번호
def decryption(pw:str) -> str:
  decrypted = ""
  for k in pw:
    decrypted += chr(ord(k)-39)
  return decrypted
