(function() {
  $(document).ready(function() {
    $('#underrepresented-only, #senior-only').change(function() {
      $('#search-btn').click();
    });

    if ($('#back-to-top').length) {
      var scrollTrigger = 600,
        backToTop = function () {
          var scrollTop = $(window).scrollTop();
          if (scrollTop > scrollTrigger) {
            $('#back-to-top').addClass('show');
          } else {
            $('#back-to-top').removeClass('show');
          }
        };
      backToTop();
      $(window).on('scroll', function () {
        backToTop();
      });
      $('#back-to-top').on('click', function (e) {
        e.preventDefault();
        $('html,body').animate({
          scrollTop: 0
        }, 700);
      });
    }

    new Waypoint.Infinite({
      element: $('.infinite-container')[0],
      onBeforePageLoad: function() {
        $('.loading').show();
      },
      onAfterPageLoad: function($items) {
        $('.loading').hide();
      },
    });
  });
})();
