// Рендер карточек отелей и номеров из данных сети.
// Все подписи идут через словарь: карточки собираются скриптом, поэтому
// applyLang их не увидит — перевод подставляется здесь и обновляется
// по событию langchange.

import { HOTELS, getHotel } from './hotels.js';
import { formatPrice } from './booking.js';
import { translate, currentLang } from './i18n.js';
import { observeReveal } from './ui.js';

const t = (key, lang, fallback) => {
  const value = translate(key, lang);
  return value === key ? fallback : value;
};

// Порядок слов в языках разный: по-русски «от 15 000 ₸», по-казахски
// «15 000 ₸ бастап». Поэтому подписи — шаблоны с подстановкой, а не склейка.
const fmt = (template, vars) =>
  template.replace(/\{(\w+)\}/g, (_, name) => vars[name] ?? '');

// «436 оценок», но «503 оценки» — в русском форма зависит от числа.
function reviewsLabel(count, lang) {
  if (lang === 'ru') {
    const tail = count % 100;
    const last = count % 10;
    let form = 'оценок';
    if (tail < 11 || tail > 14) {
      if (last === 1) form = 'оценка';
      else if (last >= 2 && last <= 4) form = 'оценки';
    }
    return `${count} ${form}`;
  }
  return fmt(t('pages.reviews', lang, '{n} оценок'), { n: count });
}

const currency = (lang) => t('pages.currency', lang, '₸');

const priceFrom = (value, lang) =>
  fmt(t('pages.priceFrom', lang, 'от {sum}'), {
    sum: `${formatPrice(value)} ${currency(lang)}`,
  });

const priceNight = (value, lang) =>
  fmt(t('pages.priceNight', lang, 'от {sum} за ночь'), {
    sum: `${formatPrice(value)} ${currency(lang)}`,
  });

const districtLabel = (hotel, lang) =>
  t(`district.${hotel.district}`, lang, hotel.district);

const addressLabel = (hotel, lang) =>
  t(`address.${hotel.id}`, lang, hotel.address);

const roomName = (hotel, room, lang) =>
  t(`room.${hotel.id}.${room.id}`, lang, room.name);

const roomBeds = (hotel, room, lang) =>
  t(`beds.${hotel.id}.${room.id}`, lang, room.beds);

export function hotelCard(hotel, lang = currentLang()) {
  const name = roomNameSafe(hotel.name);
  return `
    <article class="card reveal" data-type="${hotel.type}" data-district="${hotel.district}" data-price="${hotel.priceFrom}">
      <div class="card__media">
        <img src="${hotel.hero.replace(/w=\d+/, 'w=900')}" alt="${name}" loading="lazy">
        <span class="card__badge">${t(`pages.type.${hotel.type}`, lang, hotel.type)}</span>
      </div>
      <div class="card__body">
        <span class="rating"><span class="rating__star">★</span>${hotel.rating}
          <span class="rating__count">${reviewsLabel(hotel.reviews, lang)}</span></span>
        <h3>${name}</h3>
        <p class="card__meta">${districtLabel(hotel, lang)} · ${addressLabel(hotel, lang)}</p>
        <p class="card__price">${priceFrom(hotel.priceFrom, lang)}</p>
        <p><a class="btn btn--dark" href="${hotel.page}">${t('pages.more', lang, 'Подробнее')}</a></p>
      </div>
    </article>`;
}

export function roomCard(hotel, room, lang = currentLang()) {
  const name = roomNameSafe(roomName(hotel, room, lang));
  return `
    <article class="card reveal">
      <div class="card__media"><img src="${room.img}" alt="${name}" loading="lazy"></div>
      <div class="card__body">
        <h3>${name}</h3>
        <p class="card__meta">${fmt(t('pages.roomMeta', lang, '{area} м² · до {guests} гостей · {beds}'), {
          area: room.area,
          guests: room.guests,
          beds: roomBeds(hotel, room, lang),
        })}</p>
        <p class="card__price">${priceNight(room.price, lang)}</p>
        <p><a class="btn btn--gold" href="booking.html?hotel=${hotel.id}&room=${room.id}">${t('pages.book', lang, 'Забронировать')}</a></p>
      </div>
    </article>`;
}

// Данные приходят из своего же файла, но экранирование дешевле, чем доверие.
function roomNameSafe(value) {
  return String(value).replace(/[<>&"]/g, (ch) =>
    ({ '<': '&lt;', '>': '&gt;', '&': '&amp;', '"': '&quot;' })[ch]
  );
}

export function renderHotels(selector = '[data-hotels]', lang = currentLang()) {
  const host = document.querySelector(selector);
  if (!host) return;
  host.innerHTML = HOTELS.map((hotel) => hotelCard(hotel, lang)).join('');
  observeReveal(host);
}

export function renderRooms(hotelId, selector = '[data-rooms]', lang = currentLang()) {
  const host = document.querySelector(selector);
  const hotel = getHotel(hotelId);
  if (!host || !hotel) return;
  host.innerHTML = hotel.rooms.map((room) => roomCard(hotel, room, lang)).join('');
  observeReveal(host);
}

// Таблица сравнения на hotels.html: цифры берутся из данных, чтобы правка
// цены в hotels.js не расходилась с версткой. Без JS в ячейках остаётся
// значение, написанное в разметке.
export function renderCompare(lang = currentLang()) {
  document.querySelectorAll('[data-cell][data-hotel]').forEach((cell) => {
    const hotel = getHotel(cell.dataset.hotel);
    if (!hotel) return;
    // Цену «от» показываем только там, где её подтверждает карточка 2ГИС:
    // у Botanic она выведена из наших же категорий и фактом не является.
    if (cell.dataset.cell === 'price') {
      cell.textContent = hotel.priceConfirmed
        ? priceFrom(hotel.priceFrom, lang)
        : t('hotels.compare.tbd', lang, 'уточняется');
    }
    if (cell.dataset.cell === 'rating') cell.textContent = `${hotel.rating} · ${reviewsLabel(hotel.reviews, lang)}`;
  });
}

function renderAll(lang = currentLang()) {
  renderCompare(lang);
  renderHotels('[data-hotels]', lang);
  const host = document.querySelector('[data-rooms]');
  if (host?.dataset.rooms) renderRooms(host.dataset.rooms, '[data-rooms]', lang);
}

document.addEventListener('DOMContentLoaded', () => renderAll());
document.addEventListener('langchange', (event) => renderAll(event.detail));
