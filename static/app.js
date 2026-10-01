const form = document.getElementById("form");
const fileInput = document.getElementById("file");
const dropzone = document.getElementById("dropzone");
const fileText = document.getElementById("fileText");
const password = document.getElementById("password");
const toggle = document.getElementById("toggle");
const submit = document.getElementById("submit");
const status = document.getElementById("status");

function setFile(file) {
  if (!file) return;
  if (!file.name.toLowerCase().endsWith(".pdf")) {
    status.textContent = "Please select a PDF file.";
    return;
  }
  const dt = new DataTransfer();
  dt.items.add(file);
  fileInput.files = dt.files;
  fileText.textContent = file.name;
  status.textContent = "";
}

fileInput.addEventListener("change", () => setFile(fileInput.files[0]));

["dragenter", "dragover"].forEach(event =>
  dropzone.addEventListener(event, e => {
    e.preventDefault();
    dropzone.classList.add("dragging");
  })
);

["dragleave", "drop"].forEach(event =>
  dropzone.addEventListener(event, e => {
    e.preventDefault();
    dropzone.classList.remove("dragging");
  })
);

dropzone.addEventListener("drop", e => setFile(e.dataTransfer.files[0]));

toggle.addEventListener("click", () => {
  const visible = password.type === "text";
  password.type = visible ? "password" : "text";
  toggle.textContent = visible ? "Show" : "Hide";
});

form.addEventListener("submit", async e => {
  e.preventDefault();

  if (!fileInput.files[0]) {
    status.textContent = "Please choose a PDF.";
    return;
  }

  submit.disabled = true;
  submit.textContent = "Processing...";
  status.textContent = "Unlocking PDF...";

  const data = new FormData();
  data.append("file", fileInput.files[0]);
  data.append("password", password.value);

  try {
    const response = await fetch("/api/remove-password", {
      method: "POST",
      body: data
    });

    if (!response.ok) {
      const result = await response.json().catch(() => ({}));
      throw new Error(result.error || "Unable to process the PDF.");
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = fileInput.files[0].name.replace(/\.pdf$/i, "") + "_unlocked.pdf";
    document.body.appendChild(a);
    a.click();
    a.remove();
    URL.revokeObjectURL(url);

    status.textContent = "Done. Your unlocked PDF has been downloaded.";
  } catch (err) {
    status.textContent = err.message;
  } finally {
    submit.disabled = false;
    submit.textContent = "Remove Password";
  }
});
