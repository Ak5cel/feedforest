window.addEventListener('load', (e) => {
	var hiddenOffset = document.getElementById('hiddenOffset');
	var hiddenTime = document.getElementById('hiddenTime');
	
	const d = new Date();
	const utc_offset = d.getTimezoneOffset();
	// Sets timezone offset to be submitted along with the form
	hiddenOffset.value = utc_offset;

	// The time selected by the user is stored in the 'time_from_db' hidden element
	var time_from_db = hiddenTime.value;
	if (time_from_db != '') {
		autoFillTime(time_from_db, utc_offset);	
	}
})

function autoFillTime(time_from_db, utc_offset) {
	var [hours, am_or_pm] = getUserLocaleTime(time_from_db, utc_offset)
	// Set selected values in the dropdowns
	document.getElementById('hourField').value = hours;
	document.getElementById('ampmField').value = am_or_pm;
}