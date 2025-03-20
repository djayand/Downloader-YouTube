function showMessage(message, type) {
    const messageBox = document.getElementById(type + '-box');
    if (messageBox) {
        messageBox.textContent = message;
        messageBox.style.display = 'block';
        setTimeout(() => {
            messageBox.style.display = 'none';
        }, 5000);
    }
}

window.onload = function () {
    const downloadUrl = document.getElementById("download-url").value;
    const hasFile = document.getElementById("has-file").value === "true";

    // Vérifie si le téléchargement a déjà été lancé pour éviter la boucle infinie
    if (hasFile && !sessionStorage.getItem("download_completed")) {
        sessionStorage.setItem("download_started", "true");  // Marquer le téléchargement comme lancé
        window.location.href = downloadUrl;
    }
};
