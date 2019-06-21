

def playground():
    from simple_settings import settings
    print(settings.INDENT_COUNT)

    from termx.config import config
    config({'COLORS': {'GREEN': 'blue'}})

    print(settings.COLORS.GREEN)

