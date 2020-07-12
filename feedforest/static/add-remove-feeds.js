$(document).ready(function() {
	// Attach a submit handler to the add/remove form
	$('form.add-remove').submit(function(e) {

		// Stop form from submitting normally
		e.preventDefault();

		// Get the url of the action endpoint
		var $form = $(this);
		var url = $form.attr('action');

		// Send a POST request to the add/remove endpoint
		$.post(url, function(data, status) {
			location.reload();
		})
	});
})