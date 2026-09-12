// SPAK platform JS
document.addEventListener("DOMContentLoaded", function () {
  // Close alerts automatically
  document.querySelectorAll(".alert-dismissible").forEach(function (el) {
    setTimeout(function () {
      var close = el.querySelector(".btn-close");
      if (close) close.click();
    }, 7000);
  });
});