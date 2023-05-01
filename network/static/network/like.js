function disableComment() {
    const commentBtns = document.querySelectorAll(".btn-comment button");
    const commentFields = document.querySelectorAll(".comment-field textarea");
  
    for (let i = 0; i < commentFields.length; i++) {
      const commentBtn = commentBtns[i];
      const newComment = commentFields[i];
  
      if (newComment.value.trim() === "") {
        commentBtn.disabled = true;
      } else {
        commentBtn.disabled = false;
      }
  
      // add event listener for input event
      newComment.addEventListener("input", function () {
        if (newComment.value.trim() === "") {
          commentBtn.disabled = true;
        } else {
          commentBtn.disabled = false;
        }
      });
    }
  }
  
  window.onload = function() {
    disableComment();
  };

  // Request permission from the user
Notification.requestPermission().then(permission => {
    if (permission === 'granted') {
      // Create a service worker
      navigator.serviceWorker.register('/static/network/service-worker.js').then(() => {
        // Subscribe the user to push notifications
        navigator.serviceWorker.ready.then(registration => {
          registration.pushManager.subscribe({ userVisibleOnly: true }).then(subscription => {
            // Send the subscription object to your server
            fetch('/subscribe', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json'
              },
              body: JSON.stringify(subscription)
            });
          });
        });
      });
    }
  });
  
  // Send a push notification
  function sendPushNotification(subscription, title, message) {
    fetch('/send-push-notification', {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json'
      },
      body: JSON.stringify({
        subscription: subscription,
        title: title,
        message: message
      })
    });
  }
  
  
  
  

// This function gets the value of the cookie with the specified name
function getCookie(name){
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if(parts.length == 2) return parts.pop().split(';').shift();
        }

        // This function is called when the form for editing a post is submitted
        function submitHandler(id){
            // Get the value of the textarea for the post being edited
            const textareaValue = document.getElementById(`textarea_${id}`).value;
            // Get the content element of the post being edited
            const content = document.getElementById(`content_${id}`);
            // Get the modal element for editing the post
            const modal = document.getElementById(`modal_edit_post_${id}`);
            // Send a POST request to the server to save the changes to the post
            fetch(`/edit/${id}`, {
                method: "POST",
                headers: {"Content-type": "application/json", "X-CSRFToken": getCookie("csrftoken")},
                body: JSON.stringify({
                    content: textareaValue
                })
            })
            // Parse the response as JSON
            .then(response => response.json())
            .then(result => {
                // Update the content of the post with the new content
                content.innerHTML = result.data;
                // Close the modal
                modal.classList.remove('show');
                modal.setAttribute('aria-hidden', 'true');
                modal.setAttribute('style', 'display: none');
                // Remove the modal backdrop
                const modalsBackdrops = document.getElementsByClassName('modal-backdrop');
                for(let i=0; i<modalsBackdrops.length; i++){
                    document.body.removeChild(modalsBackdrops[i]);
                }
            })
            
        }



  // This function is called when the like button for a post is clicked
  function likeHandler(id, whoYouLiked){
    // Get the like button element
    const btn = document.getElementById(`${id}`);

    // Remove the existing like/dislike icon classes
    btn.classList.remove('fa-thumbs-up')
    btn.classList.remove('fa-thumbs-down')

    // Check if the post has already been liked by the user
    let liked = (whoYouLiked.indexOf(id) >= 0);

    // Send a request to the server to like/unlike the post
    if(liked === true){
        fetch(`/remove_like/${id}`)
        .then(response => response.json())
        .then(result => {
            if (result.message === "You have already liked this post.") {
                // User has already liked the post, don't update the button or like count
                return;
            }
            // Update the like count element in the HTML template
            document.getElementById("likeCount_" + id).innerHTML = result.likes;

            // Update the liked variable based on the new like count
            liked = (result.likes > 0);

            // Add the appropriate icon class
            if (liked) {
                btn.classList.add('fa-thumbs-down')
            } else {
                btn.classList.add('fa-thumbs-up')
            }
        })
    } else {
    fetch(`/add_like/${id}`)
    .then(response => response.json())
    .then(result => {
        if (result.message === "You have already liked this post.") {
            // User has already liked the post, don't update the button or like count
            return;
        }
        // Update the like count element in the HTML template
        document.getElementById("likeCount_" + id).innerHTML = result.likes;

        // Update the liked variable based on the new like count
        liked = (result.likes > 0);

        // Add the appropriate icon class
        if (liked) {
            btn.classList.add('fa-thumbs-down')
        } else {
            btn.classList.add('fa-thumbs-up')
        }
    })
}
  }

