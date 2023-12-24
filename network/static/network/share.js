
    let fileUrl; // Variable to store the file URL

    function shareFiles(url) {
        fileUrl = url; // Set the file URL to the variable
        const modal = document.getElementById("shareModals");
        modal.style.display = "block";
        const closeModalBtn = modal.querySelector(".close");
        closeModalBtn.onclick = function() {
            modal.style.display = "none";
        };
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        };
    }

    function shareFile(url) {
        fileUrl = url; // Set the file URL to the variable
        const modal = document.getElementById("shareModal");
        modal.style.display = "block";
        const closeModalBtn = modal.querySelector(".close");
        closeModalBtn.onclick = function() {
            modal.style.display = "none";
        };
        window.onclick = function(event) {
            if (event.target == modal) {
                modal.style.display = "none";
            }
        };
    }

    function copyLink() {
        if (fileUrl) {
            navigator.clipboard.writeText(fileUrl);
            const linkCopiedAlert = document.getElementById("linkCopiedAlert");
            linkCopiedAlert.style.display = "block";
            setTimeout(function() {
                linkCopiedAlert.style.display = "none";
            }, 2000);
        }
    }

   
    let share_id = ''; // Declare share_id as a global variable
    let friend_id = '';

function share(postId) {
    share_id = postId; // Set the global share_id variable
    console.log(share_id)
    openModal('shareModal');
}

function friendShare(friendId) {
    const postId = share_id; // Access the global share_id variable
    const friend_id = friendId
    if (!postId) {
        console.error("postId is not defined.");
        return;
    }
    console.log(postId)
    console.log(friend_id)
    const data = {
        post_id: postId,
        friendID: friend_id
    };
    fetch("/share_post", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie('csrftoken'),
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (response.ok) {
            alert("Post shared successfully!");
            closeModal('shareModal')
        } else {
            alert("Error sharing post.");
        }
    })
    .catch(error => {
        console.error("Fetch error:", error);
    });
}

function groupShare(groupId) {
    const postId = share_id; // Access the global share_id variable
    const group_id = groupId
    if (!postId) {
        console.error("postId is not defined.");
        return;
    }
    console.log(postId)
    console.log(group_id)
    const data = {
        post_id: postId,
        groupID: group_id
    };
    fetch("/group_share", {
        method: "POST",
        headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCookie('csrftoken'),
        },
        body: JSON.stringify(data),
    })
    .then(response => {
        if (response.ok) {
            alert("Post shared successfully!");
            closeModal('shareModal')
        } else {
            alert("Error sharing post.");
        }
    })
    .catch(error => {
        console.error("Fetch error:", error);
    });
}
