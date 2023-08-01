function sendEventTo(btn_id, elm) {
  document.getElementById(btn_id).addEventListener("click", (e) => {
    e.stopPropagation();
    e.preventDefault();
    elm.dispatchEvent(new MouseEvent("click", { bubbles: true }));
  });
}

window.addEventListener("load", () => {
  const profile_img = document.getElementById("profile_img");
  const imgInput = document.getElementById("imgInput");

  imgInput.addEventListener("input", function (e) {
    const [file] = this.files;
    if (file) {
      profile_img.src = URL.createObjectURL(file);
    }
  });

  sendEventTo("setPhotoBtn", imgInput);

  const colorPreview = document.getElementById("colorPreview");
  const colorInput = document.getElementById("colorInput");

  colorInput.addEventListener("input", function () {
    colorPreview.style.background = this.value;
  });

  sendEventTo("colorPreview", colorInput);
});
