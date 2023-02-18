from django.test import TestCase

# Create your tests here.

const textareavalue = document.getElementById(`textarea_${id}`).value
    fetch(`/edit/${id}`, {
      method: "POST",
      headers: {"content-type": "application/json", "X-CSRFToken": getCookie("csrftoken")},
      body: JSON.stringify({
        content: textareavalue
      })
    })
    .then(response => response.json())
    .then(result =>
    console.log(id));