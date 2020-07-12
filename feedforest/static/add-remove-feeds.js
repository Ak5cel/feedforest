$(document).ready(function() {
	// Attach a submit handler to the add/remove forms
	$('form.add-remove').submit(function(e) {

		// Stop form from submitting normally
		e.preventDefault();

		// Get the url of the action endpoint
		var $form = $(this);
		var url = $form.attr('action');

		// Send a POST request to the add/remove endpoint
		$.post(url, function(data, status) {
			/*
			 * If the AJAX request was a success, toggle the Add/Remove button
			 *
			 */
			if (status == "success") {
				var btn = $form.children('.btn');
				var btn_type = btn.attr('value');
				var id = $form.attr('id');

				// The value of the toggled button
				var newValue = '';

				// The 'action' url for the toggled button is stored in
				// the 'data-alt-action' attribute of the current form
				var newURL = $form.attr('data-alt-action');

				// If it is an 'Add' button, toggle to a 'Remove' button and 
				// vice-versa
				if (btn_type == 'Add') {
					newValue = 'Remove';
					btn.removeClass('btn-success');
					btn.addClass('btn-secondary');
				} else {
					newValue = 'Add';
					btn.removeClass('btn-secondary');
					btn.addClass('btn-success');
				}
				$form.attr("action", newURL);
				btn.attr("value", newValue);	
			} else {
				alert('Unexpected error. \nSorry, we were unable to process your request. Please try again later.')
			}
		})
	});
})