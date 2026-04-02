function showSection(id, el) {
  // Hide all sections
  document.querySelectorAll(".section").forEach(sec => {
    sec.classList.add("hidden");
  });

  // Show selected
  document.getElementById(id).classList.remove("hidden");

  // Remove active from all sidebar buttons
  document.querySelectorAll(".sidebar button").forEach(btn => {
    btn.classList.remove("active");
  });

  // Add active to clicked button
  if (el) el.classList.add("active");
}