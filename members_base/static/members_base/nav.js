document.addEventListener("DOMContentLoaded", () => {
  const $main_navbar_burger = document.getElementById("main_navbar_burger");
  const $main_navbar = document.getElementById("main_navbar");

  $main_navbar_burger.addEventListener("click", () => {
    $main_navbar_burger.classList.toggle("is-active");
    $main_navbar.classList.toggle("is-active");
  });

  new ClipboardJS(".click-copy");
});
