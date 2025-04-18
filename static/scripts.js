document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const url = form.querySelector("input[name='url']").value;
        const format = form.querySelector("select[name='format']").value;

        document.getElementById("progress-bar").style.display = "block";
        document.getElementById("bar").style.width = "30%";
        document.getElementById("progress-message").textContent = "⏳ Téléchargement en cours...";

        fetch("/", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: `url=${encodeURIComponent(url)}&format=${format}`
        })
        .then(response => response.json())
        .then(data => {
            if (data.task_id) {
                checkStatus(data.task_id);
            }
        });
    });
});

function checkStatus(taskId) {
    const interval = setInterval(() => {
        fetch(`/status/${taskId}`)
            .then(res => res.json())
            .then(status => {
                if (status.status === 'processing') {
                    document.getElementById("bar").style.width = "60%";
                    document.getElementById("progress-message").textContent = status.message;
                } else {
                    clearInterval(interval);
                    document.getElementById("bar").style.width = "100%";
                    document.getElementById("progress-message").textContent = status.message;

                    showMessage(status.message, status.status);

                    if (status.status === 'success') {
                        setTimeout(() => window.location.href = document.getElementById("download-url").value, 2000);
                    }
                }
            });
    }, 1000);
}

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
