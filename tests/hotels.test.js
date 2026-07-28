import { test, assert } from './harness.js';
import { HOTELS, EXTRAS, getHotel, getRoom } from '../assets/js/hotels.js';

test('в сети три отеля с уникальными id', () => {
  assert.equal(HOTELS.length, 3);
  const ids = HOTELS.map((h) => h.id);
  assert.deepEqual([...new Set(ids)].sort(), ['amina', 'botanic', 'cityline']);
});

test('минимальная цена отеля совпадает с самым дешёвым номером', () => {
  for (const hotel of HOTELS) {
    const min = Math.min(...hotel.rooms.map((r) => r.price));
    assert.equal(hotel.priceFrom, min, `${hotel.id}: priceFrom не совпадает`);
  }
});

test('у каждого отеля есть номер WhatsApp из 11 цифр', () => {
  for (const hotel of HOTELS) {
    assert.match(hotel.whatsapp, /^7\d{10}$/, `${hotel.id}: неверный номер`);
  }
});

test('getHotel и getRoom находят запись', () => {
  assert.equal(getHotel('amina').name, 'AMINA Hotel');
  assert.equal(getRoom('cityline', 'delux').area, 28);
  assert.equal(getHotel('нет-такого'), undefined);
});

test('у Botanic задана акция со сроками', () => {
  const promo = getHotel('botanic').promo;
  assert.equal(promo.discount, 0.15);
  assert.equal(promo.from, '2026-06-15');
  assert.equal(promo.to, '2026-08-31');
});

test('дополнительные услуги имеют цену и способ расчёта', () => {
  assert.ok(EXTRAS.length >= 3);
  for (const extra of EXTRAS) {
    assert.equal(typeof extra.price, 'number');
    assert.ok(['once', 'per-night', 'per-guest-night'].includes(extra.per));
  }
});
