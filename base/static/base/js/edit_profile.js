window.addEventListener("load", () => {
  const profile_img = document.getElementById("profile_img");
  document.getElementById("img_input").addEventListener("input", function (e) {
    const [file] = this.files;
    if (file) {
      profile_img.src = URL.createObjectURL(file);
    }
  });
});
