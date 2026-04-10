(function () {
  'use strict';

  var SENIOR_KEYWORDS = ['senior', 'lecturer', 'professor', 'director', 'principal'];
  var profiles = [];
  var searchInput, urCheckbox, seniorCheckbox, resultsContainer, countEl;

  function init() {
    searchInput = document.getElementById('search');
    urCheckbox = document.getElementById('underrepresented-only');
    seniorCheckbox = document.getElementById('senior-only');
    resultsContainer = document.getElementById('results-table');
    countEl = document.getElementById('search-count');

    if (!searchInput || !resultsContainer) return;

    fetch('/api/profiles/?format=json')
      .then(function (r) { return r.json(); })
      .then(function (data) {
        profiles = data.map(function (p) {
          // pre-compute a searchable text blob per profile (lowercase)
          p._search = [
            p.name, p.position, p.institution,
            p.country_name, p.modalities_display,
            p.domains_display, p.keywords
          ].filter(Boolean).join(' ').toLowerCase();
          return p;
        });
        // remove the server-rendered infinite scroll elements
        var moreLink = document.querySelector('.infinite-more-link');
        if (moreLink) moreLink.remove();
        var loading = document.querySelector('.loading');
        if (loading) loading.remove();
        // apply initial filter (handles ?s= in URL)
        applyFilter();
      });

    searchInput.addEventListener('input', debounce(applyFilter, 150));
    urCheckbox.addEventListener('change', applyFilter);
    seniorCheckbox.addEventListener('change', applyFilter);

    // prevent form submission — search is now live
    var form = searchInput.closest('form');
    if (form) {
      form.addEventListener('submit', function (e) {
        e.preventDefault();
      });
    }
  }

  function applyFilter() {
    var query = searchInput.value.trim().toLowerCase();
    var terms = query ? query.split(/\s+/) : [];
    var urOnly = urCheckbox && urCheckbox.checked;
    var seniorOnly = seniorCheckbox && seniorCheckbox.checked;

    var filtered = profiles.filter(function (p) {
      // under-represented filter
      if (urOnly && !p.country_is_under_represented) return false;

      // senior filter
      if (seniorOnly) {
        var pos = (p.position || '').toLowerCase();
        var isSenior = SENIOR_KEYWORDS.some(function (kw) {
          return pos.indexOf(kw) !== -1;
        });
        if (!isSenior) return false;
      }

      // text search — all terms must match
      for (var i = 0; i < terms.length; i++) {
        if (p._search.indexOf(terms[i]) === -1) return false;
      }

      return true;
    });

    render(filtered);
  }

  function render(list) {
    if (countEl) {
      countEl.textContent = list.length;
    }

    if (list.length === 0) {
      resultsContainer.innerHTML = '<p>No matching entries.</p>';
      return;
    }

    var html = '';
    for (var i = 0; i < list.length; i++) {
      var p = list[i];
      var profileUrl = p.username
        ? '/repo/' + encodeURIComponent(p.username) + '/'
        : '/repo/' + p.id + '/';
      var recommendUrl = '/repo/' + p.id + '/recommend/';

      var extras = [];
      if (p.modalities_display) extras.push(p.modalities_display);
      if (p.domains_display) extras.push(p.domains_display);
      if (p.keywords) extras.push(p.keywords);

      html += '<div class="table-entry">'
        + '<div class="d-sm-flex my-4 no-gutters">'
        + '<div class="col-xs-12 col-sm-4 col-md-4 col-lg-3">'
        + '<h5 class="text-primary fw-bold">'
        + '<a href="' + profileUrl + '">' + escapeHtml(p.name) + '</a>'
        + '</h5></div>'
        + '<div class="col-xs-12 col-sm-4 col-md-3 col-lg-3 details-grey text-muted">'
        + '<p class="m-1"><i class="fas fa-user"></i> <span>' + escapeHtml(p.position || '') + '</span></p>'
        + '<p class="m-1"><i class="fas fa-university"></i> <span>' + escapeHtml(p.institution || '') + '</span></p>'
        + '<p class="m-1"><i class="fas fa-map-marker-alt"></i> <span>' + escapeHtml(p.country_name || '') + '</span></p>'
        + '</div>'
        + '<div class="col-lg-3 keywords-list flex-fill mt-1 d-none d-lg-block">'
        + escapeHtml(extras.join(', '))
        + '</div>'
        + '<div class="col-md-1 col-lg-1 mt-1 ps-4 d-none d-md-block text-primary">'
        + (p.recommendation_count
          ? '<span><i class="fas fa-comment num-rec"></i> ' + p.recommendation_count + '</span>'
          : '')
        + '</div>'
        + '<div class="actions text-xs-start text-sm-end">'
        + '<a class="btn pill-btn btn-outline-secondary w-75 m-2" href="' + profileUrl + '">View Profile</a>'
        + '<a class="btn pill-btn btn-outline-secondary w-75 m-2" href="' + recommendUrl + '">Recommend</a>'
        + '</div></div></div>';
    }

    resultsContainer.innerHTML = html;
  }

  function escapeHtml(str) {
    var div = document.createElement('div');
    div.appendChild(document.createTextNode(str));
    return div.innerHTML;
  }

  function debounce(fn, delay) {
    var timer;
    return function () {
      clearTimeout(timer);
      timer = setTimeout(fn, delay);
    };
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }
})();
