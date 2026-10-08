#!/usr/bin/env python3
"""Собирает статические языковые версии сайта: kk/ и en/.

Русские страницы в корне — источник. Для каждого языка генератор
подставляет переводы из assets/js/i18n.js прямо в HTML (поисковик видит
готовый текст без JavaScript), переводит <title>, description, alt и
aria-label, переписывает относительные пути, canonical и hreflang,
дополняет JSON-LD. Запуск: python3 tools/build-langs.py — из корня проекта,
после любой правки русских страниц или словаря.
"""
import json
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://didariganto.github.io/hotel-ast/'
LANGS = ('kk', 'en')
HTML_LANG = {'ru': 'ru', 'kk': 'kk', 'en': 'en'}
OG_LOCALE = {'ru': 'ru_RU', 'kk': 'kk_KZ', 'en': 'en_US'}
PAGES = ['index', 'hotels', 'amina', 'cityline', 'botanic', 'offers',
         'booking', 'contacts', 'privacy']

# ── Заголовки и описания страниц ─────────────────────────────────────
META = {
    'index': {
        'kk': ('AST Hotels — Астанадағы үш қонақ үй',
               'Астанадағы AST Hotels желісі: AMINA қалалық қонақ үйі, City Line бутик-қонақ үйі және Botanic Garden апартаменттері. Делдалсыз тікелей брондау, WhatsApp арқылы өтінім.'),
        'en': ('AST Hotels — three hotels in Astana, Kazakhstan',
               'AST Hotels in Astana: AMINA city hotel, City Line boutique hotel and Botanic Garden serviced apartments. Book directly with no intermediaries — requests go straight to the hotel on WhatsApp.'),
    },
    'hotels': {
        'kk': ('Астанадағы AST Hotels желісінің қонақ үйлері — үш мекенжай',
               'Қалалық қонақ үй, бутик-қонақ үй және ас үйі бар апартаменттер: AMINA, City Line және Botanic Garden. Формат, аудан және баға бойынша салыстыру.'),
        'en': ('Hotels in Astana — AST Hotels: city hotel, boutique hotel, apartments',
               'Compare the three AST Hotels properties in Astana: AMINA city hotel, City Line boutique hotel and Botanic Garden apartments with a kitchen. Format, district, prices and 2GIS ratings.'),
    },
    'amina': {
        'kk': ('AMINA Hotel — Астанадағы қалалық қонақ үй | AST Hotels',
               'Астана, Шәмші Қалдаяқов көшесі, 15: 21 нөмір, тәулік бойы тіркеу, коворкинг, таңғы ас пен трансфер сұраныс бойынша. 12 000 ₸ бастап. WhatsApp арқылы брондау.'),
        'en': ('AMINA Hotel — city hotel in Astana, Kazakhstan | AST Hotels',
               'AMINA Hotel at 15 Shamshi Kaldayakov St., Astana: 21 rooms, 24-hour check-in, coworking, breakfast and airport transfer on request. From 12 000 KZT per night. Book directly on WhatsApp.'),
    },
    'cityline': {
        'kk': ('City Line Hotel — Астанадағы бутик-қонақ үй | AST Hotels',
               'Астана, Шәмші Қалдаяқов көшесі, 15: бутик-формат, нөмірлердің төрт санаты, лобби-бар, 2ГИС-те 3D-тур. 25 000 ₸ бастап. WhatsApp арқылы брондау.'),
        'en': ('City Line Hotel — boutique hotel in Astana, Kazakhstan | AST Hotels',
               'City Line Hotel at 15 Shamshi Kaldayakov St., Astana: boutique format, four room categories, lobby bar, 3D tour on 2GIS. From 25 000 KZT per night. Book directly on WhatsApp.'),
    },
    'botanic': {
        'kk': ('Botanic Garden Apartments — Астанадағы апартаменттер | AST Hotels',
               'Астана, Түркістан көшесі, 14а: отбасылар мен ұзақ сапарларға арналған ас үйі бар студиялар мен апартаменттер, 7 түннен бастап 10% жеңілдік. WhatsApp арқылы брондау.'),
        'en': ('Botanic Garden Apartments — serviced apartments in Astana | AST Hotels',
               'Botanic Garden Apartments at 14a Turkestan St., Astana: studios and apartments with a kitchen for families and long stays, 10% off from 7 nights. Book directly on WhatsApp.'),
    },
    'offers': {
        'kk': ('Арнайы ұсыныстар — AST Hotels, Астана',
               'AST Hotels желісінің ұсыныстары: Botanic Garden апартаменттерінде 7 түннен бастап 10% жеңілдік, AMINA-да ұзақ тұру тарифі, агрегаторлар комиссиясынсыз тікелей брондау.'),
        'en': ('Special offers — AST Hotels, Astana',
               'AST Hotels offers in Astana: 10% off stays of 7 nights or more at Botanic Garden Apartments, a long-stay rate at AMINA Hotel and direct booking with no aggregator commission.'),
    },
    'booking': {
        'kk': ('Нөмір брондау — AST Hotels, Астана',
               'Астанадағы AST Hotels желісінің үш қонақ үйінің бірінде нөмір брондаңыз: құны лезде есептеледі, өтінім қонақ үйдің WhatsApp-ына кетеді. Делдалсыз, алдын ала төлемсіз.'),
        'en': ('Book a room — AST Hotels, Astana',
               'Book a room at one of the three AST Hotels properties in Astana: the price is calculated instantly and the request goes to the hotel on WhatsApp. No intermediaries, no prepayment on the website.'),
    },
    'contacts': {
        'kk': ('AST Hotels байланысы — Астанадағы үш қонақ үйдің мекенжайлары мен телефондары',
               'AMINA Hotel, City Line Hotel және Botanic Garden Apartments: мекенжайлар, телефондар, WhatsApp, 2ГИС карточкалары. Тұру ережелері және байланыс нысаны.'),
        'en': ('Contact AST Hotels — addresses and phone numbers of three hotels in Astana',
               'AMINA Hotel, City Line Hotel and Botanic Garden Apartments: addresses, phone numbers, WhatsApp, 2GIS listings. House rules and a contact form.'),
    },
    'privacy': {
        'kk': ('Дербес деректерді өңдеу саясаты — AST Hotels',
               'AST Hotels сайты қонақтардың қандай деректерін жинайды, не үшін, қайда береді және келісімді қалай қайтарып алуға болады.'),
        'en': ('Privacy policy — AST Hotels',
               'What guest data the AST Hotels website collects, why, where it is sent and how to withdraw consent.'),
    },
}

