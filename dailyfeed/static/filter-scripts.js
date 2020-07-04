function filterFeeds() {
            // Get the topics form
            const topicsForm = document.getElementById('topicsForm');
            // Get all the checkboxes in the form
            const topicsCheckboxes = topicsForm.getElementsByClassName('form-check-input');
            // See which all topics are selected
            let selectedTopics = [];
            for (var i = 0; i < topicsCheckboxes.length; i++) {
                if (topicsCheckboxes[i].checked) {
                    selectedTopics.push(topicsCheckboxes[i].name);
                }
            }
            // Get all the filterable divs
            let filterDivs = document.getElementsByClassName('filterdiv');
            // Hide all filterdivs
            for (var i = 0; i < filterDivs.length; i++) {
                filterDivs[i].style.display = "none";
            }
            // Show only the divs matching selected topics
            for (var i = 0; i < selectedTopics.length; i++) {
                selectedTopic = selectedTopics[i];
                for (var j = 0; j < filterDivs.length; j++) {
                    if (filterDivs[j].classList.contains(selectedTopic)) {
                        filterDivs[j].style.display = "";
                    }
                }
            }
            
        }