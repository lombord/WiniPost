const htmlElm = document.querySelector("html");

function loadTheme() {
  htmlElm.setAttribute(
    "data-bs-theme",
    localStorage.getItem("theme") || "light"
  );
  document.getElementById("theme-toggler").addEventListener("click", () => {
    if (htmlElm.getAttribute("data-bs-theme") == "light") {
      htmlElm.setAttribute("data-bs-theme", "dark");
      localStorage.setItem("theme", "dark");
    } else {
      htmlElm.setAttribute("data-bs-theme", "light");
      localStorage.setItem("theme", "light");
    }
  });
}

function fixTextArea() {
  document.querySelectorAll("textarea").forEach((elm) => {
    elm.addEventListener("input", () => {
      elm.style.height = "";
      elm.style.height = `${elm.scrollHeight + 10}px`;
    });
    elm.dispatchEvent(new Event("input"));
  });
}

async function cleanFlashMessages() {
  const messages = document.querySelectorAll(".flash-message");

  for (const msg of messages) {
    await new Promise((r) =>
      setTimeout(() => {
        setTimeout(() => {
          msg.classList.add("opacity-animation");
          setTimeout(() => {
            msg.remove();
          }, 300);
        }, 5000);
        r();
      }, 600)
    );
  }
}

function main() {
  fixTextArea();
  loadTheme();
  cleanFlashMessages();
}

window.onload = main;
