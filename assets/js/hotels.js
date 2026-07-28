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
    priceFrom: 12000,
    priceConfirmed: true, // «от 12 000 ₸» и 21 номер — из Instagram отеля
    roomsTotal: 21,
    gis: 'https://2gis.kz/astana/firm/70000001060984202',
    instagram: 'https://www.instagram.com/amina.hotel/',
    hero: 'https://images.unsplash.com/photo-1765009434216-d232ecd3bbf4?auto=format&fit=crop&w=1920&q=80',
    amenities: ['wifi', 'parking', 'breakfast', 'reception24', 'coworking', 'transfer'],
    rooms: [
      {
        id: 'standard',
        name: 'Стандарт',
        area: 18,
        guests: 2,
        beds: '1 двуспальная кровать',
        price: 12000,
        img: 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=1200&q=80',
      },
      {
        id: 'twin',
        name: 'Комфорт Twin',
        area: 22,
        guests: 2,
        beds: '2 односпальные кровати',
        price: 19000,
        img: 'https://images.unsplash.com/photo-1590490360182-c33d57733427?auto=format&fit=crop&w=1200&q=80',
      },
      {
        id: 'junior',
        name: 'Полулюкс',
        area: 28,
        guests: 3,
        beds: '1 двуспальная + диван',
        price: 26000,
        img: 'https://images.unsplash.com/photo-1776763018821-8feeaeeee0a5?auto=format&fit=crop&w=1200&q=80',
      },
      {
        id: 'lux',
        name: 'Люкс',
        area: 38,
        guests: 4,
        beds: '1 двуспальная + гостиная',
        price: 38000,
        img: 'https://images.unsplash.com/photo-1582719478250-c89cae4dc85b?auto=format&fit=crop&w=1200&q=80',
      },
    ],
  },
  {
    id: 'cityline',
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
    hero: 'https://images.unsplash.com/photo-1771206331424-44b8ec9acdf4?auto=format&fit=crop&w=1920&q=80',
    amenities: ['wifi', 'parking', 'breakfast', 'reception24', 'bar', 'transfer'],
    // Категории и цены — из прайса в Instagram отеля (июль 2026).
    // Площади и спальные места по-прежнему предположение.
    rooms: [
      {
        id: 'economy',
        name: 'Стандарт эконом',
        area: 16,
        guests: 2,
        beds: '1 двуспальная кровать',
        price: 25000,
        img: 'https://images.unsplash.com/photo-1618773928121-c32242e63f39?auto=format&fit=crop&w=1200&q=80',
      },
      {
        id: 'standard',
        name: 'Стандарт',
        area: 20,
        guests: 2,
        beds: '1 двуспальная кровать',
        price: 28000,
        img: 'https://images.unsplash.com/photo-1590073242678-70ee3fc28e8e?auto=format&fit=crop&w=1200&q=80',
      },
      {
        id: 'twin',
        name: 'Твин',
        area: 22,
        guests: 2,
        beds: '2 односпальные кровати',
        price: 30000,
        img: 'https://images.unsplash.com/photo-1591088398332-8a7791972843?auto=format&fit=crop&w=1200&q=80',
      },
      {
        id: 'delux',
        name: 'DeLux',
        area: 28,
        guests: 3,
        beds: '1 двуспальная кровать и зона отдыха',
        price: 35000,
        img: 'https://images.unsplash.com/photo-1631049307264-da0ec9d70304?auto=format&fit=crop&w=1200&q=80',
      },
    ],
  },
  {
    id: 'botanic',
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
    priceFrom: 18000,
    priceConfirmed: false, // в 2ГИС цены нет — считается по нашим категориям
    gis: 'https://2gis.kz/astana/firm/70000001044528049',
    instagram: 'https://www.instagram.com/bg.apartments/',
    promo: { discount: 0.15, from: '2026-06-15', to: '2026-08-31' },
    hero: 'https://images.unsplash.com/photo-1522708323590-d24dbb6b0267?auto=format&fit=crop&w=1920&q=80',
    amenities: ['wifi', 'kitchen', 'parking', 'reception24', 'laundry', 'workspace'],
    rooms: [
      {
        id: 'studio',
        name: 'Студия',
        area: 32,
        guests: 2,
        beds: '1 двуспальная кровать, кухня',
        price: 18000,
        img: 'https://images.unsplash.com/photo-1502672260266-1c1ef2d93688?auto=format&fit=crop&w=1200&q=80',
      },
      {
        id: 'apt1',
        name: 'Апартамент, 1 спальня',
        area: 45,
        guests: 3,
        beds: 'спальня + гостиная с кухней',
        price: 24000,
        img: 'https://images.unsplash.com/photo-1560448204-e02f11c3d0e2?auto=format&fit=crop&w=1200&q=80',
      },
      {
        id: 'apt2',
        name: 'Апартамент, 2 спальни',
        area: 62,
        guests: 5,
        beds: '2 спальни + гостиная с кухней',
        price: 35000,
        img: 'https://images.unsplash.com/photo-1560185007-cde436f6a4d0?auto=format&fit=crop&w=1200&q=80',
      },
      {
        id: 'panoramic',
        name: 'Панорамный апартамент',
        area: 70,
        guests: 6,
        beds: '2 спальни, панорамные окна',
        price: 45000,
        img: 'https://images.unsplash.com/photo-1600607687939-ce8a6c25118c?auto=format&fit=crop&w=1200&q=80',
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

export const CLUB_LEVELS = [
  { id: 'silver', nights: 0, discount: 0.05 },
  { id: 'gold', nights: 10, discount: 0.1 },
  { id: 'platinum', nights: 30, discount: 0.15 },
];

export const getHotel = (id) => HOTELS.find((h) => h.id === id);

export const getRoom = (hotelId, roomId) =>
  getHotel(hotelId)?.rooms.find((r) => r.id === roomId);
