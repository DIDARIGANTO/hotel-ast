// Общее поведение всех страниц: меню, липкая шапка, появление блоков,
// аккордеоны, лайтбокс, фильтры. Подключается как <script type="module">.

const qs = (sel, root = document) => root.querySelector(sel);
const qsa = (sel, root = document) => [...root.querySelectorAll(sel)];

function initHeader() {
  const header = qs('.header');
  if (!header) return;
  const burger = qs('.burger', header);
  const nav = qs('.nav', header);

  if (!header.classList.contains('header--static')) {
    const onScroll = () => header.classList.toggle('is-solid', window.scrollY > 40);
    onScroll();
    window.addEventListener('scroll', onScroll, { passive: true });
  }

  burger?.addEventListener('click', () => {
    const open = nav.classList.toggle('is-open');
    burger.classList.toggle('is-open', open);
    burger.setAttribute('aria-expanded', String(open));
    document.body.style.overflow = open ? 'hidden' : '';
  });

  qsa('a', nav).forEach((link) =>
    link.addEventListener('click', () => {
      nav.classList.remove('is-open');
      burger?.classList.remove('is-open');
      document.body.style.overflow = '';
    })
  );

  // Закрытие мобильного меню по Escape
  document.addEventListener('keydown', (event) => {
    if (event.key !== 'Escape') return;
    if (!nav?.classList.contains('is-open')) return;
    nav.classList.remove('is-open');
    burger?.classList.remove('is-open');
    burger?.setAttribute('aria-expanded', 'false');
    document.body.style.overflow = '';
    burger?.focus();
  });

  // Подсветка текущего пункта меню
  const page = location.pathname.split('/').pop() || 'index.html';
  qsa('a', nav).forEach((link) => {
    if (link.getAttribute('href') === page) link.setAttribute('aria-current', 'page');
  });
}

// Наблюдатель общий на всю страницу: карточки отелей и номеров вставляются
// скриптом уже после старта, поэтому подписывать их нужно повторно.
let revealObserver = null;
let revealedAny = false;

export function observeReveal(root = document) {
  if (!revealObserver) return;
  qsa('.reveal', root).forEach((item) => revealObserver.observe(item));
}

// Показать всё сразу и больше не прятать.
function showEverything() {
  document.documentElement.classList.remove('js-anim');
  revealObserver?.disconnect();
  revealObserver = null;
}

function initReveal() {
  if (new URLSearchParams(location.search).has('noanim')) {
    document.body.classList.add('noanim');
    return;
  }
  if (!('IntersectionObserver' in window)) return;

  document.documentElement.classList.add('js-anim');
  revealObserver = new IntersectionObserver(
    (entries) => {
      entries.forEach((entry) => {
        if (!entry.isIntersecting) return;
        revealedAny = true;
        entry.target.classList.add('is-visible');
        revealObserver.unobserve(entry.target);
      });
    },
    { rootMargin: '0px 0px -10% 0px', threshold: 0.15 }
  );
  observeReveal();

  // Страховка: если наблюдатель молчит (старый браузер, режим экономии,
  // headless), контент не должен остаться невидимым навсегда.
  setTimeout(() => {
    if (!revealedAny) showEverything();
  }, 2000);
}

// Сегодняшняя дата в формате YYYY-MM-DD по местному времени.
const today = () => {
  const now = new Date();
  const month = String(now.getMonth() + 1).padStart(2, '0');
  const day = String(now.getDate()).padStart(2, '0');
  return `${now.getFullYear()}-${month}-${day}`;
};

function initSearchbar() {
  const form = qs('.searchbar');
  if (!form) return;

  const dates = qsa('input[type="date"]', form);
  dates.forEach((field) => field.setAttribute('min', today()));

  const checkIn = qs('input[name="in"]', form) || dates[0];
  const checkOut = qs('input[name="out"]', form) || dates[1];
  if (!checkIn || !checkOut) return;

  const markError = (on) => {
    checkOut.closest('label')?.classList.toggle('has-error', on);
  };

  [checkIn, checkOut].forEach((field) =>
    field.addEventListener('input', () => markError(false))
  );

  form.addEventListener('submit', (event) => {
    if (!checkIn.value || !checkOut.value) return;
    if (checkOut.value > checkIn.value) {
      markError(false);
      return;
    }
    event.preventDefault();
    markError(true);
    checkOut.focus();
  });
}

