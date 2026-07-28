import { test, assert } from './harness.js';
import { countNights, calcTotal, buildMessage, buildWhatsAppUrl } from '../assets/js/booking.js';

test('countNights считает разницу в сутках', () => {
  assert.equal(countNights('2026-08-01', '2026-08-04'), 3);
  assert.equal(countNights('2026-08-01', '2026-08-02'), 1);
});

test('countNights возвращает 0 на некорректном интервале', () => {
  assert.equal(countNights('2026-08-05', '2026-08-05'), 0);
  assert.equal(countNights('2026-08-05', '2026-08-01'), 0);
  assert.equal(countNights('', '2026-08-01'), 0);
});

test('calcTotal умножает цену на ночи и количество номеров', () => {
  const res = calcTotal({
    hotelId: 'amina', roomId: 'standard',
    checkIn: '2026-09-01', checkOut: '2026-09-04',
    rooms: 2, guests: 2, extras: [],
  });
  assert.equal(res.nights, 3);
  assert.equal(res.base, 72000); // 12000 * 3 * 2
  assert.equal(res.discount, 0);
  assert.equal(res.total, 72000);
});

test('calcTotal считает услуги по своим правилам', () => {
  const res = calcTotal({
    hotelId: 'amina', roomId: 'standard',
    checkIn: '2026-09-01', checkOut: '2026-09-03',
    rooms: 1, guests: 2, extras: ['breakfast', 'transfer', 'parking'],
  });
  // завтрак 3500*2 гостя*2 ночи = 14000, трансфер 8000, парковка 2000*2 = 4000
  assert.equal(res.extrasTotal, 26000);
  assert.equal(res.total, 24000 + 26000);
});

test('акция Botanic снимает 15% с проживания в период действия', () => {
  const res = calcTotal({
    hotelId: 'botanic', roomId: 'studio',
    checkIn: '2026-07-10', checkOut: '2026-07-12',
    rooms: 1, guests: 2, extras: [],
  });
  assert.equal(res.base, 36000);
  assert.equal(res.discount, 5400);
  assert.equal(res.total, 30600);
});

test('акция не применяется вне срока и к услугам', () => {
  const res = calcTotal({
    hotelId: 'botanic', roomId: 'studio',
    checkIn: '2026-10-01', checkOut: '2026-10-03',
    rooms: 1, guests: 2, extras: ['transfer'],
  });
  assert.equal(res.discount, 0);
  assert.equal(res.total, 44000);
});

test('calcTotal возвращает нули при пустых датах', () => {
  const res = calcTotal({
    hotelId: 'amina', roomId: 'standard',
    checkIn: '', checkOut: '', rooms: 1, guests: 1, extras: [],
  });
  assert.equal(res.nights, 0);
  assert.equal(res.total, 0);
});

test('buildMessage содержит отель, категорию, даты и итог', () => {
  const msg = buildMessage({
    hotelId: 'cityline', roomId: 'economy',
    checkIn: '2026-09-01', checkOut: '2026-09-03',
    rooms: 1, guests: 2, extras: ['breakfast'],
    name: 'Дидар', phone: '+7 777 000 00 00',
  });
  assert.match(msg, /City Line Hotel/);
  assert.match(msg, /Стандарт эконом/);
  assert.match(msg, /01\.09\.2026/);
  assert.match(msg, /03\.09\.2026/);
  assert.match(msg, /Дидар/);
  // Разряды разделяет неразрывный пробел, но тесту важна сумма, а не её вид.
  assert.match(msg, /64[\s  ]000/); // 25000*2 + завтрак 3500*2*2
  assert.match(msg, /Услуги: Завтрак/); // услуги названы по-человечески
});

test('buildWhatsAppUrl ведёт на номер выбранного отеля', () => {
  const url = buildWhatsAppUrl('botanic', 'тест');
  assert.ok(url.startsWith('https://wa.me/77027771503?text='));
  assert.ok(url.includes(encodeURIComponent('тест')));
});
