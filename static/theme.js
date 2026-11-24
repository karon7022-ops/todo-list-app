(function () {
  var themeSelect = document.getElementById("theme-select");
  var systemPreference = window.matchMedia("(prefers-color-scheme: dark)");

  function applyTheme(theme) {
    document.documentElement.dataset.theme = theme;
    document.documentElement.dataset.systemTheme = systemPreference.matches ? "dim" : "light";
  }

  var savedTheme = document.documentElement.dataset.theme;
  themeSelect.value = savedTheme;
  applyTheme(savedTheme);

  themeSelect.addEventListener("change", function () {
    var theme = themeSelect.value;
    applyTheme(theme);
    try {
      localStorage.setItem("todo-list-theme", theme);
    } catch (_error) {
      // The selected theme remains applied for this page even if storage is unavailable.
    }
  });

  systemPreference.addEventListener("change", function () {
    if (document.documentElement.dataset.theme === "system") {
      applyTheme("system");
    }
  });
})();
