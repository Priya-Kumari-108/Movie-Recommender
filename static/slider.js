document.addEventListener("DOMContentLoaded", function() {
    // ---------------- Hero Carousel Auto Slide ----------------
    const heroWrapper = document.querySelector(".hero-wrapper");
    const heroSlides = document.querySelectorAll(".hero-slide");
    let currentHero = 0;
    const heroInterval = 5000;

    function showHeroSlide(index) {
        heroWrapper.style.transform = `translateX(-${index * 100}%)`;
    }

    function nextHeroSlide() {
        currentHero = (currentHero + 1) % heroSlides.length;
        showHeroSlide(currentHero);
    }

    if (heroSlides.length > 0) setInterval(nextHeroSlide, heroInterval);

    // Hero carousel arrows
    const heroArrows = document.querySelectorAll("#hero-carousel .arrow");
    heroArrows.forEach(arrow => {
        arrow.addEventListener("click", () => {
            if (arrow.classList.contains("left")) {
                currentHero = (currentHero - 1 + heroSlides.length) % heroSlides.length;
            } else {
                currentHero = (currentHero + 1) % heroSlides.length;
            }
            showHeroSlide(currentHero);
        });
    });

    // ---------------- Other Horizontal Carousels ----------------
    const carousels = document.querySelectorAll(".carousel-wrapper");
    carousels.forEach(wrapper => {
        const carousel = wrapper.querySelector(".carousel");
        const leftBtn = wrapper.querySelector(".arrow.left:not(#hero-carousel .arrow)");
        const rightBtn = wrapper.querySelector(".arrow.right:not(#hero-carousel .arrow)");

        if (leftBtn) {
            leftBtn.addEventListener("click", () => {
                carousel.scrollBy({ left: -200, behavior: "smooth" });
            });
        }

        if (rightBtn) {
            rightBtn.addEventListener("click", () => {
                carousel.scrollBy({ left: 200, behavior: "smooth" });
            });
        }
    });

    // ---------------- Search Autocomplete ----------------
    const searchInput = document.getElementById("movie-search");
    const suggestionBox = document.querySelector(".suggestion-box");

    searchInput.addEventListener("input", () => {
        const query = searchInput.value.toLowerCase();
        suggestionBox.innerHTML = "";
        if (query.length > 0) {
            const suggestions = moviesList.filter(m => m.toLowerCase().includes(query));
            suggestions.forEach(s => {
                const div = document.createElement("div");
                div.classList.add("suggestion-item");
                div.textContent = s;
                div.addEventListener("click", () => {
                    searchInput.value = s;
                    suggestionBox.innerHTML = "";
                });
                suggestionBox.appendChild(div);
            });
        }
    });

    // Close suggestion box if clicked outside
    document.addEventListener("click", (e) => {
        if (!searchInput.contains(e.target)) {
            suggestionBox.innerHTML = "";
        }
    });
});
