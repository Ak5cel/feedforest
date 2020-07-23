$(document).ready(function(){

	let timeFieldSet = document.getElementById('timeFieldSet');
	let never = document.getElementById('0'); 
	let daily = document.getElementById('1');

	never.checked = true;
	timeFieldSet.disabled = true;
	
	$('input[type="radio"]').on('click', (e) => {
		
		if (never.checked) {
			timeFieldSet.disabled = true;
		} else if (daily.checked) {
			timeFieldSet.disabled = false;
		}

	})
	
})