# ── Служебные подписи вне словаря ────────────────────────────────────
CHROME = {
    'aria-label="Меню"': {'kk': 'aria-label="Мәзір"', 'en': 'aria-label="Menu"'},
    'aria-label="Выбор отеля"': {'kk': 'aria-label="Қонақ үй таңдау"', 'en': 'aria-label="Choose a hotel"'},
    'aria-label="Закрыть"': {'kk': 'aria-label="Жабу"', 'en': 'aria-label="Close"'},
}

# ── Alt-тексты фотографий ────────────────────────────────────────────
ALT = {
    'kk': {
        'Фасад': 'Қасбеті', 'Стойка регистрации': 'Тіркеу орны', 'Лаунж-зона': 'Лаунж аймағы',
        'Ванная комната': 'Жуынатын бөлме', 'Коворкинг и зона завтраков': 'Коворкинг және таңғы ас аймағы',
        'Холл': 'Холл', 'Номер категории': 'Санаттағы нөмір', 'Гостиная зона': 'Қонақ аймағы',
        'Кафе': 'Кафе', 'Студия': 'Студия', 'Гостиная апартамента': 'Апартамент қонақ бөлмесі',
        'Кухня': 'Ас үй', 'Спальня апартамента': 'Апартамент жатын бөлмесі',
        'Панорама Астаны на закате: высотные дома нового центра': 'Күн батқандағы Астана панорамасы: жаңа орталықтың биік үйлері',
        'с фиолетовыми креслами': 'күлгін креслолармен', 'с зоной отдыха': 'демалыс аймағымен',
        'с большим окном': 'үлкен терезесі бар', 'с зелёными диванами': 'жасыл дивандармен',
        'с обеденным столом': 'ас үстелімен', 'с барной стойкой': 'бар үстелімен',
        'с двумя спальнями': 'екі жатын бөлмелі', 'Зона отдыха в номере категории': 'Санаттағы нөмірдің демалыс аймағы',
        'в Астане': 'Астанада', 'на улице Шамши Калдаякова, 15': 'Шәмші Қалдаяқов көшесі, 15', 'на Туркестан, 14а': 'Түркістан көшесі, 14а',
        'Стандарт': 'Стандарт', 'DeLux': 'DeLux', 'Логотип City Line Hotel на стойке регистрации': 'Тіркеу орнындағы City Line Hotel логотипі',
    },
    'en': {
        'Фасад': 'Facade of', 'Стойка регистрации': 'Front desk of', 'Лаунж-зона': 'Lounge at',
        'Ванная комната': 'Bathroom at', 'Коворкинг и зона завтраков': 'Coworking and breakfast area at',
        'Холл': 'Lobby of', 'Номер категории': 'Room, category', 'Гостиная зона': 'Living area',
        'Кафе': 'Café at', 'Студия': 'Studio at', 'Гостиная апартамента': 'Apartment living room',
        'Кухня': 'Kitchen', 'Спальня апартамента': 'Apartment bedroom',
        'Панорама Астаны на закате: высотные дома нового центра': 'Astana skyline at sunset: high-rises of the new centre',
        'с фиолетовыми креслами': 'with purple armchairs', 'с зоной отдыха': 'with a seating area',
        'с большим окном': 'with a large window', 'с зелёными диванами': 'with green sofas',
        'с обеденным столом': 'with a dining table', 'с барной стойкой': 'with a bar counter',
        'с двумя спальнями': 'with two bedrooms', 'Зона отдыха в номере категории': 'Seating area in room, category',
        'в Астане': 'in Astana', 'на улице Шамши Калдаякова, 15': 'at 15 Shamshi Kaldayakov St.', 'на Туркестан, 14а': 'at 14a Turkestan St.',
        'номера': 'room', 'апартамента': 'apartment', 'Стандарт': 'Standard', 'DeLux': 'DeLux',
        'Логотип City Line Hotel на стойке регистрации': 'City Line Hotel logo at the front desk',
    },
}

