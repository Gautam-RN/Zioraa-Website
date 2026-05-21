let index = 0;

function showSlide() {
  const slides = document.getElementById("slides");
  slides.style.transform = `translateX(-${index * 100}%)`;
}

function nextSlide() {
  const total = document.querySelectorAll(".slide").length;
  index = (index + 1) % total;
  showSlide();
}

function prevSlide() {
  const total = document.querySelectorAll(".slide").length;
  index = (index - 1 + total) % total;
  showSlide();
}

