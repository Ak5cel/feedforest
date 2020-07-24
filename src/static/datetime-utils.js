function autoFillTime(time_from_db, utc_offset) {
	// Get hours, minutes and seconds from the time string
	var [h, m, s] = time_from_db.split(':');
	// Create a new date object with the time from the database
	var d = new Date();
	d.setHours(h);
	d.setMinutes(m);
	d.setSeconds(s);
	// Subtract offset to create a new date in the user's timezone
	let newDate = new Date(d.getTime() - utc_offset * 60 * 1000);
	var hours = newDate.getHours();
	var am_or_pm = 'am';
	if (hours > 12) {
		hours -= 12;
		am_or_pm = 'pm';
	}
	// Set selected values in the dropdowns
	document.getElementById('hourField').value = hours;
	document.getElementById('ampmField').value = am_or_pm;
}

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