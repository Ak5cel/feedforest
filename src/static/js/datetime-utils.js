function getUserLocaleTime(time_from_db, utc_offset) {
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
	} else if (hours == 12) {
		am_or_pm = 'pm'
	} else if (hours == 0) {
		hours = 12
	}
	return [hours, am_or_pm]
}
