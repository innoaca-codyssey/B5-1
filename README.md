# B5-1: 정보를 엄청 빠르게 찾아주는 작은 저장소 만들기

해시맵, 이중 연결 리스트, 최소 힙으로 String 명령과 LRU, TTL을 처리하는 Mini Redis입니다. 키와 값의 UTF-8 바이트 수로 메모리를 계산합니다.

## 실행 방법

Python 3.8 이상에서 실행합니다. 네트워크와 파일 저장은 사용하지 않습니다.

```bash
python3 main.py
```

`mini-redis>`에 명령을 입력하고 exit/quit으로 종료합니다. 공백이 있는 값은 큰따옴표로 감쌉니다.

## 실행 환경

```bash
$ python3 --version
Python 3.14.7
```

macOS arm64, Python 표준 라이브러리에서 실행합니다.
