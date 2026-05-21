let collectionIndex = 1;

function updateCollectionSlider() {
  if (window.innerWidth <= 768) return; // ❌ disable on mobile

  const track = document.getElementById("collectionTrack");
  const cards = document.querySelectorAll(".collection-card");

  if (!cards.length) return;

  const cardWidth = cards[0].offsetWidth + 30;
  const sliderWidth = track.parentElement.offsetWidth;

  const centerOffset = (sliderWidth / 2) - (cardWidth / 2);

  track.style.transform = `translateX(${centerOffset - (collectionIndex * cardWidth)}px)`;

  cards.forEach(card => card.classList.remove("active"));
  if (cards[collectionIndex]) {
    cards[collectionIndex].classList.add("active");
  }
}

function moveSlide(direction) {
  if (window.innerWidth <= 768) return; // ❌ disable on mobile

  const cards = document.querySelectorAll(".collection-card");

  collectionIndex += direction;

  if (collectionIndex < 0) collectionIndex = 0;
  if (collectionIndex >= cards.length) collectionIndex = cards.length - 1;

  updateCollectionSlider();
}

/* INIT */
window.addEventListener("load", updateCollectionSlider);
window.addEventListener("resize", updateCollectionSlider);