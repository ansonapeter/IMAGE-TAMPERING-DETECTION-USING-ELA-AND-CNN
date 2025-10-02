document.addEventListener("DOMContentLoaded", () => {
    const dropZone = document.getElementById("drop-zone");
    const fileInput = document.getElementById("fileInput");
    const uploadBtn = document.getElementById("uploadBtn");
    const resultsDiv = document.getElementById("results");

    let selectedFile = null;
    let localPreviewURL = null; // store JPG preview from server

    // Click to upload
    dropZone.addEventListener("click", () => fileInput.click());

    // Drag over effect
    dropZone.addEventListener("dragover", (e) => {
        e.preventDefault();
        dropZone.classList.add("dragover");
    });

    dropZone.addEventListener("dragleave", () => {
        dropZone.classList.remove("dragover");
    });

    // File dropped
    dropZone.addEventListener("drop", (e) => {
        e.preventDefault();
        dropZone.classList.remove("dragover");
        selectedFile = e.dataTransfer.files[0];
        previewImage(selectedFile);
    });

    // File selected via input
    fileInput.addEventListener("change", (e) => {
        selectedFile = e.target.files[0];
        previewImage(selectedFile);
    });

    // Upload and analyze
    uploadBtn.addEventListener("click", async () => {
        if (!selectedFile) {
            alert("Please select an image first!");
            return;
        }

        const formData = new FormData();
        formData.append("image", selectedFile);

        resultsDiv.innerHTML = `<p>Analyzing... Please wait.</p>`;

        try {
            const response = await fetch("/analyze", {
                method: "POST",
                body: formData
            });

            const data = await response.json();
            displayResults(data);
        } catch (err) {
            console.error(err);
            resultsDiv.innerHTML = `<p style="color:red;">Error analyzing image.</p>`;
        }
    });

    // Preview image via server conversion to JPG
    function previewImage(file) {
        if (!file.type.startsWith("image/")) {
            alert("Only image files are allowed!");
            return;
        }

        const formData = new FormData();
        formData.append("image", file);

        fetch("/preview", {
            method: "POST",
            body: formData
        })
        .then(res => res.json())
        .then(data => {
            if (data.error) {
                alert("Preview error: " + data.error);
                return;
            }
            localPreviewURL = data.preview_image; // JPG from server
            resultsDiv.innerHTML = `
                <div class="preview">
                    <h3>Selected Image:</h3>
                    <img src="${localPreviewURL}" alt="Preview" class="preview-img">
                </div>
            `;
        })
        .catch(err => {
            console.error(err);
            alert("Error generating preview.");
        });
    }

    // New: Original → Prediction → ELA
    function displayResults(data) {
        const color = data.result.toLowerCase() === "real" ? "green" : "red";

        resultsDiv.innerHTML = `
            <div class="result-container">
                <div>
                    <h3>Original Image:</h3>
                    <img src="${data.original_image}" alt="Uploaded JPG" class="preview-img">
                </div>
                <div>
                    <h3>Prediction:</h3>
                    <p style="color:${color}; font-weight:bold; font-size:18px;">
                        ${data.result}
                    </p>
                    <p>Confidence: ${data.confidence}%</p>
                </div>
                <div>
                    <h3>ELA Image:</h3>
                    <img src="${data.ela_image}" alt="ELA Result" class="preview-img">
                </div>
            </div>
        `;
    }
});
