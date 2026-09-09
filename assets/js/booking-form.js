import { HOTELS, EXTRAS, getHotel, getRoom } from './hotels.js';
import { calcTotal, buildMessage, buildWhatsAppUrl, formatPrice } from './booking.js';

const form = document.querySelector('#booking-form');
if (form) {
  const el = (name) => form.elements[name];
  const params = new URLSearchParams(location.search);
  const summary = (key) => document.querySelector(`[data-sum="${key}"]`);

  // Отели в select
  el('hotel').innerHTML = HOTELS.map((h) => `<option value="${h.id}">${h.name}</option>`).join('');

  function fillRooms(preferred) {
    const hotel = getHotel(el('hotel').value);
    // Что стараемся сохранить: категорию из ссылки либо выбранную до смены отеля.
    const wanted = preferred || el('room').value;
    el('room').innerHTML = hotel.rooms
      .map((r) => `<option value="${r.id}">${r.name} · ${formatPrice(r.price)} ₸</option>`)
      .join('');
    // Если такой категории у нового отеля нет — берём первую доступную.
    const kept = hotel.rooms.find((r) => r.id === wanted);
    el('room').value = kept ? kept.id : hotel.rooms[0].id;
  }

  // Вместимость выбранной категории с учётом количества номеров.
  function capacity() {
    const room = getRoom(el('hotel').value, el('room').value);
    const rooms = Number(el('rooms').value) || 1;
    return room ? room.guests * rooms : 1;
  }

  // Гостей не может быть больше вместимости: лишнее число прижимается
  // к максимуму, под полем показывается подсказка.
  function clampGuests() {
    const max = capacity();
    el('guests').max = String(max);
    const asked = Number(el('guests').value) || 1;
    const over = asked > max;
    if (over) el('guests').value = String(max);
    setError('guests', over);
  }

  function readForm() {
    return {
      hotelId: el('hotel').value,
      roomId: el('room').value,
      checkIn: el('in').value,
      checkOut: el('out').value,
      rooms: Number(el('rooms').value) || 1,
      guests: Number(el('guests').value) || 1,
      extras: EXTRAS.map((e) => e.id).filter((id) => form.querySelector(`[name="extra-${id}"]`)?.checked),
      name: el('name').value.trim(),
      phone: el('phone').value.trim(),
      comment: el('comment')?.value.trim() ?? '',
    };
  }

  function update() {
    clampGuests();
    const sum = calcTotal(readForm());
    summary('nights').textContent = sum.nights;
    summary('base').textContent = `${formatPrice(sum.base)} ₸`;
    summary('discount').textContent = sum.discount ? `−${formatPrice(sum.discount)} ₸` : '—';
    summary('extras').textContent = `${formatPrice(sum.extrasTotal)} ₸`;
    summary('total').textContent = `${formatPrice(sum.total)} ₸`;
    summary('discount').closest('.summary__row').hidden = sum.discount === 0;
  }

  function setError(name, on) {
    el(name).closest('.field').classList.toggle('has-error', on);
  }

  function validate(data) {
    const errors = [];
    if (!data.checkIn) errors.push('in');
    if (!data.checkOut || calcTotal(data).nights === 0) errors.push('out');
    if (data.name.length < 2) errors.push('name');
    if ((data.phone.match(/\d/g) || []).length < 10) errors.push('phone');
    if (!el('consent')?.checked) errors.push('consent');
    ['in', 'out', 'name', 'phone', 'consent'].forEach((n) => setError(n, errors.includes(n)));
    return errors;
  }

  el('hotel').addEventListener('change', () => { fillRooms(); update(); });
  form.addEventListener('input', update);
  form.addEventListener('change', update);

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    clampGuests();
    const data = readForm();
    const errors = validate(data);
    if (errors.length) {
      form.elements[errors[0]].focus();
      return;
    }
    const message = buildMessage(data);
    const done = document.querySelector('.form-done');
    // Блок с текстом заявки раскрывается до попытки открыть вкладку: если
    // сработал блокировщик всплывающих окон и window.open вернул null,
    // заявку всё равно можно скопировать вручную.
    done.querySelector('pre').textContent = message;
    done.classList.add('is-open');
    window.open(buildWhatsAppUrl(data.hotelId, message), '_blank', 'noopener');
    done.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });

  // Инициализация: сегодняшняя дата как минимум, предвыбор из ссылки
  const today = new Date().toISOString().slice(0, 10);
  el('in').min = today;
  el('out').min = today;
  if (params.get('hotel') && getHotel(params.get('hotel'))) el('hotel').value = params.get('hotel');
  fillRooms(params.get('room'));
  if (params.get('in')) el('in').value = params.get('in');
  if (params.get('out')) el('out').value = params.get('out');
  if (params.get('guests')) el('guests').value = params.get('guests');
  update();
}
