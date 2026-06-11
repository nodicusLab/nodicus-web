/* nódicus — interacciones */
(function () {
  'use strict';

  /* ---------- Header: sombra/compactado al hacer scroll ---------- */
  var header = document.getElementById('header');
  var onScroll = function () {
    if (window.scrollY > 12) header.classList.add('scrolled');
    else header.classList.remove('scrolled');
  };
  onScroll();
  window.addEventListener('scroll', onScroll, { passive: true });

  /* ---------- Menú móvil ---------- */
  var burger = document.getElementById('burger');
  var nav = document.getElementById('nav');
  var setMenu = function (open) {
    nav.classList.toggle('open', open);
    burger.setAttribute('aria-expanded', String(open));
    burger.setAttribute('aria-label', open ? 'Cerrar menú' : 'Abrir menú');
    document.body.style.overflow = open ? 'hidden' : '';
  };
  burger.addEventListener('click', function () {
    setMenu(!nav.classList.contains('open'));
  });
  nav.querySelectorAll('a').forEach(function (a) {
    a.addEventListener('click', function () { setMenu(false); });
  });
  document.addEventListener('keydown', function (e) {
    if (e.key === 'Escape') setMenu(false);
  });

  /* ---------- Smooth scroll con compensación del header ---------- */
  document.querySelectorAll('a[href^="#"]').forEach(function (a) {
    a.addEventListener('click', function (e) {
      var id = a.getAttribute('href');
      if (id === '#' || id === '#top') {
        e.preventDefault();
        window.scrollTo({ top: 0, behavior: 'smooth' });
        return;
      }
      var target = document.querySelector(id);
      if (!target) return;
      e.preventDefault();
      var y = target.getBoundingClientRect().top + window.scrollY - 72;
      window.scrollTo({ top: y, behavior: 'smooth' });
    });
  });

  /* ---------- Reveal al hacer scroll (con fallbacks robustos) ---------- */
  var reveals = Array.prototype.slice.call(document.querySelectorAll('.reveal'));
  var show = function (el) { el.classList.add('is-in'); };
  var inView = function (el) {
    var r = el.getBoundingClientRect();
    var vh = window.innerHeight || document.documentElement.clientHeight;
    return r.top < vh * 0.95 && r.bottom > 0;
  };

  // 1) Revela de inmediato lo que ya está en pantalla (above-the-fold).
  var revealInView = function () {
    reveals = reveals.filter(function (el) {
      if (inView(el)) { show(el); return false; }
      return true;
    });
  };

  if ('IntersectionObserver' in window) {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (en) {
        if (en.isIntersecting) { show(en.target); io.unobserve(en.target); }
      });
    }, { threshold: 0.1, rootMargin: '0px 0px -6% 0px' });
    reveals.forEach(function (el) { io.observe(el); });
  }

  // 2) Pasada inmediata + en scroll (por si el observer no dispara en algún contexto).
  requestAnimationFrame(revealInView);
  window.addEventListener('scroll', revealInView, { passive: true });
  window.addEventListener('load', revealInView);

  // 3) Red de seguridad: nada se queda invisible.
  setTimeout(function () { reveals.forEach(show); }, 1600);

  // 4) Al volver a la pestaña / restaurar desde caché: asegura visibilidad.
  window.addEventListener('pageshow', function () { requestAnimationFrame(revealInView); });
  document.addEventListener('visibilitychange', function () {
    if (!document.hidden) revealInView();
  });

  /* ---------- Formulario de contacto (EmailJS) ---------- */
  var form = document.getElementById('contact-form');
  var feedback = document.getElementById('form-feedback');
  if (form) {
    // Credenciales de EmailJS de nódicus (la Public Key se inicializa en el <head>).
    var SERVICE_ID = 'service_vg6oefs';
    var TEMPLATE_ID = 'template_xty5ryd';

    var resetButton = function (btn, labelHTML) {
      btn.disabled = false;
      btn.innerHTML = labelHTML;
    };

    form.addEventListener('submit', function (e) {
      e.preventDefault();
      var btn = form.querySelector('.form-submit');
      var labelHTML = btn.innerHTML;

      // Validación mínima
      var ok = true;
      form.querySelectorAll('[required]').forEach(function (f) {
        if (!f.value.trim()) ok = false;
      });
      var email = form.querySelector('#email');
      if (email && email.value && !/^[^@\s]+@[^@\s]+\.[^@\s]+$/.test(email.value)) ok = false;

      feedback.hidden = false;
      if (!ok) {
        feedback.classList.add('is-error');
        feedback.textContent = 'Revisa los campos: faltan datos o el correo no es válido.';
        return;
      }

      feedback.classList.remove('is-error');
      btn.disabled = true;
      btn.innerHTML = 'Enviando…';

      // Salvaguarda: si EmailJS no cargó (red/bloqueador), no dejamos el formulario colgado.
      if (typeof emailjs === 'undefined') {
        feedback.classList.add('is-error');
        feedback.textContent = 'No se pudo cargar el envío. Escríbenos directamente a contacto@nodicus.com';
        resetButton(btn, labelHTML);
        return;
      }

      emailjs.sendForm(SERVICE_ID, TEMPLATE_ID, form).then(function () {
        // Éxito
        btn.innerHTML = '¡Enviado! ✓';
        feedback.classList.remove('is-error');
        feedback.textContent = 'Gracias por escribirnos. Te responderemos muy pronto.';
        form.reset();
        setTimeout(function () {
          resetButton(btn, labelHTML);
          feedback.hidden = true;
        }, 5000);
      }, function (err) {
        // Error
        resetButton(btn, labelHTML);
        feedback.classList.add('is-error');
        feedback.textContent = 'Hubo un error al enviar. Escríbenos directamente a contacto@nodicus.com';
        if (window.console && console.error) console.error('EmailJS Error:', err);
      });
    });
  }
})();