# ── Дополнение JSON-LD Hotel ─────────────────────────────────────────
HOTEL_EXTRA = {
    'amina': {
        'numberOfRooms': 21,
        'amenities': ['Wi-Fi', 'Parking', 'Breakfast', '24-hour front desk', 'Coworking', 'Airport transfer'],
        'map': 'https://2gis.kz/astana/firm/70000001060984202',
    },
    'cityline': {
        'amenities': ['Wi-Fi', 'Parking', 'Breakfast', '24-hour front desk', 'Lobby bar', 'Airport transfer'],
        'map': 'https://2gis.kz/astana/firm/70000001105837375',
    },
    'botanic': {
        'amenities': ['Wi-Fi', 'Kitchen', 'Washing machine', 'Parking', '24-hour front desk', 'Workspace'],
        'map': 'https://2gis.kz/astana/firm/70000001044528049',
    },
}
AMENITY_NAMES = {
    'kk': {'Wi-Fi': 'Wi-Fi', 'Parking': 'Тұрақ', 'Breakfast': 'Таңғы ас', '24-hour front desk': 'Тәулік бойы тіркеу',
           'Coworking': 'Коворкинг', 'Airport transfer': 'Әуежайдан трансфер', 'Lobby bar': 'Лобби-бар',
           'Kitchen': 'Ас үй', 'Washing machine': 'Кір жуғыш машина', 'Workspace': 'Жұмыс орны'},
    'ru': {'Wi-Fi': 'Wi-Fi', 'Parking': 'Парковка', 'Breakfast': 'Завтрак', '24-hour front desk': 'Круглосуточная стойка',
           'Coworking': 'Коворкинг', 'Airport transfer': 'Трансфер из аэропорта', 'Lobby bar': 'Лобби-бар',
           'Kitchen': 'Кухня', 'Washing machine': 'Стиральная машина', 'Workspace': 'Рабочее место'},
}
ADDRESS = {
    'kk': {'ул. Шамши Калдаякова, 15': 'Шәмші Қалдаяқов көшесі, 15', 'ул. Туркестан, 14а': 'Түркістан көшесі, 14а', 'Астана': 'Астана'},
    'en': {'ул. Шамши Калдаякова, 15': '15 Shamshi Kaldayakov St.', 'ул. Туркестан, 14а': '14a Turkestan St.', 'Астана': 'Astana'},
}


