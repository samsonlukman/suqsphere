
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

$(document).ready(function() {
  var reactionTimeout;

  // Hide all reaction buttons by default
  $('.reaction-button').hide();

  // Show the reaction buttons when the mouse hovers on a like button
  $('.like-btn').mouseenter(function() {
    var postId = $(this).data('post-id');
    $('#reaction-buttons-' + postId).show();
    clearTimeout(reactionTimeout);
  });

  // Hide the reaction buttons after 10 seconds of not hovering on the like button
  $('.like-btn').mouseleave(function() {
    var postId = $(this).data('post-id');
    reactionTimeout = setTimeout(function() {
      $('#reaction-buttons-' + postId).hide();
    }, 3000); // 10 seconds
  });
});


function opensModal(postId) {
  var modal = document.getElementById('reactedUsersModal-' + postId);
  modal.style.display = 'block'; /* Show the modal */
}

function closesModal(postId) {
  var modal = document.getElementById('reactedUsersModal-' + postId);
  modal.style.display = 'none'; /* Hide the modal */
}


function openModal(modalId) {
  // Close any open modals (if needed)
  closeModal();

  // Open the specified modal
  const modal = document.getElementById(modalId);
  if (modal) {
      modal.style.display = "block";
  }
}

function closeModal() {
  // Close all modals
  const modals = document.querySelectorAll(".modal");
  modals.forEach((modal) => {
      modal.style.display = "none";
  });
}







const mainButton = document.getElementById('main-button');
const popup = document.getElementById('popup');

let hoverTimer;
let pressTimer;

mainButton.addEventListener('mousedown', () => {
  pressTimer = setTimeout(() => {
    popup.style.display = 'block';
  }, 2000);
});






function showColumn(columnId) {
  const column = document.getElementById(columnId);
  if (column.style.display === 'block') {
    column.style.display = 'none';
  } else {
    column.style.display = 'block';
  }
}
    
document.getElementById('shareId').addEventListener('click', () => withFriend());

   function withFriend(){
    console.log("HI")
   }
// This function gets the value of the cookie with the specified name
function getCookie(name){
            const value = `; ${document.cookie}`;
            const parts = value.split(`; ${name}=`);
            if(parts.length == 2) return parts.pop().split(';').shift();
        }

      