function initFilters() {
  const panel = document.querySelector('[data-filter]');
  if (!panel) return;
  const targets = () => [...document.querySelectorAll('[data-filter-target] > *')];
  const empty = document.querySelector('[data-filter-empty]');

  panel.addEventListener('click', (event) => {
    const btn = event.target.closest('button[data-value]');
    if (!btn) return;
    const { key } = btn.parentElement.dataset;
    [...btn.parentElement.querySelectorAll('button')].forEach((b) =>
      b.classList.toggle('is-active', b === btn)
    );
    panel.dataset[key] = btn.dataset.value;

    let visible = 0;
    targets().forEach((card) => {
      const okType = !panel.dataset.type || panel.dataset.type === 'all' || card.dataset.type === panel.dataset.type;
      const okDistrict = !panel.dataset.district || panel.dataset.district === 'all' || card.dataset.district === panel.dataset.district;
      const show = okType && okDistrict;
      card.hidden = !show;
      if (show) visible += 1;
    });
    if (empty) empty.hidden = visible > 0;
  });
}

function initAccordion() {
  document.querySelectorAll('.acc__q').forEach((btn) => {
    btn.addEventListener('click', () => {
      const item = btn.parentElement;
      const open = item.classList.toggle('is-open');
      btn.setAttribute('aria-expanded', String(open));
    });
  });
}

function initLightbox() {
  const images = [...document.querySelectorAll('[data-lightbox] img')];
  if (!images.length) return;

  const box = document.createElement('div');
  box.className = 'lightbox';
  box.innerHTML = `
    <button class="lightbox__close" type="button" aria-label="Закрыть">✕</button>
    <button class="lightbox__nav lightbox__nav--prev" type="button" aria-label="Назад">‹</button>
    <img alt="">
    <button class="lightbox__nav lightbox__nav--next" type="button" aria-label="Вперёд">›</button>`;
  document.body.append(box);

  const picture = box.querySelector('img');
  let index = 0;

  const show = (i) => {
    index = (i + images.length) % images.length;
    picture.src = images[index].dataset.full || images[index].src;
    picture.alt = images[index].alt;
  };
  const open = (i) => { show(i); box.classList.add('is-open'); document.body.style.overflow = 'hidden'; };
  const close = () => { box.classList.remove('is-open'); document.body.style.overflow = ''; };

  // Открывать галерею должно быть можно и с клавиатуры, поэтому картинка
  // становится настоящей кнопкой: роль, фокус и реакция на Enter и пробел.
  images.forEach((img, i) => {
    img.style.cursor = 'zoom-in';
    img.setAttribute('role', 'button');
    img.setAttribute('tabindex', '0');
    if (!img.getAttribute('alt')) img.setAttribute('alt', 'Фотография отеля');
    img.addEventListener('click', () => open(i));
    img.addEventListener('keydown', (event) => {
      if (event.key !== 'Enter' && event.key !== ' ') return;
      event.preventDefault();
      open(i);
    });
  });
  box.querySelector('.lightbox__close').addEventListener('click', close);
  box.querySelector('.lightbox__nav--prev').addEventListener('click', () => show(index - 1));
  box.querySelector('.lightbox__nav--next').addEventListener('click', () => show(index + 1));
  box.addEventListener('click', (e) => { if (e.target === box) close(); });
  document.addEventListener('keydown', (e) => {
    if (!box.classList.contains('is-open')) return;
    if (e.key === 'Escape') close();
    if (e.key === 'ArrowLeft') show(index - 1);
    if (e.key === 'ArrowRight') show(index + 1);
  });
}

export function initUI() {
  initHeader();
  initReveal();
  initSearchbar();
  initFilters();
  initAccordion();
  initLightbox();
}

document.addEventListener('DOMContentLoaded', initUI);
