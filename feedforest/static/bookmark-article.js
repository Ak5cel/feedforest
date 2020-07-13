$(document).ready(function() {
	// Attach an onclick handler to the bookmark toggler icon
	$('.toggle-bookmark').on('click', (e) => {

		// Prevent default link behaviour
		e.preventDefault();

		// Determine action - whether to bookmark or unbookmark
		var action = "";
		var article = $(e.target).parents(".article");
		var article_status = article.attr("data-status");
		if (article_status == "bookmarked") {
			action = "unbookmark";
		} else if (article_status == "not-bookmarked") {
			action = "bookmark";
		}

		// Get the article id
		var article_id = parseInt(article.attr("data-article-id"));

		// Determine url to make the POST request to
		var url = $SCRIPT_ROOT + "/" + action + "?article_id=" + article_id;

		// Send POST request
		$.post(url, function(data, status) {
			/*
			 * If the AJAX request was a success, toggle the bookmark button
			 *
			 */
			if (status == "success") {
				// If the article was bookmarked, set status to 'bookmarked', otherwise
				// set status to 'not-bookmarked'
				if (action == "bookmark") {
					article.attr("data-status", "bookmarked");
				} else if (action == "unbookmark") {
					article.attr("data-status", "not-bookmarked");
				}
			}
		})
	})

})