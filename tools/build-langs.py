#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Собирает статические языковые версии сайта: kk/ и en/.

Русские страницы в корне — источник. Для каждого языка генератор
подставляет переводы из assets/js/i18n.js прямо в HTML (поисковик видит
готовый текст без JavaScript), переводит <title>, description, alt и
aria-label, переписывает относительные пути, canonical и hreflang,
дополняет JSON-LD. Запуск: python3 tools/build-langs.py — из корня проекта,
после любой правки русских страниц или словаря.
"""
import hashlib
import json
from urllib.parse import quote
import os
import re
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = 'https://hotel-astana.kz/'
LANGS = ('kk', 'en')
HTML_LANG = {'ru': 'ru', 'kk': 'kk', 'en': 'en'}
OG_LOCALE = {'ru': 'ru_RU', 'kk': 'kk_KZ', 'en': 'en_US'}
PAGES = ['index', 'hotels', 'amina', 'cityline', 'botanic',
         'booking', 'contacts', 'privacy']

# ── Заголовки и описания страниц ─────────────────────────────────────
META = {
    'index': {
        'kk': ('Астана қонақ үйлері — AMINA, City Line, Botanic Garden',
               'Астанадағы қонақ үйлер: оң жағалаудағы арзан смарт-қонақ үй AMINA мен бутик-қонақ үй City Line, сол жағалаудағы тәуліктік Botanic Garden апартаменттері. 15 000 ₸ бастап, WhatsApp арқылы брондау.'),
        'en': ('Hotels in Astana, Kazakhstan — AMINA, City Line, Botanic Garden',
               'Hotels in Astana: AMINA budget smart hotel and City Line boutique hotel on the right bank, Botanic Garden serviced apartments on the left bank. From 15 000 KZT per night, book on WhatsApp.'),
    },
    'hotels': {
        'kk': ('Астана қонақ үйлері: үш қонақ үйдің бағасы мен ауданын салыстыру',
               'Астана қонақ үйлерін салыстырыңыз: смарт-қонақ үй AMINA, бутик-қонақ үй City Line және Botanic Garden апартаменттері. Оң және сол жағалау, тәуліктік бағалар, 2ГИС рейтингтері.'),
        'en': ('Hotels in Astana: compare prices and districts of three hotels',
               'Compare hotels in Astana: AMINA smart hotel, City Line boutique hotel and Botanic Garden apartments. Right and left bank, prices per night, 2GIS ratings, direct booking.'),
    },
    'amina': {
        'kk': ('AMINA Hotel — Астанадағы арзан смарт-қонақ үй',
               'Астананың оң жағалауындағы арзан смарт-қонақ үй AMINA, Шәмші Қалдаяқов көшесі, 15, LRT жанында. Бір және екі орындық нөмірлер тәулігіне 15 000 ₸ бастап, есеп құжаттары беріледі.'),
        'en': ('AMINA Hotel Astana — budget smart hotel on the right bank',
               'AMINA Smart Hotel Astana: a budget hotel at 15 Shamshi Kaldayakov St. on the right bank, near the LRT and the Palace of Independence. Single and double rooms from 15 000 KZT per night.'),
    },
    'cityline': {
        'kk': ('City Line Hotel — Астанадағы бутик-қонақ үй',
               'Астананың оң жағалауындағы жаңа бутик-қонақ үй City Line, Шәмші Қалдаяқов көшесі, 15, LRT пен Тәуелсіздік сарайы жанында. Екі орындық нөмірлер тәулігіне 25 000 ₸ бастап.'),
        'en': ('City Line Hotel Astana — boutique hotel on the right bank',
               'City Line Hotel Astana: a new boutique hotel at 15 Shamshi Kaldayakov St. on the right bank, near the LRT and the Palace of Independence. Double and twin rooms from 25 000 KZT per night.'),
    },
    'botanic': {
        'kk': ('Botanic Garden Apartments — Астанадағы тәуліктік апартаменттер',
               'Астананың сол жағалауындағы тәуліктік және жарты тәуліктік апартаменттер, Түркістан көшесі, 14а, Ботаникалық бақ пен ЭКСПО жанында. Ас үйі бар апартаменттер 32 000 ₸ бастап.'),
        'en': ('Botanic Garden Apartments Astana — serviced apartments, left bank',
               'Botanic Garden Apartments Astana: serviced apartments with a kitchen for daily and half-day stays at 14a Turkestan St. on the left bank, near the Botanical Garden and EXPO. From 32 000 KZT.'),
    },
    'offers': {
        'kk': ('Арнайы ұсыныстар — Астана',
               'Үш қонақ үйдің ұсыныстары: үш қонақ үйдің кез келгенінде 3 түннен бастап тұрғанда 10% жеңілдік және агрегаторлар комиссиясынсыз тікелей брондау.'),
        'en': ('Special offers — Astana',
               'Offers from three hotels in Astana: 10% off stays of 3 nights or more at any of the three hotels and direct booking with no aggregator commission.'),
    },
    'booking': {
        'kk': ('Астанада қонақ үйді тікелей брондау — WhatsApp өтінімі',
               'Астанада қонақ үйді делдалсыз брондаңыз: AMINA, City Line немесе Botanic Garden. Аты-жөні, келу күні, түн мен қонақ саны — өтінім бірден қонақ үйдің WhatsApp-ына кетеді.'),
        'en': ('Book a hotel in Astana directly — request via WhatsApp',
               'Book a hotel in Astana with no intermediaries: AMINA, City Line or Botanic Garden. Name, arrival date, nights and guests — the request goes straight to the hotel on WhatsApp.'),
    },
    'contacts': {
        'kk': ('Астана қонақ үйлерінің байланыстары: AMINA, City Line, Botanic Garden',
               'AMINA Hotel, City Line Hotel және Botanic Garden Apartments мекенжайлары, телефондары мен WhatsApp: оң жағалау, Шәмші Қалдаяқов көшесі, 15 және сол жағалау, Түркістан көшесі, 14а.'),
        'en': ('Contacts of hotels in Astana: AMINA, City Line, Botanic Garden',
               'Addresses, phone numbers and WhatsApp of AMINA Hotel, City Line Hotel and Botanic Garden Apartments in Astana: right bank, 15 Shamshi Kaldayakov St., and left bank, 14a Turkestan St.'),
    },
    'privacy': {
        'kk': ('Дербес деректерді өңдеу саясаты',
               'Қонақ үйлер сайты қонақтардың қандай деректерін жинайды, не үшін, қайда береді және келісімді қалай қайтарып алуға болады.'),
        'en': ('Privacy policy',
               'What guest data the hotels website collects, why, where it is sent and how to withdraw consent.'),
    },
}

# ── Приветствие в ссылках WhatsApp (?text=…) ─────────────────────────
WA_TEXT = {
    'amina': {'ru': 'Здравствуйте! Я на сайте отеля AMINA Hotel, хочу уточнить наличие номеров.',
              'kk': 'Сәлеметсіз бе! Мен AMINA Hotel қонақ үйінің сайтындамын, бос нөмірлер бар-жоғын білгім келеді.',
              'en': 'Hello! I am on the AMINA Hotel website and would like to check room availability.'},
    'cityline': {'ru': 'Здравствуйте! Я на сайте отеля City Line Hotel, хочу уточнить наличие номеров.',
                 'kk': 'Сәлеметсіз бе! Мен City Line Hotel қонақ үйінің сайтындамын, бос нөмірлер бар-жоғын білгім келеді.',
                 'en': 'Hello! I am on the City Line Hotel website and would like to check room availability.'},
    'botanic': {'ru': 'Здравствуйте! Я на сайте Botanic Garden Apartments, хочу уточнить наличие апартаментов.',
                'kk': 'Сәлеметсіз бе! Мен Botanic Garden Apartments сайтындамын, бос апартаменттер бар-жоғын білгім келеді.',
                'en': 'Hello! I am on the Botanic Garden Apartments website and would like to check apartment availability.'},
}

# ── Служебные подписи вне словаря ────────────────────────────────────
CHROME = {
    'aria-label="Меню"': {'kk': 'aria-label="Мәзір"', 'en': 'aria-label="Menu"'},
    'aria-label="Выбор отеля"': {'kk': 'aria-label="Қонақ үй таңдау"', 'en': 'aria-label="Choose a hotel"'},
    'aria-label="Закрыть"': {'kk': 'aria-label="Жабу"', 'en': 'aria-label="Close"'},
    'aria-label="Предыдущее фото"': {'kk': 'aria-label="Алдыңғы фото"', 'en': 'aria-label="Previous photo"'},
    'aria-label="Следующее фото"': {'kk': 'aria-label="Келесі фото"', 'en': 'aria-label="Next photo"'},
    'title="Карта: ул. Шамши Калдаякова, 15"': {'kk': 'title="Карта: Шәмші Қалдаяқов көшесі, 15"', 'en': 'title="Map: 15 Shamshi Kaldayakov St."'},
    'title="Карта: ул. Туркестан, 14а"': {'kk': 'title="Карта: Түркістан көшесі, 14а"', 'en': 'title="Map: 14a Turkestan St."'},
    '&hl=ru&output=embed': {'kk': '&hl=kk&output=embed', 'en': '&hl=en&output=embed'},
}

# ── Alt-тексты фотографий ────────────────────────────────────────────
ALT = {
    'kk': {
        'Апартамент-студия с кухней и диваном в Botanic Garden Apartments': 'Botanic Garden Apartments: ас үйі мен диваны бар студия-апартамент',
        'Просторный апартамент с диваном в Botanic Garden Apartments, Астана': 'Botanic Garden Apartments: диваны бар кең апартамент, Астана',
        'Спальня апартамента с телевизором в Botanic Garden Apartments': 'Botanic Garden Apartments: теледидары бар апартамент жатын бөлмесі',
        'Гостиная апартамента с зелёным диваном в Botanic Garden Apartments': 'Botanic Garden Apartments: жасыл диваны бар апартамент қонақ бөлмесі',
        'Кухня апартамента с барной стойкой в Botanic Garden Apartments': 'Botanic Garden Apartments: бар үстелі бар апартамент ас үйі',
        'Чайник, вода и чай в апартаменте Botanic Garden Apartments': 'Botanic Garden Apartments: апартаменттегі шәйнек, су және шай',
        'Фасад': 'Қасбеті', 'Вывеска AMINA Hotel на фасаде здания': 'Ғимарат қасбетіндегі AMINA Hotel маңдайшасы',
        'Номер с окном в AMINA Hotel': 'AMINA Hotel-дегі терезесі бар нөмір', 'Общая кухня': 'Ортақ ас үй', 'Зона завтраков': 'Таңғы ас аймағы', 'Коридор': 'Дәліз',
        'Рабочее место в апартаменте': 'Апартаменттегі жұмыс орны', 'Стиральная машина в ванной апартамента': 'Апартамент жуынатын бөлмесіндегі кір жуғыш машина', 'с зелёной стеной': 'жасыл қабырғасы бар', 'Делюкс': 'Делюкс', 'Стойка регистрации': 'Тіркеу орны', 'Лаунж-зона': 'Лаунж аймағы',
        'Ванная комната': 'Жуынатын бөлме', 'Коворкинг и зона завтраков': 'Коворкинг және таңғы ас аймағы',
        'Холл': 'Холл', 'Номер категории': 'Санаттағы нөмір', 'Гостиная зона': 'Қонақ аймағы',
        'Кафе': 'Кафе', 'Студия': 'Студия', 'Гостиная апартамента': 'Апартамент қонақ бөлмесі',
        'Кухня': 'Ас үй', 'Спальня апартамента': 'Апартамент жатын бөлмесі',
        'Панорама Астаны на закате: высотные дома нового центра': 'Күн батқандағы Астана панорамасы: жаңа орталықтың биік үйлері',
        'с фиолетовыми креслами': 'күлгін креслолармен', 'с зоной отдыха': 'демалыс аймағымен',
        'с большим окном': 'үлкен терезесі бар', 'с зелёными диванами': 'жасыл дивандармен',
        'с обеденным столом': 'ас үстелімен', 'с барной стойкой': 'бар үстелімен',
        'с двумя спальнями': 'екі жатын бөлмелі', 'с диваном': 'диванымен',
        'Кухня апартамента': 'Апартамент ас үйі', 'Кухня студии': 'Студия ас үйі',
        'Ванная комната апартамента': 'Апартамент жуынатын бөлмесі', 'Спальня в апартаменте': 'Апартаменттегі жатын бөлме', 'Зона отдыха в номере категории': 'Санаттағы нөмірдің демалыс аймағы',
        'в Астане': 'Астанада', 'на улице Шамши Калдаякова, 15': 'Шәмші Қалдаяқов көшесі, 15', 'на Туркестан, 14а': 'Түркістан көшесі, 14а',
        'Спальня апартамента Делюкс в Botanic Garden Apartments': 'Botanic Garden Apartments: Делюкс апартаментінің жатын бөлмесі',
        'Номер категории Стандарт в City Line Hotel': 'City Line Hotel-дегі Стандарт санатындағы нөмір',
        'Гостиная зона в номере City Line Hotel': 'City Line Hotel нөміріндегі қонақ аймағы',
        'Стандарт': 'Стандарт', 'DeLux': 'DeLux', 'Логотип City Line Hotel на стойке регистрации': 'Тіркеу орнындағы City Line Hotel логотипі',
    },
    'en': {
        'Апартамент-студия с кухней и диваном в Botanic Garden Apartments': 'Studio apartment with a kitchen and a sofa at Botanic Garden Apartments',
        'Просторный апартамент с диваном в Botanic Garden Apartments, Астана': 'Spacious apartment with a sofa at Botanic Garden Apartments, Astana',
        'Спальня апартамента с телевизором в Botanic Garden Apartments': 'Apartment bedroom with a TV at Botanic Garden Apartments',
        'Гостиная апартамента с зелёным диваном в Botanic Garden Apartments': 'Apartment living room with a green sofa at Botanic Garden Apartments',
        'Кухня апартамента с барной стойкой в Botanic Garden Apartments': 'Apartment kitchen with a bar counter at Botanic Garden Apartments',
        'Чайник, вода и чай в апартаменте Botanic Garden Apartments': 'Kettle, water and tea in an apartment at Botanic Garden Apartments',
        'Фасад': 'Facade of', 'Вывеска AMINA Hotel на фасаде здания': 'AMINA Hotel sign on the building facade',
        'Номер с окном в AMINA Hotel': 'Room with a window at AMINA Hotel', 'Общая кухня': 'Shared kitchen at', 'Зона завтраков': 'Breakfast area at', 'Коридор': 'Corridor of',
        'Рабочее место в апартаменте': 'Workspace in the apartment', 'Стиральная машина в ванной апартамента': 'Washing machine in the apartment bathroom', 'с зелёной стеной': 'with a green wall', 'Делюкс': 'Deluxe', 'Стойка регистрации': 'Front desk of', 'Лаунж-зона': 'Lounge at',
        'Ванная комната': 'Bathroom at', 'Коворкинг и зона завтраков': 'Coworking and breakfast area at',
        'Холл': 'Lobby of', 'Номер категории': 'Room, category', 'Гостиная зона': 'Living area',
        'Кафе': 'Café at', 'Студия': 'Studio at', 'Гостиная апартамента': 'Apartment living room',
        'Кухня': 'Kitchen', 'Спальня апартамента': 'Apartment bedroom',
        'Панорама Астаны на закате: высотные дома нового центра': 'Astana skyline at sunset: high-rises of the new centre',
        'с фиолетовыми креслами': 'with purple armchairs', 'с зоной отдыха': 'with a seating area',
        'с большим окном': 'with a large window', 'с зелёными диванами': 'with green sofas',
        'с обеденным столом': 'with a dining table', 'с барной стойкой': 'with a bar counter',
        'с двумя спальнями': 'with two bedrooms', 'с диваном': 'with a sofa',
        'Кухня апартамента': 'Apartment kitchen', 'Кухня студии': 'Studio kitchen',
        'Ванная комната апартамента': 'Apartment bathroom', 'Спальня в апартаменте': 'Bedroom in an apartment', 'Зона отдыха в номере категории': 'Seating area in room, category',
        'в Астане': 'in Astana', 'на улице Шамши Калдаякова, 15': 'at 15 Shamshi Kaldayakov St.', 'на Туркестан, 14а': 'at 14a Turkestan St.',
        'номера': 'room', 'апартамента': 'apartment', 'Стандарт': 'Standard', 'DeLux': 'DeLux',
        'Логотип City Line Hotel на стойке регистрации': 'City Line Hotel logo at the front desk',
        'Спальня апартамента Делюкс в Botanic Garden Apartments': 'Deluxe apartment bedroom at Botanic Garden Apartments',
        'Номер категории Стандарт в City Line Hotel': 'Standard room at City Line Hotel',
        'Гостиная зона в номере City Line Hotel': 'Living area in a City Line Hotel room',
    },
}

# ── Дополнение JSON-LD Hotel ─────────────────────────────────────────
HOTEL_EXTRA = {
    'amina': {
        'numberOfRooms': 21,
        'amenities': ['Wi-Fi', 'Parking', '24-hour front desk', 'Shared kitchen', 'Workspace', 'Taxi on request'],
        'map': 'https://2gis.kz/astana/firm/70000001060984202',
    },
    'cityline': {
        'amenities': ['Wi-Fi', 'Parking', '24-hour front desk', 'Shared kitchen', 'Workspace', 'Taxi on request'],
        'map': 'https://2gis.kz/astana/firm/70000001105837375',
    },
    'botanic': {
        'amenities': ['Wi-Fi', 'Kitchen', 'Washing machine', '24-hour front desk', 'Workspace'],
        'map': 'https://2gis.kz/astana/firm/70000001044528049',
    },
}
HOTEL_SEO = {
 "amina": {
  "keywords": {
   "ru": "отель Астана, гостиница Астана, недорогой отель Астана, недорогая гостиница Астана, гостиница эконом Астана, смарт-отель Астана, smart-отель Астана, Smart Hotel Astana, Amina Hotel Astana, отель Амина Астана, гостиница на ночь Астана, отель на сутки Астана, отель в Астане цены, забронировать отель Астана, отель с закрывающими документами Астана, отель для командировок Астана, гостиница для туристов Астана, гостиница на правом берегу Астаны, гостиница возле ЛРТ Астана, отель возле Дворца Независимости Астана, отель возле Дворца Мира и Согласия Астана, одноместный номер Астана, двухместный номер Астана, гостиница с Wi-Fi Астана, гостиница на Шамши Калдаякова",
   "kk": "Астана қонақ үй, арзан қонақ үй Астана, смарт-қонақ үй Астана, AMINA Hotel Астана, LRT жанындағы қонақ үй, Тәуелсіздік сарайы жанындағы қонақ үй, Бейбітшілік және келісім сарайы жанындағы қонақ үй, іссапарға қонақ үй Астана, бір орындық нөмір Астана, екі орындық нөмір Астана, оң жағалаудағы қонақ үй",
   "en": "hotel Astana, budget hotel Astana, cheap hotel Astana, Smart Hotel Astana, Amina Hotel Astana, hotel near LRT Astana, hotel near Palace of Independence Astana, hotel near Palace of Peace and Reconciliation, business trip hotel Astana, single room Astana, double room Astana, right bank hotel Astana"
  },
  "alternateName": [
   "Амина",
   "Отель Амина",
   "Гостиница Амина",
   "AMINA Smart Hotel",
   "Amina Hotel Astana"
  ],
  "priceRange": {
   "ru": "15 000–23 000 ₸ за сутки",
   "kk": "тәулігіне 15 000–23 000 ₸",
   "en": "15,000–23,000 KZT per night"
  }
 },
 "cityline": {
  "keywords": {
   "ru": "бутик-отель Астана, boutique hotel Astana, boutique отель Астана, новый отель Астана, новая гостиница Астана, отель Астана, гостиница Астана, современный отель Астана, уютный отель Астана, комфортный отель Астана, City Line Hotel Astana, отель Сити Лайн Астана, гостиница Сити Лайн, отель для командировок Астана, гостиница для туристов Астана, гостиница на сутки Астана, забронировать отель Астана, двухместный номер Астана, гостиница на правом берегу Астаны, гостиница возле ЛРТ Астана, отель возле Дворца Независимости, отель возле Дворца Мира и Согласия, отель на Шамши Калдаякова",
   "kk": "бутик-қонақ үй Астана, жаңа қонақ үй Астана, City Line Hotel Астана, Астана қонақ үй, заманауи қонақ үй Астана, іссапарға қонақ үй Астана, LRT жанындағы қонақ үй, Тәуелсіздік сарайы жанындағы қонақ үй, екі орындық нөмір Астана, оң жағалаудағы қонақ үй",
   "en": "boutique hotel Astana, new hotel Astana, City Line Hotel Astana, modern hotel Astana, comfortable hotel Astana, business trip hotel Astana, hotel near LRT Astana, hotel near Palace of Independence Astana, double room Astana, right bank hotel Astana"
  },
  "alternateName": [
   "Сити Лайн",
   "Отель Сити Лайн",
   "Гостиница Сити Лайн",
   "City Line Boutique Hotel",
   "City Line Hotel Astana"
  ],
  "priceRange": {
   "ru": "25 000–35 000 ₸ за сутки",
   "kk": "тәулігіне 25 000–35 000 ₸",
   "en": "25,000–35,000 KZT per night"
  }
 },
 "botanic": {
  "keywords": {
   "ru": "апартаменты Астана, апартаменты посуточно Астана, апартаменты в Астане посуточно, апартаменты на полсуток Астана, гостиница на полсуток Астана, отель на полсуток Астана, апартаменты левый берег Астана, апартаменты в центре Астаны, снять апартаменты Астана, аренда квартиры посуточно Астана, квартира посуточно Астана, апартаменты Астана цена, гостиничные апартаменты Астана, апарт-отель Астана, апартаменты с кухней Астана, семейные апартаменты Астана, семейный отель Астана, отель для семьи Астана, семейный номер Астана, апартаменты на длительный срок Астана, отель с закрывающими документами Астана, жильё для командировки Астана, отель для командировок Астана, отель на левом берегу Астана, гостиница на левом берегу Астана, апартаменты возле Ботанического сада Астана, отель возле Экспо Астана, апартаменты возле Экспо Астана, студия посуточно Астана, апартаменты Делюкс Астана, апартаменты Люкс Астана, Botanic Garden Apartments Astana, Ботаник Гарден Астана",
   "kk": "апартаменттер Астана, тәуліктік апартаменттер Астана, жарты тәулікке апартамент Астана, тәулігіне пәтер Астана, ас үйі бар апартаменттер Астана, отбасылық апартаменттер Астана, сол жағалаудағы апартаменттер, Ботаникалық бақ жанындағы апартаменттер, ЭКСПО жанындағы апартаменттер, Botanic Garden Apartments Астана",
   "en": "apartments Astana, serviced apartments Astana, daily rent apartments Astana, half-day apartments Astana, apartments with kitchen Astana, family apartments Astana, apartments left bank Astana, apartments near Botanical Garden Astana, apartments near EXPO Astana, long stay apartments Astana, Botanic Garden Apartments Astana"
  },
  "alternateName": [
   "Ботаник Гарден",
   "Botanic Garden",
   "Апартаменты Ботаник Гарден",
   "Botanic Garden Apartments Astana"
  ],
  "priceRange": {
   "ru": "от 32 000 ₸ за сутки",
   "kk": "тәулігіне 32 000 ₸ бастап",
   "en": "from 32,000 KZT per night"
  }
 }
}

AMENITY_NAMES = {
    'kk': {'Wi-Fi': 'Wi-Fi', 'Parking': 'Тұрақ', 'Breakfast': 'Таңғы ас', '24-hour front desk': 'Тәулік бойы тіркеу',
           'Coworking': 'Коворкинг', 'Airport transfer': 'Әуежайдан трансфер', 'Lobby bar': 'Лобби-бар',
           'Kitchen': 'Ас үй', 'Shared kitchen': 'Ортақ ас үй', 'Washing machine': 'Кір жуғыш машина', 'Workspace': 'Жұмыс орны', 'Taxi on request': 'Такси шақыру'},
    'ru': {'Wi-Fi': 'Wi-Fi', 'Parking': 'Парковка', 'Breakfast': 'Завтрак', '24-hour front desk': 'Круглосуточная стойка',
           'Coworking': 'Коворкинг', 'Airport transfer': 'Трансфер из аэропорта', 'Lobby bar': 'Лобби-бар',
           'Kitchen': 'Кухня', 'Shared kitchen': 'Общая кухня', 'Washing machine': 'Стиральная машина', 'Workspace': 'Рабочее место', 'Taxi on request': 'Вызов такси'},
}
ADDRESS = {
    'kk': {'ул. Шамши Калдаякова, 15': 'Шәмші Қалдаяқов көшесі, 15', 'ул. Туркестан, 14а': 'Түркістан көшесі, 14а', 'Астана': 'Астана'},
    'en': {'ул. Шамши Калдаякова, 15': '15 Shamshi Kaldayakov St.', 'ул. Туркестан, 14а': '14a Turkestan St.', 'Астана': 'Astana'},
}


DICTS = {}  # заполняется в main(): словари ru/kk/en


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
        seo = HOTEL_SEO[page]
        ld['alternateName'] = seo['alternateName']
        ld['priceRange'] = seo['priceRange'][lang]
        ld['keywords'] = seo['keywords'][lang]
        # описание для нейросетей и карточек — первый абзац блока «Коротко» на странице
        fact = DICTS.get(lang, {}).get(f'seo.{page}.p1')
        if fact:
            ld['description'] = fact
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
        if 'description' in ld and page in META and ld.get('@type') != 'Hotel':
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
    for texts in WA_TEXT.values():
        html = html.replace(quote(texts['ru']), quote(texts[lang]))
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


def lastmod(page):
    """Дата последнего коммита страницы; при незакоммиченных правках — сегодня."""
    import datetime
    import subprocess
    today = datetime.date.today().isoformat()
    name = f'{page}.html'
    try:
        dirty = subprocess.run(['git', 'status', '--porcelain', '--', name, 'assets/js/i18n.js', 'assets/js/hotels.js'],
                               cwd=ROOT, capture_output=True, text=True).stdout.strip()
        if dirty:
            return today
        date = subprocess.run(['git', 'log', '-1', '--format=%cs', '--', name],
                              cwd=ROOT, capture_output=True, text=True).stdout.strip()
        return date or today
    except OSError:
        return today


# ── Версия стилей и скриптов в адресах ───────────────────────────────
RE_VER = re.compile(r'\?v=[0-9a-f]+')


def asset_version():
    """Хеш CSS и JS без самих меток ?v=: меняется при любой правке стилей или скриптов."""
    h = hashlib.sha1()
    for folder in ('assets/css', 'assets/js'):
        for name in sorted(os.listdir(os.path.join(ROOT, folder))):
            if name.endswith(('.css', '.js')):
                text = open(os.path.join(ROOT, folder, name), encoding='utf-8').read()
                h.update(name.encode() + RE_VER.sub('', text).encode())
    return h.hexdigest()[:8]


def stamp_assets():
    """Дописывает ?v=<версия> к style.css и модулям: в HTML и в import внутри JS.

    До 17.11.2026 хостинг отдавал CSS и JS с кэшем на 10 лет, и браузеры гостей
    держат старые копии. С новой меткой адрес другой — браузер скачивает файл
    заново. Во всех import одна и та же метка, иначе модуль загрузится дважды
    как два разных.
    """
    version = asset_version()
    re_html = re.compile(r'((?:href|src)="assets/(?:css|js)/[\w-]+\.(?:css|js))(?:\?v=[0-9a-f]+)?"')
    re_import = re.compile(r"(from '\./[\w-]+\.js)(?:\?v=[0-9a-f]+)?'")
    targets = [(name, re_html) for name in os.listdir(ROOT) if name.endswith('.html')]
    targets += [(os.path.join('assets/js', name), re_import)
                for name in os.listdir(os.path.join(ROOT, 'assets/js')) if name.endswith('.js')]
    for rel, pattern in sorted(targets):
        path = os.path.join(ROOT, rel)
        text = open(path, encoding='utf-8').read()
        stamped = pattern.sub(rf'\1?v={version}' + ('"' if pattern is re_html else "'"), text)
        if stamped != text:
            open(path, 'w', encoding='utf-8').write(stamped)
    print(f'версия стилей и скриптов: {version}')


def main():
    stamp_assets()
    dicts = load_dict()
    DICTS.update(dicts)
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
    # sitemap со всеми версиями; lastmod — дата последнего изменения русской страницы
    urls = []
    for page in PAGES:
        suffix = '' if page == 'index' else f'{page}.html'
        modified = lastmod(page)
        for prefix in ('', 'kk/', 'en/'):
            urls.append(f'  <url><loc>{BASE}{prefix}{suffix}</loc><lastmod>{modified}</lastmod></url>')
    open(os.path.join(ROOT, 'sitemap.xml'), 'w', encoding='utf-8').write(
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + '\n'.join(urls) + '\n</urlset>\n')
    print('sitemap.xml:', len(urls), 'адресов')


if __name__ == '__main__':
    sys.exit(main())
