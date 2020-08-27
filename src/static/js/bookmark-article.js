$(document).ready(function() {
  // Attach an onclick handler to the bookmark toggler icon/button
  $('.toggle-bookmark').on('click', (e) => {

    // Prevent default link behaviour
    e.preventDefault();

    // Determine action - whether to bookmark or unbookmark
    var action = "";
    var article = $(e.target).parents(".article");
    var article_status = article.attr("data-status");
    if (article_status == "bookmarked") {
      action = "unbookmark";
    } else if (article_status == "notBookmarked") {
      action = "bookmark";
    }

    // Get the article id
    var article_id = parseInt(article.attr("data-article-id"));

    // Determine url to make the POST request to
    var url = $SCRIPT_ROOT + "/" + action + "?article_id=" + article_id;

    // Send POST request
    $.ajax({
      type: 'POST',
      url: url,
      success: function(res) {
        if (action == "bookmark") {
          article.attr("data-status", "bookmarked");
        } else if (action == "unbookmark") {
          article.attr("data-status", "notbookmarked");
        }
        // Check whether there are any more bookmarked articles
        var bookmarked_articles = $('.article.toggle-display[data-status="bookmarked"]');
        if ($('.article.toggle-display').length > 0 && bookmarked_articles.length == 0) {
          window.location.reload(true);
        }
      },
      error: function(err) {
        if (err.responseJSON.message == "LOGIN_REQUIRED") {
          window.location.href =  err.responseJSON.redirect;
        } else {
          alert(`Sorry, we've encountered an unexpected error. Please try again later.
            \nStatus: ${err.status}`);
        }
      } 
    });

    
  })

})