let cameraStream = null;
let capturedImage = null;
let faceLandmarks = [];
let lastAnalysisResult = null;

function startAnalysis() {
    const section = document.getElementById("analysis");

    if (section) {
        section.scrollIntoView({
            behavior: "smooth"
        });
    }
}

function scrollToFeatures() {
    const section = document.getElementById("features");

    if (section) {
        section.scrollIntoView({
            behavior: "smooth"
        });
    }
}

function scrollToMakeup() {
    const section = document.getElementById("makeup");

    if (section) {
        section.scrollIntoView({
            behavior: "smooth"
        });
    }
}

function scrollToHairstyle() {
    const section = document.getElementById("hairstyle");

    if (section) {
        section.scrollIntoView({
            behavior: "smooth"
        });
    }
}


// ======================================
// OPEN CAMERA
// ======================================

async function openCamera() {

    console.log("🌸 Open Camera clicked");

    const video = document.getElementById("camera");
    const container = document.getElementById("camera-container");
    const startArea = document.getElementById("camera-start-area");
    const status = document.getElementById("status");

    if (!video) {
        status.textContent = "Camera preview is unavailable on this page.";
        return;
    }

    if (!navigator.mediaDevices ||
        !navigator.mediaDevices.getUserMedia) {

        status.textContent = "This browser does not support camera access. Upload a photo instead.";
        return;
    }

    const openButton = document.getElementById("openCameraButton");
    if (openButton) openButton.disabled = true;
    status.textContent = "Requesting camera access…";
    try {
        if (cameraStream && cameraStream.getVideoTracks().some(track => track.readyState === "live")) {
            container.classList.remove("hidden");
            if (startArea) startArea.classList.add("hidden");
            status.textContent = "Camera ready. Center your face and capture a photo.";
            return;
        }
        cameraStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: "user" },
            audio: false
        });

        video.srcObject = cameraStream;

        await video.play();

        container.classList.remove("hidden");

        if (startArea) {
            startArea.classList.add("hidden");
        }

        console.log("✅ Camera opened successfully");
        status.textContent = "Camera ready. Center your face and capture a photo.";

    } catch (error) {

        console.error("❌ Camera error:", error);
        if (cameraStream) {
            cameraStream.getTracks().forEach(track => track.stop());
            cameraStream = null;
        }
        video.srcObject = null;

        if (error.name === "NotAllowedError") {
            status.textContent = "Camera permission is blocked. Allow camera access for localhost in your browser settings, then try again. You can also upload a photo.";
        } else if (error.name === "NotFoundError") {
            status.textContent = "No camera was found. Connect a camera or upload a photo.";
        } else if (error.name === "NotReadableError" || error.name === "AbortError") {
            status.textContent = "The camera is busy in another app or browser tab. Close other camera apps/tabs, then try again—or upload a photo.";
        } else if (error.name === "SecurityError") {
            status.textContent = "Camera access is blocked by browser security. Open the app on localhost and allow camera access, or upload a photo.";
        } else {
            status.textContent = `Camera could not be opened (${error.name}). Upload a photo or check browser camera settings.`;
        }
    } finally {
        if (openButton) openButton.disabled = false;
    }
}


// ======================================
// STOP CAMERA
// ======================================

function stopCamera() {

    if (cameraStream) {

        cameraStream.getTracks().forEach(
            track => track.stop()
        );

        cameraStream = null;
    }

    const video =
        document.getElementById("camera");

    const container =
        document.getElementById("camera-container");

    const startArea =
        document.getElementById("camera-start-area");

    if (video) {
        video.srcObject = null;
    }

    if (container) {
        container.classList.add("hidden");
    }

    if (startArea) {
        startArea.classList.remove("hidden");
    }

}


// ======================================
// CAPTURE FACE
// ======================================


async function captureFace() {
    const video = document.getElementById("camera");
    const canvas = document.getElementById("snapshot");
    if (!video || !video.videoWidth || !video.videoHeight || !canvas) {
        document.getElementById("status").textContent = "Camera is not ready yet.";
        return;
    }

    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    const context = canvas.getContext("2d");
    context.drawImage(video, 0, 0, canvas.width, canvas.height);
    stopCamera();
    const blob = await new Promise(resolve => canvas.toBlob(resolve, "image/jpeg", 0.92));
    if (!blob) {
        document.getElementById("status").textContent = "Could not create the captured photo.";
        return;
    }
    await analyzePhoto(blob, "captured_face.jpg");
}

