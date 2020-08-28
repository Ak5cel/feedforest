$(document).ready(function() {

  function loadArticles(page, feed_id, loader) {
    var template = loader.querySelector('.article_template');
    var loadBtn = $(loader).siblings('.btn-load')[0];

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

          let feedLinkNode = template_clone.querySelector('#feedLink');
          if (feedLinkNode) {
            feedLinkNode.setAttribute("href", res["site_url"]);
            feedLinkNode.innerHTML = res["feed_name"].toUpperCase();
          }

          let articleLinkNode = template_clone.querySelector('#articleLink');
          if (articleLinkNode) {
            articleLinkNode.setAttribute("href", articles[i].link);
            articleLinkNode.innerHTML = articles[i].title;
          }

          let publishedOnNode = template_clone.querySelector('#publishedOn');
          if (publishedOnNode) {
            publishedOnNode.innerHTML = articles[i].published_on + ' UTC';
          }

          // Attach event handlers to the toggleBookmark icon/button
          template_clone.querySelector(".toggle-bookmark").onclick = toggleBookmark;

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


  $('.btn-load').on('click', (e) => {
    e.preventDefault();

    var loader = $(e.target).siblings('.loader')[0];
    let page = parseInt(e.target.getAttribute("data-page"));
    let feedId = parseInt(e.target.getAttribute("data-feed-id"));

    loadArticles(page + 1, feedId, loader);
  })

})