def load_dict():
    src = open(os.path.join(ROOT, 'assets/js/i18n.js'), encoding='utf-8').read()
    out = {}
    for lang in ('ru', 'kk', 'en'):
        block = re.search(rf'^  {lang}: \{{(.*?)^  \}},', src, re.S | re.M).group(1)
        out[lang] = {k: v.replace("\\'", "'") for k, v in re.findall(r"^    '([\w.-]+)': '(.*)',$", block, re.M)}
    return out


def esc(text):
    return text.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


def translate_alt(alt, lang):
    out = alt
    for ru, tr in sorted(ALT[lang].items(), key=lambda kv: -len(kv[0])):
        out = out.replace(ru, tr)
    return out


def enrich_jsonld(page, ld, lang):
    """Дополняет разметку Hotel; для index — Organization."""
    url_prefix = BASE if lang == 'ru' else f'{BASE}{lang}/'
    if ld.get('@type') == 'Hotel':
        extra = HOTEL_EXTRA[page]
        ld['inLanguage'] = lang
        ld['hasMap'] = extra['map']
        ld['availableLanguage'] = ['ru', 'kk', 'en']
        ld['currenciesAccepted'] = 'KZT'
        ld['paymentAccepted'] = 'Cash, Credit Card'
        if 'numberOfRooms' in extra:
            ld['numberOfRooms'] = extra['numberOfRooms']
        names = AMENITY_NAMES.get(lang)
        ld['amenityFeature'] = [
            {'@type': 'LocationFeatureSpecification', 'name': names[a] if names else a, 'value': True}
            for a in extra['amenities']
        ]
        if lang != 'ru':
            addr = ld['address']
            addr['streetAddress'] = ADDRESS[lang].get(addr['streetAddress'], addr['streetAddress'])
            addr['addressLocality'] = ADDRESS[lang]['Астана']
    if lang != 'ru':
        ld['url'] = ld['url'].replace(BASE, url_prefix)
        if 'description' in ld and page in META:
            ld['description'] = META[page][lang][1]
    return ld