async function analyzeUploadedPhoto(event) {
    const file = event.target.files[0];
    if (!file) return;
    stopCamera();
    if (!file.type.startsWith("image/")) {
        document.getElementById("status").textContent = "Choose a valid image file.";
        event.target.value = "";
        return;
    }
    if (file.size > 10 * 1024 * 1024) {
        document.getElementById("status").textContent = "Image must be 10 MB or smaller.";
        event.target.value = "";
        return;
    }
    await analyzePhoto(file, file.name || "uploaded_face.jpg");
}

async function analyzePhoto(blob, filename) {
    const result = document.getElementById("result");
    const resultText = document.getElementById("result-text");
    const tryOn = document.getElementById("makeup-tryon");
    const tryOnEmpty = document.getElementById("makeup-empty");
    const status = document.getElementById("status");
    result.classList.remove("hidden");
    resultText.textContent = "Sending your photo to GlowPetals AI for analysis…";
    status.textContent = "Analyzing photo on the backend…";
    tryOn.classList.add("hidden");
    tryOnEmpty.classList.remove("hidden");
    const progressTimer = window.setTimeout(() => {
        if (status.textContent === "Analyzing photo on the backend…") {
            status.textContent = "First scan can take up to 30 seconds while the face detector initializes. Please keep this page open.";
        }
    }, 5000);

    const previewUrl = URL.createObjectURL(blob);
    try {
        capturedImage = await new Promise((resolve, reject) => {
            const image = new Image();
            image.onload = () => resolve(image);
            image.onerror = () => reject(new Error("Could not open this image."));
            image.src = previewUrl;
        });

        const formData = new FormData();
        formData.append("image", blob, filename);
        formData.append("profile", document.getElementById("profile").value);

        const controller = new AbortController();
        const timeout = window.setTimeout(() => controller.abort(), 90000);
        let response;
        try {
            response = await fetch("/analyze", {
                method: "POST",
                body: formData,
                signal: controller.signal
            });
        } finally {
            window.clearTimeout(timeout);
        }
        const data = await response.json();
        if (!response.ok || !data.success) {
            throw new Error(data.message || "Face analysis failed.");
        }

        if (data.analysis && data.analysis.face_detected) {
            faceLandmarks = data.analysis.landmarks || [];
            lastAnalysisResult = {
                profile: data.profile,
                analysis: data.analysis,
                recommendations: data.recommendations
            };
            renderRecommendations(data.recommendations || {});
            const skin = data.analysis.skin_appearance || {};
            resultText.innerHTML = `
                <h3>Analysis completed</h3>
                <p><strong>Profile:</strong> ${data.profile}</p>
                <p><strong>Faces found:</strong> ${data.analysis.face_count}</p>
                <p><strong>Estimated face shape:</strong> ${data.analysis.face_shape}</p>
                <p><strong>Estimated skin appearance:</strong> ${skin.estimated_skin_type || skin.label || "Unavailable"} (low confidence)</p>
                <p><strong>Visible-shine estimate:</strong> ${skin.visible_shine_percent ?? "Unavailable"}${skin.visible_shine_percent == null ? "" : "%"}</p>
                <p><strong>Estimated complexion:</strong> ${skin.skin_tone_label || "Unavailable"} (low confidence)</p>
                <p class="estimate-note">This estimates visible shine, not dry or sensitive skin. Lighting, makeup and camera settings can affect photo-based estimates.</p>
            `;
            tryOn.classList.remove("hidden");
            tryOnEmpty.classList.add("hidden");
            status.textContent = "Face analysis complete. Your suggestions and virtual try-on are ready.";
            applyMakeup();
        } else {
            faceLandmarks = [];
            lastAnalysisResult = null;
            capturedImage = null;
            document.getElementById("recommendation-list").replaceChildren();
            resultText.textContent = data.message || "No face detected. Try a clear, front-facing photo.";
            status.textContent = "No face detected. Try a brighter, front-facing photo.";
        }
    } catch (error) {
        console.error("Face analysis request failed:", error);
        const message = error.name === "AbortError"
            ? "Face analysis timed out. Please try again with a smaller, clear photo."
            : error.message || "Could not connect to the analysis service.";
        resultText.textContent = message;
        status.textContent = message;
        faceLandmarks = [];
        lastAnalysisResult = null;
        capturedImage = null;
    } finally {
        window.clearTimeout(progressTimer);
        URL.revokeObjectURL(previewUrl);
    }
}

