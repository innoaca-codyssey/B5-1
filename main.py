from cache import Cache


def main():
    cache = Cache()
    while True:
        try:
            command = input('mini-redis> ')
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if command.strip().lower() in ('exit', 'quit'):
            break
        result = cache.execute(command)
        if result:
            print(result)


if __name__ == '__main__':
    main()
