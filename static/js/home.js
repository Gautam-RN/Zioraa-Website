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

let position = 0;

function moveSlide(direction) {
  const track = document.getElementById("collectionTrack");
  const cards = document.querySelectorAll(".collection-card");

  const cardWidth = cards[0].offsetWidth + 30;
  const visibleCards = Math.floor(track.parentElement.offsetWidth / cardWidth);

  const maxMove = (cards.length - visibleCards) * cardWidth;

  position += direction * cardWidth;

  if (position < 0) position = 0;
  if (position > maxMove) position = maxMove;

  track.style.transform = `translateX(-${position}px)`;
}