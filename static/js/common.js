function toggleProfileMenu() {
    const menu = document.getElementById("profileDropdown");
    menu.style.display = menu.style.display === "block" ? "none" : "block";
  }
  document.addEventListener("click", function (e) {
    const profileMenu = document.querySelector(".profile-menu");
    if (!profileMenu.contains(e.target)) {
      document.getElementById("profileDropdown").style.display = "none";
    }
  });

function toggleMenu() {
    const nav = document.getElementById("navbar");
    if (nav.style.display === "flex") {
        nav.style.display = "none";
    } else {
        nav.style.display = "flex";
    }
}
