"use strict";

function handleProblemSubmit(event) {
  event.preventDefault();

  let form = document.querySelector("form.math_problem");
  let answer = form.querySelector("#id_answer");
  let submitButton = form.querySelector("input[type=submit]");

  submitButton.disabled = true;

  fetch(form.action, {
    method: "POST",
    redirect: "follow",
    body: "answer=" + answer.value,
    headers: {
      "Content-Type": "application/x-www-form-urlencoded"
    }
  })
    .then(response => {
      submitButton.disabled = false;
      return response.json();
    })
    .then(data => {
      if (data.success === true) {
        answer.style.borderColor = "#00FF00";
        submitButton.style.display = "none";
        window.setTimeout(() => {
          window.location = data.redirect_to;
        }, 1000);
      } else {
        answer.value = "";
        answer.style.borderColor = "#FF0000";
      }
    });

  return false;
}

window.addEventListener("DOMContentLoaded", event => {
  let form = document.querySelector("form.math_problem");

  if (form) {
    form.addEventListener("submit", handleProblemSubmit);
  }
});
