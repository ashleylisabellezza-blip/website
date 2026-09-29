/* Bellezza & Co. - single external script.
   Builds the shared top bar / header / footer, runs the mobile nav,
   the hero fader and the back-to-top button. No jQuery, no plugins. */

(function () {
  'use strict';

  var SITE = {
    phone: '740-366-1604',
    tel: 'tel:+17403661604',
    address: '206 Deo Drive, Newark, Ohio 43055',
    hours: 'Mon-Tues: 9am-8pm | Wed: 12pm-8pm | Thurs: 9am-8pm | Fri: 9am-7pm | Sat: 8am-3pm',
    booking: 'https://login.meevo.com/bellezza/ob?locationId=103245',
    giftcards: 'https://na0.meevo.com/EgiftApp/home?tenantId=100947',
    ratings: 'https://na0.meevo.com/FiveStarRatingApp/five-star-rating?t=100947&l=103245',
    quiz: 'https://app.joinmya.com/bellezza',
    facebook: 'https://www.facebook.com/BellezzaSpaOnline',
    instagram: 'https://instagram.com/bellezza_newark',
    ios: 'https://apps.apple.com/us/app/bellezza-salon-day-spa/id1314312155',
    android: 'https://play.google.com/store/apps/details?id=com.webappclouds.bellezzaspa',
    mapQuery: '206 Deo Drive, Newark, OH 43055'
  };

  /* label, href, children */
  var NAV = [
    ['Home', 'index.html', []],
    ['Services', '#', [
      ['Brides', 'brides.html'],
      ['Salon', 'salon.html'],
      ['Tips and Toes', 'tips-and-toes.html'],
      ['Massages', 'massages.html'],
      ['Makeup and Eyes', 'makeup-and-eyes.html'],
      ['Facials', 'facials.html'],
      ['Hair Removal', 'hair-removal.html'],
      ['Spray Tans', 'spray-tans.html'],
      ['Men&#39;s Care', 'mens-care.html'],
      ['Slay Aesthetics', 'slay-aesthetics.html']
    ]],
    ['Specials', 'specials.html', []],
    ['Book Online', 'book-online.html', []],
    ['Products', 'products.html', []],
    ['Our Team', 'our-team.html', [
      ['Join Our Team', 'join-our-team.html'],
      ['Contact Us', 'contact-us.html']
    ]],
    ['Purchase', 'gift-cards.html', [
      ['Gift Cards', 'gift-cards.html'],
      ['Pick Up Orders', 'pick-up-orders.html']
    ]]
  ];

  var here = location.pathname.split('/').pop() || 'index.html';

  function navHtml() {
    var out = '<ul>';
    NAV.forEach(function (item) {
      var kids = item[2];
      var active = item[1] === here || kids.some(function (k) { return k[1] === here; });
      out += '<li class="' + (active ? 'is-active' : '') + '">';
      out += '<a href="' + item[1] + '">' + item[0] + '</a>';
      if (kids.length) {
        out += '<ul>';
        kids.forEach(function (k) {
          out += '<li><a href="' + k[1] + '">' + k[0] + '</a></li>';
        });
        out += '</ul>';
      }
      out += '</li>';
    });
    return out + '</ul>';
  }

  function topbarHtml() {
    return '<div class="topbar"><div class="wrap">' +
      '<span><b>HOURS:</b> ' + SITE.hours + '</span>' +
      '<span><b>ADDRESS:</b> ' + SITE.address + '</span>' +
      '</div></div>';
  }

  function headerHtml() {
    return '<header class="site-header"><div class="wrap">' +
      '<div class="header-utils">' +
        '<a class="call" href="' + SITE.tel + '">Click to call us ' + SITE.phone + '</a>' +
        '<span class="social">' +
          '<a href="' + SITE.facebook + '" aria-label="Facebook" target="_blank" rel="noopener">f</a>' +
          '<a href="' + SITE.instagram + '" aria-label="Instagram" target="_blank" rel="noopener">ig</a>' +
        '</span>' +
      '</div>' +
      '<a class="logo" href="index.html"><img src="assets/img/logo.png" alt="Bellezza and Co. Salon Spa Boutique, established 2009" width="340" height="120"></a>' +
      '<button class="nav-toggle" type="button" aria-expanded="false">Menu</button>' +
      '<nav class="nav" aria-label="Main">' + navHtml() + '</nav>' +
      '</div></header>';
  }

  function footerHtml() {
    var map = 'https://maps.google.com/maps?q=' + encodeURIComponent(SITE.mapQuery) + '&z=15&output=embed';
    return '<footer class="site-footer"><div class="wrap">' +
      '<div class="footer-grid">' +
        '<div>' +
          '<img class="footer-logo" src="assets/img/logo-mark.png" alt="Bellezza and Co." width="120" height="120">' +
          '<ul class="footer-list">' +
            '<li><a href="' + SITE.tel + '">1-' + SITE.phone + '</a></li>' +
            '<li>206 Deo Dr, Newark, OH 43055</li>' +
          '</ul>' +
        '</div>' +
        '<div><h4>Explore</h4><ul class="footer-list">' +
          '<li><a href="book-online.html">Book Online</a></li>' +
          '<li><a href="specials.html">Specials</a></li>' +
          '<li><a href="gift-cards.html">Gift Cards</a></li>' +
          '<li><a href="our-team.html">Our Team</a></li>' +
          '<li><a href="join-our-team.html">Join Our Team</a></li>' +
          '<li><a href="policies.html">Policies &amp; Guest Information</a></li>' +
        '</ul></div>' +
        '<div><h4>Contact</h4>' +
          /* TODO: point action= at your form provider, e.g.
             https://formspree.io/f/XXXXXXX  or Netlify Forms */
          '<form class="footer-form" action="https://formspree.io/f/REPLACE-ME" method="post">' +
            '<div class="field"><label for="f-name">Name</label><input id="f-name" name="name" type="text" required></div>' +
            '<div class="field"><label for="f-email">Email</label><input id="f-email" name="email" type="email" required></div>' +
            '<div class="field"><label for="f-msg">Message</label><textarea id="f-msg" name="message" rows="3" required></textarea></div>' +
            '<button class="btn" type="submit">Send</button>' +
          '</form>' +
        '</div>' +
        '<div><h4>Visit Us!</h4>' +
          '<iframe class="map-embed" src="' + map + '" title="Map to Bellezza and Co." loading="lazy" referrerpolicy="no-referrer-when-downgrade"></iframe>' +
        '</div>' +
      '</div>' +
      '<div class="footer-bottom">' +
        '<span>Copyright <span id="yr"></span> Bellezza Salon and Day Spa</span>' +
        '<span class="social">' +
          '<a href="' + SITE.facebook + '" aria-label="Facebook" target="_blank" rel="noopener">f</a>' +
          '<a href="' + SITE.instagram + '" aria-label="Instagram" target="_blank" rel="noopener">ig</a>' +
        '</span>' +
      '</div>' +
      '</div></footer>';
  }

  function fill(id, html) {
    var el = document.getElementById(id);
    if (el) el.outerHTML = html;
  }

  document.addEventListener('DOMContentLoaded', function () {
    fill('site-topbar', topbarHtml());
    fill('site-header', headerHtml());
    fill('site-footer', footerHtml());

    var yr = document.getElementById('yr');
    if (yr) yr.textContent = new Date().getFullYear();

    /* mobile nav */
    var nav = document.querySelector('.nav');
    var toggle = document.querySelector('.nav-toggle');
    if (toggle && nav) {
      toggle.addEventListener('click', function () {
        var open = nav.classList.toggle('is-open');
        toggle.setAttribute('aria-expanded', open ? 'true' : 'false');
      });
    }
    /* tap a parent item to open its submenu on touch screens */
    document.querySelectorAll('.nav > ul > li').forEach(function (li) {
      var link = li.querySelector('a');
      if (!li.querySelector('ul') || !link) return;
      link.addEventListener('click', function (e) {
        if (window.matchMedia('(max-width:760px)').matches) {
          e.preventDefault();
          li.classList.toggle('is-open');
        }
      });
    });

    /* hero fader (replaces Revolution Slider) */
    var slides = document.querySelectorAll('.hero-slide');
    if (slides.length > 1) {
      var i = 0, timer;
      var show = function (n) {
        slides[i].classList.remove('is-on');
        i = (n + slides.length) % slides.length;
        slides[i].classList.add('is-on');
      };
      var auto = function () { timer = setInterval(function () { show(i + 1); }, 7000); };
      var stop = function () { clearInterval(timer); auto(); };
      document.querySelectorAll('.hero-arrow').forEach(function (btn) {
        btn.addEventListener('click', function () {
          show(i + (btn.classList.contains('hero-arrow--next') ? 1 : -1));
          stop();
        });
      });
      auto();
    }

    /* team bio dialogs: <button data-bio="bio-id"> opens <dialog id="bio-id"> */
    document.querySelectorAll('[data-bio]').forEach(function (btn) {
      var dlg = document.getElementById(btn.getAttribute('data-bio'));
      if (!dlg || !dlg.showModal) return;
      btn.addEventListener('click', function () { dlg.showModal(); });
    });
    document.querySelectorAll('dialog.bio').forEach(function (dlg) {
      var close = dlg.querySelector('.bio-close');
      if (close) close.addEventListener('click', function () { dlg.close(); });
      /* click on the backdrop closes */
      dlg.addEventListener('click', function (e) { if (e.target === dlg) dlg.close(); });
    });

    /* jobs.html?position=Nail pre-selects that position */
    var pos = new URLSearchParams(location.search).get('position');
    if (pos) {
      document.querySelectorAll('input[name="position"]').forEach(function (r) {
        if (r.value === pos) r.checked = true;
      });
    }

    /* back to top */
    var top = document.querySelector('.to-top');
    if (top) top.addEventListener('click', function () { window.scrollTo({ top: 0, behavior: 'smooth' }); });
  });
})();