function renderRecommendations(recommendations) {
    const container = document.getElementById("recommendation-list");
    if (!container) return;

    container.replaceChildren();
    const categories = recommendations.face_shape_matches || {};
    const groups = Object.entries(categories);
    const skinProducts = recommendations.skin_product_guidance || [];
    const makeupProducts = recommendations.makeup_product_guidance || [];

    const createProductCard = (product) => {
        const card = document.createElement("a");
        card.className = "product-card";
        card.href = product.url;
        card.target = "_blank";
        card.rel = "noopener noreferrer";

        if (product.image) {
            const image = document.createElement("img");
            image.src = product.image;
            image.alt = `${product.brand} ${product.name} product image`;
            image.loading = "lazy";
            image.decoding = "async";
            image.addEventListener("error", () => {
                const placeholder = document.createElement("div");
                placeholder.className = "product-image-placeholder";
                placeholder.textContent = product.type;
                placeholder.setAttribute("aria-label", `${product.type} product image unavailable`);
                image.replaceWith(placeholder);
            }, { once: true });
            card.append(image);
        } else {
            const placeholder = document.createElement("div");
            placeholder.className = "product-image-placeholder";
            placeholder.textContent = product.type;
            placeholder.setAttribute("aria-label", `${product.type} product`);
            card.append(placeholder);
        }

        const details = document.createElement("div");
        details.className = "product-details";
        const brand = document.createElement("strong");
        brand.textContent = product.brand;
        const name = document.createElement("span");
        name.textContent = product.name;
        const type = document.createElement("small");
        type.textContent = product.type;
        const reason = document.createElement("p");
        reason.textContent = product.why;
        details.append(brand, name, type, reason);
        card.append(details);
        return card;
    };

    for (const [category, items] of groups) {
        const section = document.createElement("section");
        const heading = document.createElement("h4");
        heading.textContent = category;
        const list = document.createElement("ul");
        for (const item of items) {
            const entry = document.createElement("li");
            entry.textContent = item;
            list.append(entry);
        }
        section.append(heading, list);
        container.append(section);
    }

    if (skinProducts.length || recommendations.skin_product_note) {
        const productSection = document.createElement("section");
        const productHeading = document.createElement("h4");
        productHeading.textContent = skinProducts.length
            ? `Skincare picks for ${recommendations.skin_match_label || "your face scan"}`
            : "Skincare guidance";
        productSection.append(productHeading);
        if (skinProducts.length) {
            const productGrid = document.createElement("div");
            productGrid.className = "product-grid";
            for (const product of skinProducts) {
                productGrid.append(createProductCard(product));
            }
            productSection.append(productGrid);
        }
        if (recommendations.skin_product_note) {
            const skincareNote = document.createElement("p");
            skincareNote.className = "recommendation-note";
            skincareNote.textContent = recommendations.skin_product_note;
            productSection.append(skincareNote);
        }
        container.append(productSection);
    }

    if (makeupProducts.length) {
        const productSection = document.createElement("section");
        const productHeading = document.createElement("h4");
        productHeading.textContent = "Makeup picks";
        const productGrid = document.createElement("div");
        productGrid.className = "product-grid";

        for (const product of makeupProducts) {
            productGrid.append(createProductCard(product));
        }

        productSection.append(productHeading, productGrid);
        container.append(productSection);
    }

    if (recommendations.product_catalog_note) {
        const note = document.createElement("p");
        note.className = "recommendation-note";
        note.textContent = recommendations.product_catalog_note;
        container.append(note);
    }

    const braidSection = document.createElement("section");
    const braidHeading = document.createElement("h4");
    braidHeading.textContent = "Braided styles by occasion";
    braidSection.append(braidHeading);
    const occasionSelect = document.createElement("select");
    occasionSelect.setAttribute("aria-label", "Choose braid occasion");
    const braidList = document.createElement("ul");
    const braidOptions = recommendations.occasion_braids || {};
    for (const occasion of Object.keys(braidOptions)) {
        const option = document.createElement("option");
        option.value = occasion;
        option.textContent = occasion;
        occasionSelect.append(option);
    }
    const updateBraids = () => {
        braidList.replaceChildren();
        for (const style of braidOptions[occasionSelect.value] || []) {
            const item = document.createElement("li");
            item.textContent = style;
            braidList.append(item);
        }
    };
    occasionSelect.addEventListener("change", updateBraids);
    braidSection.append(occasionSelect, braidList);
    container.append(braidSection);
    updateBraids();
}

