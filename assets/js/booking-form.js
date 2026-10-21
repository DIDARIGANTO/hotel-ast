import { HOTELS, getHotel } from './hotels.js';
import { buildQuickMessage, buildWhatsAppUrl } from './booking.js';

// Быстрая заявка: отель, имя, дата заезда, число ночей, гостей, телефон,
// согласие. Стоимость гостю не считаем — её подтверждает отель в ответе.
const form = document.querySelector('#booking-form');
if (form) {
  const el = (name) => form.elements[name];
  const params = new URLSearchParams(location.search);

  el('hotel').innerHTML = HOTELS.map((h) => `<option value="${h.id}">${h.name}</option>`).join('');

  function readForm() {
    return {
      hotelId: el('hotel').value,
      checkIn: el('in').value,
      nights: Number(el('nights').value) || 0,
      guests: Number(el('guests').value) || 1,
      name: el('name').value.trim(),
      phone: el('phone').value.trim(),
    };
  }

  function setError(name, on) {
    el(name).closest('.field').classList.toggle('has-error', on);
  }

  function validate(data) {
    const errors = [];
    if (data.name.length < 2) errors.push('name');
    if (!data.checkIn) errors.push('in');
    if (data.nights < 1 || data.nights > 90) errors.push('nights');
    if ((data.phone.match(/\d/g) || []).length < 10) errors.push('phone');
    if (!el('consent')?.checked) errors.push('consent');
    ['name', 'in', 'nights', 'phone', 'consent'].forEach((n) => setError(n, errors.includes(n)));
    return errors;
  }

  form.addEventListener('input', () => ['name', 'in', 'nights', 'phone', 'consent'].forEach((n) => setError(n, false)));

  form.addEventListener('submit', (event) => {
    event.preventDefault();
    const data = readForm();
    const errors = validate(data);
    if (errors.length) {
      form.elements[errors[0]].focus();
      return;
    }
    const message = buildQuickMessage(data);
    const done = document.querySelector('.form-done');
    // Текст заявки показываем до попытки открыть вкладку: если сработал
    // блокировщик всплывающих окон, заявку можно скопировать вручную.
    done.querySelector('pre').textContent = message;
    done.classList.add('is-open');
    window.open(buildWhatsAppUrl(data.hotelId, message), '_blank', 'noopener');
    done.scrollIntoView({ behavior: 'smooth', block: 'center' });
  });

  // Сегодняшняя дата как минимум; предвыбор отеля и дат из ссылки
  el('in').min = new Date().toISOString().slice(0, 10);
  if (params.get('hotel') && getHotel(params.get('hotel'))) el('hotel').value = params.get('hotel');
  if (params.get('in')) el('in').value = params.get('in');
  if (params.get('nights')) el('nights').value = params.get('nights');
  if (params.get('guests')) el('guests').value = params.get('guests');
}
