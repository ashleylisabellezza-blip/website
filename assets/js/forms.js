/* Bellezza & Co. — form validation and submission (Netlify Forms).
   Loaded only on pages with forms. Without JS, forms still POST normally. */
(function () {
  'use strict';
  var doc = document;

  function label(field) {
    var l = field.id && doc.querySelector('label[for="' + field.id + '"]');
    if (l) return l.textContent.replace(/\(optional\)/i, '').trim();
    var fs = field.closest('fieldset');
    var lg = fs && fs.querySelector('legend');
    return lg ? lg.textContent.trim() : field.name;
  }

  function message(field) {
    var v = field.validity;
    if (v.valueMissing) {
      var l = label(field);
      if (field.type === 'radio' || field.type === 'checkbox') return 'Choose an option for ' + l.toLowerCase().replace(/\?$/, '') + '.';
      if (field.type === 'file') return 'Attach ' + l.toLowerCase().replace(/^attach /, '') + '.';
      if (/\?$/.test(l)) return 'Answer “' + l + '”';
      return 'Enter your ' + l.toLowerCase().replace(/^your /, '') + '.';
    }
    if (v.typeMismatch && field.type === 'email') return 'Enter an email address like name@example.com.';
    if (v.patternMismatch || v.typeMismatch) return 'Check the format of ' + label(field).toLowerCase() + '.';
    if (v.badInput) return field.type === 'number' ? 'Enter ' + label(field).toLowerCase() + ' as a number.' : 'Check the format of ' + label(field).toLowerCase() + '.';
    if (v.rangeUnderflow) return 'Enter ' + field.min + ' or more for ' + label(field).toLowerCase() + '.';
    if (v.rangeOverflow) return 'Enter ' + field.max + ' or less for ' + label(field).toLowerCase() + '.';
    if (v.stepMismatch) return 'Enter a whole number for ' + label(field).toLowerCase() + '.';
    if (field.type === 'file' && field.files[0] && field.dataset.maxMb && field.files[0].size > field.dataset.maxMb * 1048576) {
      return 'Choose a file smaller than ' + field.dataset.maxMb + ' MB.';
    }
    return '';
  }

  function errorId(field) { return (field.type === 'radio' ? field.name : (field.id || field.name)) + '-error'; }

  function showError(field, text) {
    var host = field.closest('.field, .fieldset');
    var id = errorId(field);
    var existing = doc.getElementById(id);
    var group = field.type === 'radio' ? host.querySelectorAll('input[name="' + field.name + '"]') : [field];
    if (!text) {
      if (existing) existing.remove();
      Array.prototype.forEach.call(group, function (f) { f.removeAttribute('aria-invalid'); });
      return;
    }
    if (!existing) {
      existing = doc.createElement('p');
      existing.className = 'field-error';
      existing.id = id;
      host.appendChild(existing);
    }
    existing.textContent = 'Error: ' + text;
    Array.prototype.forEach.call(group, function (f) {
      f.setAttribute('aria-invalid', 'true');
      var d = (f.getAttribute('aria-describedby') || '').split(' ').filter(Boolean);
      if (d.indexOf(id) < 0) { d.push(id); f.setAttribute('aria-describedby', d.join(' ')); }
    });
  }

  function check(field) {
    if (field.type === 'file' && field.files && field.files[0] && field.dataset.maxMb && field.files[0].size > field.dataset.maxMb * 1048576) {
      field.setCustomValidity('too big');
    } else if (field.type === 'file') field.setCustomValidity('');
    var text = field.checkValidity() ? '' : message(field) || 'Check ' + label(field).toLowerCase() + '.';
    showError(field, text);
    return !text;
  }

  function init(form) {
    form.noValidate = true;
    var fields = Array.prototype.filter.call(form.elements, function (f) {
      return f.name && f.type !== 'hidden' && f.type !== 'submit' && !f.closest('[hidden]');
    });
    fields.forEach(function (f) {
      var choice = f.type === 'radio' || f.type === 'checkbox' || f.type === 'file';
      f.addEventListener(choice ? 'change' : 'blur', function () { if (choice || f.value || f.getAttribute('aria-invalid')) check(f); });
    });

    form.addEventListener('submit', function (e) {
      var summary = form.querySelector('.error-summary');
      if (summary) summary.remove();
      var seen = {}, bad = [];
      fields.forEach(function (f) {
        if (f.type === 'radio') { if (seen[f.name]) return; seen[f.name] = true; }
        if (!check(f)) bad.push(f);
      });
      if (bad.length) {
        e.preventDefault();
        summary = doc.createElement('div');
        summary.className = 'error-summary';
        summary.tabIndex = -1;
        summary.setAttribute('role', 'alert');
        var list = bad.map(function (f) {
          return '<li><a href="#' + (f.id || '') + '">' + doc.getElementById(errorId(f)).textContent.replace(/^Error: /, '') + '</a></li>';
        }).join('');
        summary.innerHTML = '<h2>Please fix ' + bad.length + (bad.length > 1 ? ' things' : ' thing') + '</h2><ul>' + list + '</ul>';
        form.insertBefore(summary, form.firstChild);
        summary.focus();
        return;
      }
      if (!window.fetch || !window.FormData) return; /* plain POST fallback */
      e.preventDefault();
      var btn = form.querySelector('[type=submit]');
      if (btn) { btn.disabled = true; btn.dataset.label = btn.textContent; btn.textContent = 'Sending…'; }
      fetch(form.getAttribute('action') || '/', { method: 'POST', body: new FormData(form) })
        .then(function (r) {
          if (!r.ok) throw new Error(r.status);
          var ok = doc.createElement('div');
          ok.className = 'form-success';
          ok.setAttribute('role', 'status');
          ok.tabIndex = -1;
          ok.innerHTML = '<h2>' + (form.dataset.successTitle || 'Thank you.') + '</h2><p>' + (form.dataset.success || 'We received your message.') + '</p>';
          form.replaceWith(ok);
          ok.focus();
        })
        .catch(function () {
          if (btn) { btn.disabled = false; btn.textContent = btn.dataset.label; }
          var err = doc.createElement('div');
          err.className = 'error-summary';
          err.setAttribute('role', 'alert');
          err.innerHTML = '<h2>That didn’t send</h2><p>Please try again, or call us at 740-366-1604.</p>';
          err.tabIndex = -1;
          form.insertBefore(err, form.firstChild);
          err.focus();
        });
    });
  }

  /* ?position=Massage pre-selects the careers position radio */
  function preselect() {
    var m = /[?&]position=([^&]+)/.exec(location.search);
    if (!m) return;
    var val = decodeURIComponent(m[1].replace(/\+/g, ' '));
    Array.prototype.forEach.call(doc.querySelectorAll('input[name="position"]'), function (r) {
      if (r.value === val) r.checked = true;
    });
  }

  function ready(fn) { if (doc.readyState !== 'loading') fn(); else doc.addEventListener('DOMContentLoaded', fn); }
  ready(function () {
    preselect();
    Array.prototype.forEach.call(doc.querySelectorAll('form[data-netlify]'), init);
  });
})();