function applyMakeup() {
    const preview = document.getElementById("makeup-preview");
    const status = document.getElementById("makeup-status");
    if (!preview || !capturedImage || !capturedImage.complete || !capturedImage.naturalWidth || faceLandmarks.length < 455) {
        if (status) status.textContent = "Capture and analyze a face before applying makeup.";
        return;
    }

    const context = preview.getContext("2d");
    const width = capturedImage.naturalWidth;
    const height = capturedImage.naturalHeight;
    preview.width = width;
    preview.height = height;
    context.clearRect(0, 0, width, height);
    context.drawImage(capturedImage, 0, 0, width, height);

    const point = (index) => ({
        x: faceLandmarks[index].x * width,
        y: faceLandmarks[index].y * height
    });
    const intensity = Number(document.getElementById("makeup-strength").value) / 100;
    const baseAlpha = Math.min(0.95, 0.1 + intensity * 0.9);
    const lipColor = document.getElementById("lip-color").value;
    const blushColor = document.getElementById("blush-color").value;
    const bronzerColor = document.getElementById("bronzer-color").value;
    const highlighterColor = document.getElementById("highlighter-color").value;

    const drawSoftEllipse = (cx, cy, rx, ry, color, alpha, blur = 18, rotation = 0) => {
        context.save();
        context.globalAlpha = alpha;
        context.fillStyle = color;
        context.filter = `blur(${blur}px)`;
        context.beginPath();
        context.ellipse(cx, cy, rx, ry, rotation, 0, Math.PI * 2);
        context.fill();
        context.restore();
    };

    if (document.getElementById("foundation-toggle").checked) {
        const foundationAlpha = baseAlpha * 0.22;
        const faceCenter = point(10);
        const leftCheek = point(234);
        const rightCheek = point(454);
        drawSoftEllipse(faceCenter.x, faceCenter.y, width * 0.21, height * 0.29, "#f5d7c7", foundationAlpha, 20);
        drawSoftEllipse(leftCheek.x, leftCheek.y, width * 0.08, height * 0.12, "#f5d7c7", foundationAlpha, 18);
        drawSoftEllipse(rightCheek.x, rightCheek.y, width * 0.08, height * 0.12, "#f5d7c7", foundationAlpha, 18);
    }

    if (document.getElementById("concealer-toggle").checked) {
        const underEyeLeft = point(133);
        const underEyeRight = point(362);
        drawSoftEllipse(underEyeLeft.x, underEyeLeft.y + height * 0.018, width * 0.045, height * 0.028, "#f9ebdd", baseAlpha * 0.28, 16);
        drawSoftEllipse(underEyeRight.x, underEyeRight.y + height * 0.018, width * 0.045, height * 0.028, "#f9ebdd", baseAlpha * 0.28, 16);
    }

    if (document.getElementById("blush-toggle").checked) {
        const blur = Math.max(8, width * 0.025);
        for (const cheekIndex of [205, 425]) {
            const cheek = point(cheekIndex);
            drawSoftEllipse(cheek.x, cheek.y, width * 0.055, height * 0.035, blushColor, baseAlpha * 0.35, blur);
        }
    }

    if (document.getElementById("bronzer-toggle").checked) {
        const leftJaw = point(179);
        const rightJaw = point(443);
        drawSoftEllipse(leftJaw.x, leftJaw.y, width * 0.055, height * 0.05, bronzerColor, baseAlpha * 0.18, 16);
        drawSoftEllipse(rightJaw.x, rightJaw.y, width * 0.055, height * 0.05, bronzerColor, baseAlpha * 0.18, 16);
    }

    if (document.getElementById("highlighter-toggle").checked) {
        const browLeft = point(70);
        const browRight = point(300);
        drawSoftEllipse(browLeft.x, browLeft.y - height * 0.02, width * 0.025, height * 0.022, highlighterColor, baseAlpha * 0.45, 16);
        drawSoftEllipse(browRight.x, browRight.y - height * 0.02, width * 0.025, height * 0.022, highlighterColor, baseAlpha * 0.45, 16);
        const noseTip = point(6);
        drawSoftEllipse(noseTip.x, noseTip.y, width * 0.018, height * 0.04, highlighterColor, baseAlpha * 0.45, 12);
    }

    if (document.getElementById("mascara-toggle").checked) {
        const lashStyles = [
            [133, 246, 161, 160, 159],
            [362, 466, 387, 386, 385],
        ];
        lashStyles.forEach((indexes) => {
            context.save();
            context.strokeStyle = "#514238";
            context.globalAlpha = baseAlpha * 0.9;
            context.lineWidth = Math.max(1, width * 0.0018);
            context.lineCap = "round";
            context.beginPath();
            indexes.forEach((index, position) => {
                const coordinates = point(index);
                if (position === 0) context.moveTo(coordinates.x, coordinates.y);
                else context.lineTo(coordinates.x, coordinates.y);
            });
            context.stroke();
            context.restore();
        });
    }

    const outerLip = [61, 146, 91, 181, 84, 17, 314, 405, 321, 375, 291, 409, 270, 269, 267, 0, 37, 39, 40, 185];
    const innerLip = [78, 95, 88, 178, 87, 14, 317, 402, 318, 324, 308, 415, 310, 311, 312, 13, 82, 81, 80, 191];

    const mask = document.createElement("canvas");
    mask.width = width;
    mask.height = height;
    const maskContext = mask.getContext("2d");
    maskContext.fillStyle = "white";
    maskContext.beginPath();
    outerLip.forEach((index, position) => {
        const coordinates = point(index);
        if (position === 0) maskContext.moveTo(coordinates.x, coordinates.y);
        else maskContext.lineTo(coordinates.x, coordinates.y);
    });
    maskContext.closePath();
    maskContext.fill();
    maskContext.globalCompositeOperation = "destination-out";
    maskContext.beginPath();
    innerLip.forEach((index, position) => {
        const coordinates = point(index);
        if (position === 0) maskContext.moveTo(coordinates.x, coordinates.y);
        else maskContext.lineTo(coordinates.x, coordinates.y);
    });
    maskContext.closePath();
    maskContext.fill();

    const tint = document.createElement("canvas");
    tint.width = width;
    tint.height = height;
    const tintContext = tint.getContext("2d");
    tintContext.fillStyle = lipColor;
    tintContext.fillRect(0, 0, width, height);
    tintContext.globalCompositeOperation = "destination-in";
    tintContext.drawImage(mask, 0, 0);

    context.save();
    context.globalAlpha = Math.min(0.95, baseAlpha * 0.9);
    context.globalCompositeOperation = "multiply";
    context.filter = "blur(0.35px)";
    context.drawImage(tint, 0, 0);
    context.restore();

    if (status) status.textContent = "Makeup applied to the captured photo. Change the shade or intensity to update the preview.";
}

