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
