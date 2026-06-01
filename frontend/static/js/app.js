document.addEventListener("DOMContentLoaded", () => {
  if (window.Swiper) {
    document.querySelectorAll(".featured-swiper").forEach((el) => {
      new Swiper(el, {
        slidesPerView: 1.08,
        spaceBetween: 18,
        loop: el.querySelectorAll(".swiper-slide").length > 2,
        autoplay: { delay: 3800, disableOnInteraction: false },
        breakpoints: {
          768: { slidesPerView: 2.1 },
          1100: { slidesPerView: 3.1 }
        }
      });
    });

    document.querySelectorAll(".apartment-plan-swiper").forEach((el) => {
      new Swiper(el, {
        slidesPerView: 1,
        speed: 650,
        autoHeight: false,
        observer: true,
        observeParents: true,
        navigation: {
          nextEl: el.querySelector(".apartment-plan-next"),
          prevEl: el.querySelector(".apartment-plan-prev")
        },
        pagination: {
          el: el.querySelector(".apartment-plan-pagination"),
          clickable: true
        },
        keyboard: { enabled: true }
      });
    });
  }

  if (window.gsap) {
    gsap.from(".hero .eyebrow, .hero h1, .hero-copy, .search-console, .stat-card", {
      y: 28,
      opacity: 0,
      duration: .9,
      stagger: .08,
      ease: "power3.out"
    });
  }

  document.querySelectorAll(".js-loading-form").forEach((form) => {
    form.addEventListener("submit", () => {
      var button = form.querySelector("button[type='submit']");
      if (!button) return;
      var spinner = button.querySelector(".spinner-border");
      if (spinner) spinner.classList.remove("d-none");
      button.disabled = true;
    });
  });

  document.querySelectorAll(".js-account-required").forEach((trigger) => {
    trigger.addEventListener("click", (event) => {
      var modalEl = document.getElementById("accountRequiredModal");
      if (!modalEl || !window.bootstrap) return;
      event.preventDefault();
      bootstrap.Modal.getOrCreateInstance(modalEl).show();
    });
  });
});