function applyNaturalMakeup() {
    const setChecked = (id, checked) => {
        document.getElementById(id).checked = checked;
    };
    document.getElementById("makeup-strength").value = "8";
    document.getElementById("lip-color").value = "#b96f71";
    document.getElementById("blush-color").value = "#d98782";
    document.getElementById("bronzer-color").value = "#a67d62";
    document.getElementById("highlighter-color").value = "#e7c9a4";
    setChecked("foundation-toggle", true);
    setChecked("concealer-toggle", true);
    setChecked("blush-toggle", true);
    setChecked("bronzer-toggle", false);
    setChecked("highlighter-toggle", false);
    setChecked("mascara-toggle", true);
    applyMakeup();
}

async function refreshRecommendations() {
    if (!lastAnalysisResult) {
        console.log("No previous analysis result to refresh from.");
        return;
    }

    const profile = document.getElementById("profile").value || lastAnalysisResult.profile;
    try {
        const response = await fetch("/recommendations", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({
                profile,
                face_shape: lastAnalysisResult.analysis.face_shape,
                skin_appearance: lastAnalysisResult.analysis.skin_appearance
            })
        });

        if (!response.ok) throw new Error("Failed to refresh recommendations.");

        const data = await response.json();
        if (data.recommendations) {
            renderRecommendations(data.recommendations);
        }
    } catch (error) {
        console.error("Recommendation refresh failed:", error);
    }
}

document.addEventListener("DOMContentLoaded", () => {
    document.addEventListener("visibilitychange", () => {
        if (document.hidden) stopCamera();
    });
    window.addEventListener("pagehide", stopCamera);

    const imageUpload = document.getElementById("image-upload");
    if (imageUpload) {
        imageUpload.addEventListener("change", analyzeUploadedPhoto);
    }

    [
        "makeup-strength",
        "lip-color",
        "blush-color",
        "bronzer-color",
        "highlighter-color",
        "foundation-toggle",
        "concealer-toggle",
        "blush-toggle",
        "bronzer-toggle",
        "highlighter-toggle",
        "mascara-toggle"
    ].forEach((id) => {
        const element = document.getElementById(id);
        if (element) {
            const eventName = element.type === "checkbox" ? "change" : "input";
            element.addEventListener(eventName, applyMakeup);
        }
    });

    ["profile"].forEach((id) => {
        const element = document.getElementById(id);
        if (element) {
            element.addEventListener("change", refreshRecommendations);
        }
    });
});