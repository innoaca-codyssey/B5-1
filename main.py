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
        for channel, message in cache.pubsub.drain('cli'):
            print(f'1. "message"\n2. "{channel}"\n3. "{message}"')


if __name__ == '__main__':
    main()
