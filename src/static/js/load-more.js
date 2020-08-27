$(document).ready(function() {

  function loadArticles(page, feed_id, loader) {
    // var loader = document.querySelector('#loader');
    var template = document.querySelector('#article_template');
    var loadBtn = $(loader).siblings('#loadBtn')[0];

    url = `/load?feed_id=${feed_id}&page=${page}`;

    $.ajax({
      type: 'POST',
      url: url,
      success: function(res) {
        var articles = res["articles"];

        for (var i = 0; i < articles.length; i++) {
          let template_clone = template.content.cloneNode(true);
          let articleItem = template_clone.querySelector('#articleItem');
          
          // Query and update the template content
          articleItem.setAttribute("data-article-id", articles[i].id);
          if (articles[i].is_bookmarked) {
            articleItem.setAttribute("data-status", "bookmarked"); 
          } else {
            articleItem.setAttribute("data-status", "notBookmarked");
          }

          template_clone.querySelector('#feedLink').setAttribute("href", res["site_url"]);
          template_clone.querySelector('#feedLink').innerHTML = res["feed_name"].toUpperCase();
          template_clone.querySelector('#articleLink').setAttribute("href", articles[i].link);
          template_clone.querySelector('#articleLink').innerHTML = articles[i].title;
          template_clone.querySelector('#publishedOn').innerHTML = articles[i].published_on + ' UTC';

          // Append template to DOM
          loader.appendChild(template_clone);

          
          if (res["has_next"]) {
            // Increase page count
            loadBtn.setAttribute("data-page", page);
          } else {
            // If there are no more articles, remove the Load More button
            $(loadBtn).remove();
          }

        }
      },
      error: function(err) {
        console.log(err);
      }
    })
  }


  $('#loadBtn').on('click', (e) => {
    e.preventDefault();

    var loader = $(e.target).siblings('#loader')[0];
    let page = parseInt(e.target.getAttribute("data-page"));
    let feedId = parseInt(e.target.getAttribute("data-feed-id"));

    loadArticles(page + 1, feedId, loader);
  })

})
