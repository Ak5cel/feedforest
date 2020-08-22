// SCRIPTS FOR EDIT FEEDS PAGE --------------------------------------------------------
$(document).ready(function() {
  $('.topic-selector').on('click', (e) => {
    let topic = e.target.id;
    if (topic == 'all') {
      // Show all feeds
      $('.feed-info').show().addClass('d-flex');
      // Set dropdown to display 'All Topics'
      $('#topicsDropdown').text('All Topics');
    } else {
      // Hide all feeds:
      // Removing 'd-flex' is necessary as otherwise the !important property of
      // Bootstrap d-flex overrides hide()
      $('.feed-info').hide().removeClass('d-flex');
      // Show just the feeds from the selected topic
      $('.feed-info[data-topic="' + topic + '"]').show().addClass('d-flex');   
      // Set dropdown to display the selected topic
      $('#topicsDropdown').text(topic);
    }
    // Highlight selected topic in the dropdown-menu
    $('.topic-selector').removeClass('active');
    $(e.target).addClass("active");
  })
})
// END SCRIPTS FOR EDIT FEEDS PAGE --------------------------------------------------