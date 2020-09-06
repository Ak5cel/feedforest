function addCustomFeed(e) {
  // Prevent modal from closing before validation
  e.preventDefault();

  var form = $('#customFeedForm')[0];
  var submitBtn = $('#customFeedForm #submit_feed')[0];

  var url = $(form).attr("action");

  $.post(url, data=$(form).serialize(), function(res) {
    if (res.message == "ok") {
      // if validation succeeds, hide the modal and reload the page
      $('#addCustomFeedModal').modal('hide');
      location.reload();
    } else {
      // if validation fails, show error feedback under the fields
      for (var key in res.data) {
        var field = $('.form-control[name="' + key + '"]')[0];
        $(field).addClass('is-invalid');
        var invalidFeedback = $("<div></div>").text(res.data[key]).addClass("invalid-feedback");
        $(field).after(invalidFeedback);
      }
    }
  });
}

$(document).ready(function () {
  $('#submit_feed').on('click', addCustomFeed);
});
