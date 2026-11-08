// Контурные иконки 24×24 в цвете текста. Подключаются по атрибуту
// data-icon="имя": ui.js вставляет svg первым потомком элемента.
const P = (d) => `<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">${d}</svg>`;

export const ICONS = {
  wifi: P('<path d="M2.5 9a15 15 0 0 1 19 0"/><path d="M5.5 12.5a10.5 10.5 0 0 1 13 0"/><path d="M8.5 16a6 6 0 0 1 7 0"/><circle cx="12" cy="19.2" r="1" fill="currentColor"/>'),
  parking: P('<rect x="3.5" y="3.5" width="17" height="17" rx="3"/><path d="M9 17V7h3.8a3 3 0 0 1 0 6H9"/>'),
  clock: P('<circle cx="12" cy="12" r="8.5"/><path d="M12 7.5V12l3 2"/>'),
  kitchen: P('<path d="M7 3v6a2.5 2.5 0 0 0 5 0V3"/><path d="M9.5 3v18"/><path d="M17.5 3c-2.2 1.8-2.2 6.2 0 8v10"/>'),
  laptop: P('<rect x="4" y="5" width="16" height="11" rx="1.5"/><path d="M2.5 19h19"/>'),
  coffee: P('<path d="M4 9h12v5.5A4.5 4.5 0 0 1 11.5 19h-3A4.5 4.5 0 0 1 4 14.5V9z"/><path d="M16 11h1.5a2.25 2.25 0 0 1 0 4.5H16"/><path d="M8 3.5c0 1 .8 1.2.8 2.2M11.5 3.5c0 1 .8 1.2.8 2.2"/>'),
  bar: P('<path d="M5 4h14l-7 8z"/><path d="M12 12v7"/><path d="M8.5 19h7"/>'),
  car: P('<path d="M4 15v3h2.5v-1.5h11V18H20v-3l-1.6-4.5a2 2 0 0 0-1.9-1.3H7.5a2 2 0 0 0-1.9 1.3L4 15z"/><path d="M4 15h16"/><circle cx="8" cy="15" r=".9" fill="currentColor"/><circle cx="16" cy="15" r=".9" fill="currentColor"/>'),
  washer: P('<rect x="4" y="3.5" width="16" height="17" rx="2"/><circle cx="12" cy="13" r="4.5"/><path d="M8 6.5h.01M11 6.5h2"/>'),
  bed: P('<path d="M3 18v-7a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2v7"/><path d="M3 15h18"/><path d="M6 9V6.5h5V9M13 9V6.5h5V9"/>'),
  pin: P('<path d="M12 21s6.5-5.6 6.5-11a6.5 6.5 0 0 0-13 0c0 5.4 6.5 11 6.5 11z"/><circle cx="12" cy="10" r="2.3"/>'),
  phone: P('<path d="M6.5 3.5h3l1.5 4-2 1.5a10 10 0 0 0 5 5l1.5-2 4 1.5v3a2 2 0 0 1-2.2 2A15.5 15.5 0 0 1 4.5 5.7a2 2 0 0 1 2-2.2z"/>'),
  chat: P('<path d="M4 6.5A2.5 2.5 0 0 1 6.5 4h11A2.5 2.5 0 0 1 20 6.5v7a2.5 2.5 0 0 1-2.5 2.5H10l-4.5 3.5V16A2.5 2.5 0 0 1 4 13.5v-7z"/><path d="M8 9h8M8 12h5"/>'),
  percent: P('<path d="M18 6 6 18"/><circle cx="8" cy="8" r="2.2"/><circle cx="16" cy="16" r="2.2"/>'),
  card: P('<rect x="3" y="5.5" width="18" height="13" rx="2"/><path d="M3 10h18"/><path d="M7 14.5h4"/>'),
  check: P('<circle cx="12" cy="12" r="8.5"/><path d="m8.5 12.5 2.3 2.3 4.7-5"/>'),
};

export function mountIcons(root = document) {
  root.querySelectorAll('[data-icon]').forEach((el) => {
    if (el.querySelector(':scope > .ico')) return;
    const svg = ICONS[el.dataset.icon];
    if (!svg) return;
    el.insertAdjacentHTML('afterbegin', `<span class="ico">${svg}</span>`);
  });
}