def build_page(page, lang, dicts):
    src = open(os.path.join(ROOT, f'{page}.html'), encoding='utf-8').read()
    d = dicts[lang]
    html = src

    # 1. тексты по data-i18n и атрибуты по data-i18n-attr
    def sub_text(m):
        key, rest, old = m.group(1), m.group(2), m.group(3)
        val = d.get(key)
        return f'data-i18n="{key}"{rest}>{esc(val) if val is not None else old}<'
    html = re.sub(r'data-i18n="([\w.-]+)"([^>]*)>([^<]*)<', sub_text, html)

    def sub_attr(m):
        tag = m.group(0)
        pairs = m.group(1).split(';')
        for pair in pairs:
            if ':' not in pair:
                continue
            attr, key = (x.strip() for x in pair.split(':', 1))
            val = d.get(key)
            if val is not None:
                tag = re.sub(rf'{attr}="[^"]*"', f'{attr}="{esc(val)}"', tag, count=1)
        return tag
    html = re.sub(r'<[^>]*data-i18n-attr="([^"]+)"[^>]*>', sub_attr, html)

    # 2. title, description, html lang, og
    title, desc = META[page][lang]
    html = re.sub(r'<title>.*?</title>', f'<title>{esc(title)}</title>', html, count=1)
    html = re.sub(r'<meta name="description" content="[^"]*">', f'<meta name="description" content="{esc(desc)}">', html, count=1)
    html = html.replace('<html lang="ru">', f'<html lang="{HTML_LANG[lang]}">', 1)
    html = re.sub(r'<meta property="og:title" content="[^"]*">', f'<meta property="og:title" content="{esc(title)}">', html, count=1)
    html = re.sub(r'<meta property="og:description" content="[^"]*">', f'<meta property="og:description" content="{esc(desc)}">', html, count=1)
    html = html.replace('<meta property="og:locale" content="ru_RU">', f'<meta property="og:locale" content="{OG_LOCALE[lang]}">', 1)

    # 3. canonical / og:url на свою папку
    page_url = f'{BASE}{lang}/' if page == 'index' else f'{BASE}{lang}/{page}.html'
    html = re.sub(r'<link rel="canonical" href="[^"]*">', f'<link rel="canonical" href="{page_url}">', html, count=1)
    html = re.sub(r'<meta property="og:url" content="[^"]*">', f'<meta property="og:url" content="{page_url}">', html, count=1)

    # 4. JSON-LD
    def sub_ld(m):
        ld = json.loads(m.group(1))
        ld = enrich_jsonld(page, ld, lang)
        return '<script type="application/ld+json">\n' + json.dumps(ld, ensure_ascii=False, indent=1) + '\n</script>'
    html = re.sub(r'<script type="application/ld\+json">(.*?)</script>', sub_ld, html, flags=re.S)

    # 5. служебные подписи и alt
    for ru, tr in CHROME.items():
        html = html.replace(ru, tr[lang])
    html = re.sub(r'alt="([^"]*)"', lambda m: f'alt="{esc(translate_alt(m.group(1), lang))}"', html)

    # 6. относительные пути: ресурсы — на уровень выше, страницы — внутри папки
    html = html.replace('href="assets/', 'href="../assets/').replace('src="assets/', 'src="../assets/')
    # ссылки на страницы остаются относительными (hotels.html → kk/hotels.html) — ничего не меняем

    # 7. активный язык в переключателе
    html = re.sub(r'<button type="button" data-lang="ru" class="is-active">', '<button type="button" data-lang="ru">', html)
    html = html.replace(f'<button type="button" data-lang="{lang}">', f'<button type="button" data-lang="{lang}" class="is-active">', 1)
    return html


def rewrite_hreflang(html, page):
    """Единый блок hreflang на всех версиях страницы."""
    suffix = '' if page == 'index' else f'{page}.html'
    links = (
        f'<link rel="alternate" hreflang="ru" href="{BASE}{suffix}">\n'
        f'<link rel="alternate" hreflang="kk" href="{BASE}kk/{suffix}">\n'
        f'<link rel="alternate" hreflang="en" href="{BASE}en/{suffix}">\n'
        f'<link rel="alternate" hreflang="x-default" href="{BASE}{suffix}">'
    )
    return re.sub(r'(<link rel="alternate" hreflang="[^"]*" href="[^"]*">\n?)+', links + '\n', html, count=1)


def main():
    dicts = load_dict()
    # hreflang и дополненный JSON-LD — и в русских исходниках
    for page in PAGES:
        path = os.path.join(ROOT, f'{page}.html')
        html = open(path, encoding='utf-8').read()
        html = rewrite_hreflang(html, page)
        html = re.sub(r'<script type="application/ld\+json">(.*?)</script>',
                      lambda m: '<script type="application/ld+json">\n' + json.dumps(enrich_jsonld(page, json.loads(m.group(1)), 'ru'), ensure_ascii=False, indent=1) + '\n</script>',
                      html, flags=re.S)
        open(path, 'w', encoding='utf-8').write(html)
    for lang in LANGS:
        os.makedirs(os.path.join(ROOT, lang), exist_ok=True)
        for page in PAGES:
            html = rewrite_hreflang(build_page(page, lang, dicts), page)
            open(os.path.join(ROOT, lang, f'{page}.html'), 'w', encoding='utf-8').write(html)
        print(f'{lang}/: {len(PAGES)} страниц')
    # sitemap со всеми версиями
    urls = []
    for page in PAGES:
        suffix = '' if page == 'index' else f'{page}.html'
        for prefix in ('', 'kk/', 'en/'):
            urls.append(f'  <url><loc>{BASE}{prefix}{suffix}</loc></url>')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n')
    print('sitemap.xml:', len(urls), 'адресов')


if __name__ == '__main__':
    sys.exit(main())
