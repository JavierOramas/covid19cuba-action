from json import dump, load, loads
from hashlib import sha1
from os import listdir, makedirs, path
from .checker import check
from .generator import generate
from .generator_jt_news import generate as generate_jt_news
from .generator_provinces import generate as generate_provinces
from .generator_municipalities import generate as generate_municipalities
from ..static.app_version import APP_VERSION_CODE
from ..static.changelog import changelog as data_changelog
from ..utils import dump_util, send_msg


def run(debug=False):
    try:
        makedirs('api/v1', exist_ok=True)
        ok = check(debug)
        generate(debug)
        generate_provinces(debug)
        generate_municipalities(debug)
        generate_jt_news(debug)
        build_changelog(debug)
        build_full('api/v1', debug)
        build_state(debug)
        build_jt_news_state(debug)
        if ok:
            return True
    except Exception as e:
        send_msg(e, debug)
        if debug:
            raise e
    return False


def build_state(debug):
    dump_util('api/v1', state, debug=debug)


def state(data):
    result = {
        'version': APP_VERSION_CODE,
        'cache': None,
        'data': None,
        'days': 0
    }
    with open('api/v1/full.json', encoding='utf-8') as file:
        text = file.read()
        cache = sha1(text.encode())
        result['data'] = cache.hexdigest()
    with open('api/v1/all.json', encoding='utf-8') as file:
        text = file.read()
        cache = sha1(text.encode())
        result['cache'] = cache.hexdigest()
        data = loads(text)
        days = len(data['evolution_of_cases_by_days']['accumulated']['values'])
        result['days'] = days
    return result


def build_jt_news_state(debug):
    dump_util('api/v1', jt_news_state, debug=debug)


def jt_news_state(data):
    result = {
        'cache': None,
    }
    with open('api/v1/jt_news.json', encoding='utf-8') as file:
        text = file.read()
        cache = sha1(text.encode())
        result['cache'] = cache.hexdigest()
    return result


def build_changelog(debug):
    dump_util('api/v1', changelog, debug=debug)


def changelog(_):
    return data_changelog


def build_full(base_path, debug):
    subdirs = [ name for name in listdir(base_path) if path.isdir(path.join(base_path, name)) ]
    all_data = None
    try:
        with open(path.join(base_path, 'all.json'), encoding='utf-8') as file:
            all_data = load(file)
    except FileNotFoundError:
        pass
    full_data = dict()
    for subdir in subdirs:
        subdir_full_data = build_full(path.join(base_path, subdir), debug)
        if len(list(subdir_full_data.keys())):
            full_data[subdir] = subdir_full_data
    if all_data:
        full_data['all'] = all_data
        if len(subdirs):
            with open(path.join(base_path, 'full.json'), mode='w', encoding='utf-8') as file:
                dump(full_data, file,
                    ensure_ascii=False,
                    indent=2 if debug else None,
                    separators=(',', ': ') if debug else (',', ':'))
    return full_data
