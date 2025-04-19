document.addEventListener("DOMContentLoaded", function () {
    const form = document.querySelector("form");
    form.addEventListener("submit", function (e) {
        e.preventDefault();
        const url = form.querySelector("input[name='url']").value;
        const format = form.querySelector("select[name='format']").value;

        document.getElementById("progress-bar").style.display = "block";
        document.getElementById("bar").style.width = "0%";

        // Réinitialiser la timeline
        document.getElementById("status-log").innerHTML = "";

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
    const logSet = new Set(); // éviter les doublons
    const logContainer = document.getElementById("status-log");

    const interval = setInterval(() => {
        fetch(`/status/${taskId}`)
            .then(res => res.json())
            .then(status => {
                const logList = status.log || [];

                // Ajouter tous les nouveaux messages
                logList.forEach(msg => {
                    if (!logSet.has(msg)) {
                        const li = document.createElement("li");
                        li.textContent = msg;
                        logContainer.appendChild(li);
                        logSet.add(msg);
                    }
                });

                // Mise à jour de la barre : on suppose 6 étapes pour 100%
                const percent = Math.min((logList.length / 6) * 100, 100);
                document.getElementById("bar").style.width = percent + "%";

                if (status.status !== 'processing') {
                    clearInterval(interval);

                    showMessage(logList.at(-1), status.status);

                    if (status.status === 'success') {
                        document.getElementById("download-url").value = `/download?task_id=${taskId}`;
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
        messageBox.classList.remove('hidden');
        setTimeout(() => {
            messageBox.classList.add('hidden');
        }, 5000);
    }
}