

def playground():
    from termx.config import config
    print(config.COLORS.GREEN('TEST'))
    config({'COLORS': {'GREEN': 'BLUE'}})

    print(config.COLORS.GREEN('TEST'))
    import ipdb; ipdb.set_trace()
