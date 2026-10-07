import { getHotel, getRoom, EXTRAS } from './hotels.js';

const DAY = 24 * 60 * 60 * 1000;

export function countNights(checkIn, checkOut) {
  if (!checkIn || !checkOut) return 0;
  const from = Date.parse(`${checkIn}T00:00:00Z`);
  const to = Date.parse(`${checkOut}T00:00:00Z`);
  if (Number.isNaN(from) || Number.isNaN(to)) return 0;
  const nights = Math.round((to - from) / DAY);
  return nights > 0 ? nights : 0;
}

// Акция «длительное проживание»: скидка включается, когда ночей не меньше
// порога minNights. Акции по датам (from/to) тоже поддерживаются — если у
// отеля заданы обе границы, проверяется дата заезда.
function promoDiscount(hotel, checkIn, nights) {
  const promo = hotel?.promo;
  if (!promo) return 0;
  if (promo.minNights) return nights >= promo.minNights ? promo.discount : 0;
  if (promo.from && promo.to && checkIn) {
    return checkIn >= promo.from && checkIn <= promo.to ? promo.discount : 0;
  }
  return 0;
}

function extraCost(extra, { nights, guests, rooms }) {
  if (extra.per === 'once') return extra.price;
  if (extra.per === 'per-night') return extra.price * nights;
  return extra.price * nights * guests * rooms; // per-guest-night
}

export function calcTotal({ hotelId, roomId, checkIn, checkOut, rooms = 1, guests = 1, extras = [] }) {
  const hotel = getHotel(hotelId);
  const room = getRoom(hotelId, roomId);
  const nights = countNights(checkIn, checkOut);
  if (!hotel || !room || nights === 0) {
    return { nights: 0, base: 0, discount: 0, extrasTotal: 0, total: 0 };
  }
  const base = room.price * nights * rooms;
  const discount = Math.round(base * promoDiscount(hotel, checkIn, nights));
  const extrasTotal = extras
    .map((id) => EXTRAS.find((e) => e.id === id))
    .filter(Boolean)
    .reduce((sum, extra) => sum + extraCost(extra, { nights, guests, rooms }), 0);
  return { nights, base, discount, extrasTotal, total: base - discount + extrasTotal };
}

// Разряды числа разделяет неразрывный пробел: «15 000 ₸» не должно
// разрываться переносом строки. Браузеры отдают то U+00A0, то U+202F —
// приводим к одному виду.
export const formatPrice = (value) =>
  new Intl.NumberFormat('ru-RU').format(value).replace(/[\s  ]/g, ' ');

export const formatDate = (iso) => {
  if (!iso) return '';
  const [y, m, d] = iso.split('-');
  return `${d}.${m}.${y}`;
};

export function buildMessage(form) {
  const hotel = getHotel(form.hotelId);
  const room = getRoom(form.hotelId, form.roomId);
  const sum = calcTotal(form);
  const extraNames = form.extras?.length
    ? form.extras
        .map((id) => EXTRAS.find((e) => e.id === id)?.label ?? id)
        .join(', ')
    : '—';
  return [
    'Заявка на бронирование — AST Hotels',
    `Отель: ${hotel?.name ?? '—'}`,
    `Категория: ${room?.name ?? '—'}`,
    `Заезд: ${formatDate(form.checkIn)}`,
    `Выезд: ${formatDate(form.checkOut)}`,
    `Ночей: ${sum.nights}`,
    `Номеров: ${form.rooms}, гостей: ${form.guests}`,
    `Услуги: ${extraNames}`,
    `Итого: ${formatPrice(sum.total)} ₸`,
    `Гость: ${form.name}`,
    `Телефон: ${form.phone}`,
    ...(form.comment ? [`Пожелания: ${form.comment}`] : []),
  ].join('\n');
}

export function buildWhatsAppUrl(hotelId, message) {
  const hotel = getHotel(hotelId);
  return `https://wa.me/${hotel?.whatsapp ?? ''}?text=${encodeURIComponent(message)}`;
}
