document.addEventListener("DOMContentLoaded", () => {
  const attachSimpleFormValidations = () => {
    const forms = document.querySelectorAll("form[data-validate]");

    forms.forEach((form) => {
      form.addEventListener("submit", (event) => {
        const mode = form.dataset.validate;

        if (mode === "login") {
          const email = form.querySelector("#email");
          const contrasenia = form.querySelector("#contrasenia");
          const emailValue = email ? email.value.trim() : "";
          const contraseniaValue = contrasenia ? contrasenia.value : "";

          if (!emailValue || !emailValue.includes("@") || !emailValue.includes(".")) {
            event.preventDefault();
            alert("Ingresa un correo institucional valido.");
            return;
          }

          if (contraseniaValue.length < 2) {
            event.preventDefault();
            alert("La contrasena debe tener al menos 2 caracteres.");
            return;
          }
        }

        if (mode === "register") {
          const nombre = form.querySelector("#nombre");
          const email = form.querySelector("#email");
          const contrasenia = form.querySelector("#contrasenia");
          const nombreValue = nombre ? nombre.value.trim() : "";
          const emailValue = email ? email.value.trim() : "";
          const contraseniaValue = contrasenia ? contrasenia.value : "";

          if (nombreValue.length < 3) {
            event.preventDefault();
            alert("El nombre debe tener al menos 3 caracteres.");
            return;
          }

          if (!emailValue || !emailValue.includes("@")) {
            event.preventDefault();
            alert("Ingresa un correo electronico valido.");
            return;
          }

          if (contraseniaValue.length < 8) {
            event.preventDefault();
            alert("La contrasena debe tener al menos 8 caracteres.");
            return;
          }
        }

        if (mode === "alumno-reserva") {
          const articulo = form.querySelector("#articulo");
          const fecha = form.querySelector("#fecha");
          const desde = form.querySelector("#desde");
          const hasta = form.querySelector("#hasta");

          const articuloValue = articulo ? articulo.value.trim() : "";
          const fechaValue = fecha ? fecha.value : "";
          const desdeValue = desde ? desde.value : "";
          const hastaValue = hasta ? hasta.value : "";

          if (!articuloValue) {
            event.preventDefault();
            alert("Selecciona un articulo.");
            return;
          }

          if (!fechaValue || !desdeValue || !hastaValue) {
            event.preventDefault();
            alert("Completa fecha y rango horario.");
            return;
          }

          if (desdeValue >= hastaValue) {
            event.preventDefault();
            alert("La hora de inicio debe ser menor a la hora de fin.");
            return;
          }
        }

        if (mode === "profesor-reserva") {
          const articulo = form.querySelector("#articulo_id");
          const inicio = form.querySelector("#fecha_inicio");
          const fin = form.querySelector("#fecha_fin");

          const articuloValue = articulo ? articulo.value.trim() : "";
          const inicioValue = inicio ? inicio.value : "";
          const finValue = fin ? fin.value : "";

          if (!articuloValue) {
            event.preventDefault();
            alert("Selecciona un articulo para reservar.");
            return;
          }

          if (!inicioValue || !finValue) {
            event.preventDefault();
            alert("Completa fecha de inicio y devolucion.");
            return;
          }

          if (inicioValue > finValue) {
            event.preventDefault();
            alert("La fecha de inicio no puede ser posterior a la fecha de devolucion.");
          }
        }
      });
    });
  };

  attachSimpleFormValidations();

  const attachTicketActions = () => {
    const printButtons = document.querySelectorAll("[data-ticket-print], [data-ticket-pdf]");

    printButtons.forEach((button) => {
      button.addEventListener("click", () => {
        const originalTitle = document.title;
        const ticketFileName = button.dataset.ticketFileName;
        if (ticketFileName) {
          document.title = ticketFileName;
        }
        window.print();
        window.setTimeout(() => {
          document.title = originalTitle;
        }, 1000);
      });
    });
  };

  attachTicketActions();

  document.querySelectorAll(".reportes-bar").forEach((bar) => {
    const w = bar.dataset.width;
    if (w) bar.style.setProperty("--bar-width", w + "px");
  });
  
  const faqItems = document.querySelectorAll(".faq-item");

  faqItems.forEach((item) => {
    const questionBtn = item.querySelector(".faq-question");
    questionBtn.addEventListener("click", () => {
      item.classList.toggle("active");
    });
  });

  // Dynamic Greeting Logic for Dashboard
  const greetingElement = document.getElementById("greeting");
  const dateElement = document.getElementById("current-date");

  if (greetingElement && dateElement) {
    const now = new Date();
    const hour = now.getHours();
    let greeting = "Buenas noches";

    if (hour >= 5 && hour < 12) {
      greeting = "Buenos días";
    } else if (hour >= 12 && hour < 19) {
      greeting = "Buenas tardes";
    }

    const userNameElement = document.getElementById("dashboard-usuario-name");
    const userName = userNameElement ? userNameElement.textContent.trim() : "Usuario";

    greetingElement.textContent = `${greeting}, ${userName}`;

    const options = { weekday: "long", year: "numeric", month: "long", day: "numeric" };
    // Primera letra mayúscula para el día
    let dateString = now.toLocaleDateString("es-ES", options);
    dateString = dateString.charAt(0).toUpperCase() + dateString.slice(1);
    dateElement.textContent = dateString;
  }

  // Auto-add reveal class and staggered delays to elements
  const elementsToReveal = document.querySelectorAll(
    ".step-card, .benefit-card, .rule-item, .faq-item, section h2, .subtitle"
  );
  elementsToReveal.forEach((el) => {
    el.classList.add("reveal");
    let delayIndex = Array.from(el.parentNode.children).indexOf(el);
    // Limit delay to prevent excessive waits
    if (delayIndex > 5) delayIndex = 5;
    el.style.transitionDelay = delayIndex * 0.15 + "s";
  });

  // Scroll Reveal Animation Logic
  const reveals = document.querySelectorAll(".reveal");
  const revealOptions = {
    threshold: 0.1,
    rootMargin: "0px 0px -50px 0px",
  };

  const revealOnScroll = new IntersectionObserver(function (entries, observer) {
    entries.forEach((entry) => {
      if (entry.isIntersecting) {
        entry.target.classList.add("visible");
        observer.unobserve(entry.target);
      }
    });
  }, revealOptions);

  reveals.forEach((reveal) => {
    revealOnScroll.observe(reveal);
  });
});

