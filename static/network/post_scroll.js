
  let counter = 1;
  const quantity = 10;

  document.addEventListener('DOMContentLoaded', load);
  window.onscroll = () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
      load();
    }
  };

  function load() {
    const start = counter;
    const end = start + quantity - 1;
    counter = end + 1;

    fetch(`/load_posts/?start=${start}&end=${end}`)
      .then(response => response.json())
      .then(data => {
        console.log(data)
        data.posts.forEach(renderPost);
      });
  }

  function renderPost(postData) {
  const postElement = document.createElement('div');
  postElement.className = 'post';

  const user = postData.scrollUser;
  const profilePic = user.profile_pic
    ? `<img src="${user.profile_pic}" class="rounded-circle" width="70" height="70">`
    : '<img src="/media/post_image/hand.gif" class="rounded-circle" width="70" height="70">';

    const postContent = postData.scrollContent
  .split('\n')
  .slice(0, 3)  // Limit to 5 paragraphs
  .map(paragraph => `<p>${paragraph}</p>`)
  .join('');


  const postTimestamp = new Date(postData.scrollTimestamp).toLocaleString('en-US', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: 'numeric',
    minute: 'numeric',
    hour12: true,
  });

  const postImage = postData.scrollImage
    ? `<div class="card-body">
         <div class="image-container">
           <img src="${postData.scrollImage}" class="img-fluid desktop-image" alt="Post Image">
         </div>
       </div>`
    : '';

  const userProfileLink = `/profile/${user.user}/`; // Use user.id here
  const userFullName = `${user.first_name} ${user.last_name}`;
  const userName = `@${user.username}`;
  const likesSection = document.createElement('div');
  

  const readMoreLink = postData.scrollPostId
    ? `<a style="color: white"; href="/post_content/${postData.scrollPostId}">Read full content, reactions and comments >>></a>`
    : '';

  postElement.innerHTML = `
    <div class="container">
      <div class="card">
        <div class="card-body">
          <div class="d-flex align-items-center">
            <a href="${userProfileLink}">
              ${profilePic}
            </a>
            <div class="ml-3">
              <h5 class="card-title mb-1">
                <a class="card-title" style="text-decoration: none;" href="${userProfileLink}">${userFullName}</a>
              </h5>
              <p class="mb-0">
                <p>${userName}</p>
              </p>
            </div>
          </div>
          <br>
          <br>
          <div class="card-text" id="content_${postData.scrollId}">
            ${postContent}
            ${readMoreLink} <!-- Use readMoreLink here -->
            ${postImage}
          </div>
          <p class="card-text"><small class="text-muted">${postTimestamp}</small></p>
          <!-- ... (your existing code) ... -->
        </div>
      </div>
    </div>
  `;

  

  document.querySelector('#posts').appendChild(postElement);
}



 
