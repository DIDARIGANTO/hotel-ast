// Единственный источник данных о сети. Правки цен и контактов — только здесь.
//
// Из 2ГИС подтверждены: адреса, индексы, телефоны, почта, рейтинги, число
// оценок и акция Botanic. Из Instagram отелей (июль 2026): AMINA — 21 номер,
// «от 12 000 ₸», коворкинг; City Line — прайс четырёх категорий (25/28/30/35
// тыс. ₸). Площади, спальные места и категории AMINA и Botanic —
// предположения, их список ждёт подтверждения заказчика в README.

export const HOTELS = [
  {
    id: 'amina',
    promo: { discount: 0.10, minNights: 3 },   // спецпредложение сети: от 3 ночей −10 %
    name: 'AMINA Hotel',
    page: 'amina.html',
    type: 'hotel',
    district: 'Сарайшык',
    address: 'ул. Шамши Калдаякова, 15',
    postal: 'Z01F3A2',
    phone: '+7 701 335 35 30',
    whatsapp: '77013353530',
    rating: 4.7,
    reviews: 436,
    priceFrom: 15000,
    priceConfirmed: true, // цены — из ТЗ заказчика (03.11.2026), 21 номер — из Instagram
    roomsTotal: 21,
    gis: 'https://2gis.kz/astana/firm/70000001060984202',
    instagram: 'https://www.instagram.com/amina.hotel/',
    hero: 'assets/img/amina/amina-hotel-astana-nomer-okno.jpg',
    amenities: ['wifi', 'parking', 'reception24', 'kitchen', 'coworking', 'transfer'],
    // Категории и цены — из ТЗ заказчика (03.11.2026). Фото номеров пока
    // из съёмки с Яндекс.Диска: для категорий без окна — те же снимки.
    rooms: [
      {
        id: 'single-nw',
        name: 'Одноместный эконом (без окна)',
        guests: 1,
        beds: '1 односпальная кровать',
        window: false,
        price: 15000,
        img: 'assets/img/amina/amina-hotel-astana-nomer-odnomestny.jpg',
        desc: 'Компактный и практичный номер для комфортного проживания одного гостя. Отличный вариант для коротких поездок и остановок в Астане.',
      },
      {
        id: 'double-nw',
        name: 'Стандарт двухместный (без окна)',
        guests: 2,
        beds: '1 двуспальная кровать',
        window: false,
        price: 18000,
        img: 'assets/img/amina/amina-hotel-astana-nomer-standart-bez-okna.jpg',
        desc: 'Компактный и функциональный номер для одного или двух гостей. Практичный вариант для комфортного проживания во время поездки в Астану.',
      },
      {
        id: 'double',
        name: 'Стандарт двухместный',
        guests: 2,
        beds: '1 двуспальная кровать',
        window: true,
        price: 21000,
        img: 'assets/img/amina/amina-hotel-astana-nomer-standart-dvuhmestny.jpg',
        desc: 'Светлый и уютный номер с естественным освещением, подходящий для размещения одного или двух гостей.',
      },
      {
        id: 'twin',
        name: 'Стандарт с двумя раздельными кроватями',
        guests: 2,
        beds: '2 односпальные кровати',
        window: true,
        price: 21000,
        img: 'assets/img/amina/amina-hotel-astana-nomer-tvin.jpg',
        desc: 'Удобный формат размещения для двух гостей с двумя односпальными кроватями.',
      },
      {
        id: 'plus',
        name: 'Стандарт Плюс',
        guests: 2,
        beds: '1 двуспальная кровать',
        window: true,
        price: 23000,
        img: 'assets/img/amina/amina-hotel-astana-nomer-plus.jpg',
        desc: 'Номер с увеличенной площадью для более комфортного размещения одного или двух гостей.',
      },
    ],
  },
  {
    id: 'cityline',
    promo: { discount: 0.10, minNights: 3 },   // спецпредложение сети: от 3 ночей −10 %
    name: 'City Line Hotel',
    page: 'cityline.html',
    type: 'boutique',
    district: 'Сарайшык',
    address: 'ул. Шамши Калдаякова, 15',
    postal: 'Z01F3A2',
    phone: '+7 775 959 00 88',
    whatsapp: '77759590088',
    rating: 4.9,
    reviews: 68,
    priceFrom: 25000,
    priceConfirmed: true,
    gis: 'https://2gis.kz/astana/firm/70000001105837375',
    instagram: 'https://www.instagram.com/city_line_hotel/',
    tour3d: true,
    hero: 'assets/img/cityline/city-line-hotel-astana-nomer-standart.jpg',
    amenities: ['wifi', 'parking', 'reception24', 'kitchen', 'workspace', 'taxi'],
    // Категории и цены — из прайса в Instagram отеля (июль 2026).
    // Площади и спальные места по-прежнему предположение.
    rooms: [
      {
        id: 'economy',
        name: 'Стандарт (без окна)',
        area: 16,
        guests: 2,
        beds: '1 двуспальная кровать',
        // «без окна» уже в названии — отдельной пометки в строке нет (ТЗ 20.11)
        price: 25000,
        img: 'assets/img/cityline/city-line-hotel-astana-nomer-standart-bez-okna.jpg',
        desc: 'Компактный и тихий номер с большой кроватью — удобный вариант для коротких деловых поездок.',
      },
      {
        id: 'standard',
        name: 'Стандарт двухместный',
        area: 20,
        guests: 2,
        beds: '1 двуспальная кровать',
        window: true,
        price: 28000,
        img: 'assets/img/cityline/city-line-hotel-astana-nomer-standart.jpg',
        desc: 'Светлый номер с полноценным рабочим местом — удобно для тех, кто совмещает поездку с работой.',
      },
      {
        id: 'twin',
        name: 'Стандарт с двумя раздельными кроватями',
        area: 22,
        guests: 2,
        beds: '2 односпальные кровати',
        window: true,
        price: 30000,
        img: 'assets/img/cityline/city-line-hotel-astana-nomer-tvin.jpg',
        desc: 'Светлый номер с рабочим столом — удобный вариант для коллег в командировке или друзей в совместной поездке.',
      },
      {
        id: 'delux',
        name: 'Делюкс',
        area: 28,
        guests: 2,
        beds: '1 двуспальная кровать',
        window: true,
        price: 35000,
        img: 'assets/img/cityline/city-line-hotel-astana-nomer-deluxe.jpg',
        desc: 'Самый просторный номер отеля. Подходит для длительного проживания и тех, кто ценит больше свободного места.',
      },
    ],
  },
  {
    id: 'botanic',
    promo: { discount: 0.10, minNights: 3 },   // спецпредложение сети: от 3 ночей −10 %
    name: 'Botanic Garden Apartments',
    page: 'botanic.html',
    type: 'apartments',
    district: 'Есиль',
    address: 'ул. Туркестан, 14а',
    postal: 'Z05T6K8',
    phone: '+7 702 777 15 03',
    phoneAlt: '+7 702 777 15 63',
    email: 'bq.apart2020@gmail.ru',
    whatsapp: '77027771503',
    rating: 4.6,
    reviews: 503,
    priceFrom: 32000,
    priceConfirmed: true, // категории и цены — от заказчика (07.11.2026)
    gis: 'https://2gis.kz/astana/firm/70000001044528049',
    instagram: 'https://www.instagram.com/bg.apartments/',
    hero: 'assets/img/botanic/botanic-garden-astana-gostinaya-divan.jpg',
    amenities: ['wifi', 'kitchen', 'reception24', 'laundry', 'workspace'],
    rooms: [
      {
        id: 'standard',
        name: 'Стандарт',
        guests: 2,
        beds: '1 двуспальная кровать, кухня',
        price: 32000,
        img: 'assets/img/botanic/botanic-garden-astana-nomer-standart.jpg',
        desc: 'Уютный апартамент с кухней и всем необходимым для самостоятельного проживания.',
      },
      {
        id: 'delux',
        name: 'Делюкс',
        guests: 2,
        beds: '1 двуспальная кровать, диван, кухня',
        price: 34000,
        img: 'assets/img/botanic/botanic-garden-astana-nomer-deluxe.jpg',
        desc: 'Просторнее стандарта: зона отдыха с диваном, кухня и рабочее место.',
      },
      {
        id: 'lux',
        name: 'Люкс',
        guests: 3,
        beds: 'спальня и гостиная с кухней',
        price: 36000,
        img: 'assets/img/botanic/botanic-garden-astana-nomer-lux.jpg',
        desc: 'Отдельная спальня и гостиная с кухней — для долгих поездок и семейного отдыха.',
      },
      {
        id: 'family',
        name: 'Семейный',
        guests: 4,
        beds: 'до 4 спальных мест, кухня',
        price: 36000,
        img: 'assets/img/botanic/botanic-garden-astana-nomer-semeyny-dve-krovati.jpg',
        desc: 'До четырёх спальных мест, кухня и гостиная — для семьи с детьми или компании.',
      },
    ],
  },
];

// per: once — разово за бронь, per-night — за ночь, per-guest-night — за гостя за ночь
export const EXTRAS = [
  { id: 'breakfast', label: 'Завтрак', price: 3500, per: 'per-guest-night' },
  { id: 'transfer', label: 'Трансфер от аэропорта', price: 8000, per: 'once' },
  { id: 'parking', label: 'Парковка', price: 2000, per: 'per-night' },
  { id: 'latecheckout', label: 'Поздний выезд', price: 5000, per: 'once' },
];


export const getHotel = (id) => HOTELS.find((h) => h.id === id);

export const getRoom = (hotelId, roomId) =>
  getHotel(hotelId)?.rooms.find((r) => r.id === roomId);
