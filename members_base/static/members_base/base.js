document.addEventListener("DOMContentLoaded", () => {
  const $main_navbar_burger = document.getElementById("main_navbar_burger");
  const $main_navbar = document.getElementById("main_navbar");

  $main_navbar_burger.addEventListener("click", () => {
    $main_navbar_burger.classList.toggle("is-active");
    $main_navbar.classList.toggle("is-active");
  });

  new ClipboardJS(".click-copy");
});

document.addEventListener("DOMContentLoaded", () => {
  const $theme_toggle = document.getElementById("theme-toggle");
  const $theme_icon_auto = document.getElementById("theme-icon-auto");
  const $theme_icon_light = document.getElementById("theme-icon-light");
  const $theme_icon_dark = document.getElementById("theme-icon-dark");

  function handleThemeChange(theme) {
    if (theme === "auto") {
      delete document.documentElement.dataset.theme;
      $theme_icon_auto.style.display = "";
      $theme_icon_light.style.display = "none";
      $theme_icon_dark.style.display = "none";
    } else if (theme === "light") {
      document.documentElement.dataset.theme = theme;
      $theme_icon_auto.style.display = "none";
      $theme_icon_light.style.display = "";
      $theme_icon_dark.style.display = "none";
    } else if (theme === "dark") {
      document.documentElement.dataset.theme = theme;
      $theme_icon_auto.style.display = "none";
      $theme_icon_light.style.display = "none";
      $theme_icon_dark.style.display = "";
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

  $theme_toggle.addEventListener("click", () => {
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
});
