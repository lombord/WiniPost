function sendEventTo(btn_id, elm) {
  document.getElementById(btn_id).addEventListener("click", (e) => {
    e.stopPropagation();
    e.preventDefault();
    elm.dispatchEvent(new MouseEvent("click"));
  });
}

function setColorInput(colorInput) {
  const colorPreview = document.getElementById("colorPreview");
  colorPreview.style.backgroundColor = colorInput.value;

  colorInput.addEventListener("input", function () {
    colorPreview.style.background = this.value;
  });

  sendEventTo("colorPreview", colorInput);
}

function setImgInput(imgInput) {
  const editImg = document.getElementById("editImg");

  imgInput.addEventListener("input", function (e) {
    const [file] = this.files;
    if (file) {
      editImg.src = URL.createObjectURL(file);
    }
  });

  sendEventTo("setImgBtn", imgInput);
}

window.addEventListener("load", () => {
  const imgInput = document.querySelector("#imgBox > input[type='file']");
  imgInput && setImgInput(imgInput);

  const colorInput = document.querySelector("#colorBox > input");
  colorInput && setColorInput(colorInput);
});
