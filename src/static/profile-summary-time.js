window.addEventListener('load', (e) => {
	const time_from_db = document.getElementById('hiddenTime').value;
	const d = new Date();
	const utc_offset = d.getTimezoneOffset();
	if (time_from_db != '') {
		var [hours, am_or_pm] = getUserLocaleTime(time_from_db, utc_offset);
		// Set selected values in the placeholders
		document.getElementById('hourField').innerHTML = hours;
		document.getElementById('ampmField').innerHTML = am_or_pm;
	}
})