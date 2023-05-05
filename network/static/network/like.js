//read more button

$(document).on('click', '.read-more', function() {
  var postId = $(this).data('post');
  window.location.href = "/post_content/" + postId;
});


