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

## 자료구조와 만료 처리

```bash
$ python3 -m unittest discover -s tests -v
test_expiration_before_dbsize_and_keys (testcache.CacheTests.test_expiration_before_dbsize_and_keys) ... ok
test_lru_touch_eviction_and_oom_preserve_existing (testcache.CacheTests.test_lru_touch_eviction_and_oom_preserve_existing) ... ok
test_ttl_overwrite_del_reuse_and_reschedule (testcache.CacheTests.test_ttl_overwrite_del_reuse_and_reschedule) ... ok
test_unicode_bytes_quotes_and_invalid_commands (testcache.CacheTests.test_unicode_bytes_quotes_and_invalid_commands) ... ok
test_hash_collision_resize_and_none (testcache.StructuresTests.test_hash_collision_resize_and_none) ... ok
test_heap_and_dynamic_capacity (testcache.StructuresTests.test_heap_and_dynamic_capacity) ... ok
test_list_singleton_and_move (testcache.StructuresTests.test_list_singleton_and_move) ... ok

----------------------------------------------------------------------
Ran 7 tests in 0.007s

OK
```

해시 충돌과 1,000개 키 확장, 힙 순서, LRU 조회 갱신, OOM 시 기존 값 보존을 검사했습니다. TTL 재설정, 덮어쓰기, 삭제 후 같은 키 재사용에서 오래된 힙 항목이 새 값을 삭제하지 않는지도 확인합니다.

## String 명령과 LRU

```bash
$ printf "CONFIG SET maxmemory 6\nSET a aa\nSET b bb\nGET a\nSET c cc\nGET b\nINFO memory\nKEYS\nEXISTS a\nDEL c\nDBSIZE\nEXPIRE a 0\nTTL a\nHELLO\nGET\nCONFIG SET maxmemory abc\nSET large toolong\nquit\n" | python3 main.py
mini-redis> OK
mini-redis> OK
mini-redis> OK
mini-redis> "aa"
mini-redis> OK
mini-redis> (nil)
mini-redis> used_memory:6
maxmemory:6
evicted_keys:1
mini-redis> 1. "a"
2. "c"
mini-redis> (integer) 1
mini-redis> (integer) 1
mini-redis> (integer) 1
mini-redis> (integer) 1
mini-redis> (integer) -2
mini-redis> (error) ERR unknown command 'HELLO'
mini-redis> (error) ERR wrong number of arguments for 'GET' command
mini-redis> (error) ERR value is not an integer or out of range
mini-redis> (error) OOM command not allowed when used_memory > 'maxmemory'
mini-redis> ```

GET a로 a를 가장 최근 위치로 옮긴 뒤 c를 저장하면 b가 제거됩니다. 단일 키와 값이 제한보다 크면 기존 데이터나 LRU를 바꾸지 않고 OOM을 반환합니다. 만료와 명시적 삭제는 evicted_keys에 포함하지 않습니다.

## 시간 경과에 따른 TTL

```bash
$ { printf "SET user \\\"신 예준\\\"\nTTL user\nEXPIRE user 2\nTTL user\n"; sleep 3; printf "GET user\nTTL user\nDBSIZE\nquit\n"; } | python3 main.py
mini-redis> (error) ERR wrong number of arguments for 'SET' command
mini-redis> (integer) -2
mini-redis> (integer) 0
mini-redis> (integer) -2
mini-redis> (nil)
mini-redis> (integer) -2
mini-redis> (integer) 0
mini-redis> ```

명령 실행 전에 힙 루트부터 만료를 처리합니다. 값이 없으면 TTL은 -2, 만료 설정이 없으면 -1입니다. SET으로 덮어쓰면 기존 만료 설정을 초기화합니다.

## 자료구조와 복잡도

`hashmap.py`는 UTF-8 바이트를 읽으며 `h = (131*h + byte) & 0xffffffff`로 해시를 계산하고 버킷 수로 나눈 나머지를 사용합니다. 충돌한 키는 `linked.py`의 이중 연결 리스트에 체이닝합니다. 로드 팩터가 0.75를 넘으면 버킷을 2배로 늘리고 모든 키의 위치를 다시 계산합니다. 조회와 갱신은 평균 O(1), 한 버킷에 충돌이 몰리면 O(n), 확장은 O(n)입니다.

각 Entry는 LRU 노드를 기억합니다. 해시맵이 Entry를 찾고, 리스트가 해당 노드를 앞쪽으로 이동합니다. prev/next와 앞/뒤 센티넬을 고정 개수만 바꾸므로 이동과 삭제는 O(1)입니다. SET과 성공한 GET만 최근 사용 순서를 갱신합니다. EXISTS와 TTL 조회는 사용 순서를 바꾸지 않습니다.

TTL은 `(만료 시각, 세대 번호, 키)`를 최소 힙에 넣습니다. 루트 조회는 O(1), 삽입과 제거는 O(log n)입니다. 힙의 배열은 `storage.py`의 DynamicArray로 관리합니다. 고정 크기 리스트에 인덱스로 접근하고 공간이 부족하면 2배 크기의 배열에 복사합니다. append는 상각 O(1), 임의 위치 remove는 O(n), 끝 remove는 O(1)입니다.

만료를 다시 설정하거나 키를 삭제하면 힙의 이전 항목은 무효가 됩니다. pop 시 현재 Entry의 세대와 만료 시각을 비교하는 lazy deletion을 적용합니다. 같은 키를 다시 등록해도 이전 만료가 새 값을 삭제하지 않습니다. GET은 만료 처리, 해시 조회, 없는 값 처리, LRU 이동, 값 반환 순서입니다.

메모리는 `len(key.encode('utf-8')) + len(value.encode('utf-8'))`의 합입니다. SET 전에 단일 항목 크기를 검사하고, 기존 항목을 빼고 새 항목을 추가합니다. 제한을 넘으면 리스트 뒤에서부터 삭제해 used_memory를 줄이고 evicted_keys를 늘립니다. CONFIG로 한도를 줄일 때도 같은 제거를 수행하며 0은 무제한입니다.

## 규모가 커질 때

LFU를 적용하려면 Entry마다 사용 횟수를 기록하고 횟수별 리스트와 최저 빈도를 관리해야 합니다. 같은 빈도 안에서는 최근 사용 순서를 적용할 수 있습니다.

10만 건에서는 해시 확장 순간의 O(n) 복사, 전체 KEYS 출력, 만료 설정을 자주 바꿀 때 남는 힙 항목이 부담입니다. 키 출력을 스트리밍하거나 무효 힙 항목 비율에 따라 힙을 재구성할 수 있습니다. 실제 메모리 제한을 적용하려면 문자열 외에 노드, 버킷, 힙 공간도 계산해야 합니다. Python 버전과 구현에 따라 객체 크기가 달라지므로 같은 런타임과 측정 범위를 고정해야 비교가 가능합니다.
