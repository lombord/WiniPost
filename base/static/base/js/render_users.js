window.addEventListener("load", () => {
  document.querySelectorAll(".user-thumbnail").forEach((elm) => {
    elm.addEventListener("click", () => {
      window.location.assign(elm.attributes.href.value);
    });
  });
});
