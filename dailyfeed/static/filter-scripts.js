function filterFeedsByTopic() {
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

function filterFeedsBySite() {
            // Get the sites form
            const sitesForm = document.getElementById('sitesForm');
            // Get all the topic section divs in the form
            var topicSections = document.getElementsByClassName('topic-section');
            
            for (var i = 0; i < topicSections.length; i++) {
                topicNameUpperCase = topicSections[i].querySelector("h6").innerText;
                topicName = topicNameUpperCase.charAt(0) + topicNameUpperCase.substr(1).toLowerCase();
                // For each topic section, get all the checkboxes
                let sitesCheckboxes = topicSections[i].getElementsByClassName('form-check-input');
                // See which all sites are selected for that topic
                let selectedSites = [];
                for (var j = 0; j < sitesCheckboxes.length; j++) {
                    if (sitesCheckboxes[j].checked) {
                        selectedSites.push(sitesCheckboxes[j].name);
                    }
                }
                // Get that topic's filterdiv
                let topicDiv = document.getElementsByClassName(`filterdiv ${topicName}`)[0];
                // Get every article's site link and article link
                let siteLinks = topicDiv.querySelectorAll("a.site-link");
                let articleLinks = topicDiv.querySelectorAll("a.site-link + p");
                // For each site link, if the site name is selected, display the entry
                // Else, hide the entry
                for (var entryNum = 0; entryNum < siteLinks.length; entryNum++) {
                    articleSite = siteLinks[entryNum].querySelector("small").innerText;
                    if (selectedSites.indexOf(articleSite) > -1) {
                        siteLinks[entryNum].style.display = "";
                        articleLinks[entryNum].style.display = "";
                    } else {
                        siteLinks[entryNum].style.display = "none";
                        articleLinks[entryNum].style.display = "none";
                    }
                }
                // If no site is selected for that topic, hide the topic's div
                if (selectedSites.length == 0) {
                    topicDiv.style.display = "none";
                } else {
                    topicDiv.style.display = "";
                }
                
            }
        }