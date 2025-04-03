document.addEventListener("DOMContentLoaded", () => {
  const $main_navbar_burger = document.getElementById("main_navbar_burger");
  const $main_navbar = document.getElementById("main_navbar");

  $main_navbar_burger.addEventListener("click", () => {
    $main_navbar_burger.classList.toggle("is-active");
    $main_navbar.classList.toggle("is-active");
  });

  new ClipboardJS(".click-copy");
});

(() => {
  const theme_toggle_el = document.getElementById("theme-toggle");
  const theme_icon_auto_el = document.getElementById("theme-icon-auto");
  const theme_icon_light_el = document.getElementById("theme-icon-light");
  const theme_icon_dark_el = document.getElementById("theme-icon-dark");

  function handleThemeChange(theme) {
    if (theme === "auto") {
      delete document.documentElement.dataset.theme;
      theme_icon_auto_el.style.display = "";
      theme_icon_light_el.style.display = "none";
      theme_icon_dark_el.style.display = "none";
    } else if (theme === "light") {
      document.documentElement.dataset.theme = theme;
      theme_icon_auto_el.style.display = "none";
      theme_icon_light_el.style.display = "";
      theme_icon_dark_el.style.display = "none";
    } else if (theme === "dark") {
      document.documentElement.dataset.theme = theme;
      theme_icon_auto_el.style.display = "none";
      theme_icon_light_el.style.display = "none";
      theme_icon_dark_el.style.display = "";
    } else {
      handleThemeChange("auto");
      return;
    }

    localStorage.setItem("theme", theme);
  }

  function getTheme() {
    const theme_saved = localStorage.getItem("theme");

    if (
      theme_saved === "auto" ||
      theme_saved === "light" ||
      theme_saved === "dark"
    ) {
      return theme_saved;
    }
    return "auto";
  }

  theme_toggle_el.addEventListener("click", () => {
    const theme = getTheme();
    if (theme === "auto") {
      handleThemeChange("light");
    } else if (theme === "light") {
      handleThemeChange("dark");
    } else if (theme === "dark") {
      handleThemeChange("auto");
    } else {
      handleThemeChange("auto");
    }
  });

  handleThemeChange(getTheme());
})();
