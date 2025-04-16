   // static/js/script.js
   function getCookie(name) {
       const cookieArr = document.cookie.split(";");
       for (let i = 0; i < cookieArr.length; i++) {
           const cookiePair = cookieArr[i].trim();
           if (cookiePair.startsWith(name + "=")) {
               return cookiePair.split("=")[1];
           }
       }
       return null;
   }

function sendToken(event) {
    event.preventDefault(); // Отменяем стандартное поведение формы
    const token = getCookie("access_token");
    if (token) {
        const xhr = new XMLHttpRequest();
        xhr.open(event.target.method, event.target.action, true);
        xhr.setRequestHeader("Authorization", "Bearer " + token);
        xhr.onload = function() {
            if (xhr.status >= 200 && xhr.status < 300) {
                const contentType = xhr.getResponseHeader("Content-Type");
                if (contentType.includes("application/json")) {
                    const response = JSON.parse(xhr.responseText);
                    if (response.redirect_url) {
                        window.location.href = response.redirect_url;
                    }
                } else if (contentType.includes("text/html")) {
                    document.open();
                    document.write(xhr.responseText);
                    document.close();
                }
            } else {
                console.error("Ошибка при отправке запроса:", xhr.statusText);
            }
        };

        xhr.send(new FormData(event.target));
    } else {
        console.error("Token not found");
        window.location.href = "/login";
    }
}


document.addEventListener("DOMContentLoaded", () => {
    const forms = [
        "multi-player-form",
        "single-player-form",
        "find-user",
        "send-invitation",
        "delete-game",
        "accepted-user",
        "reject-user",
        "wait-status",
        "wait-user",
        "refresh-token",
        "find-user-token",
        "history-games",
        "all-history-games",
        "table-best-user",
        "top-Users-Form",

    ];

    forms.forEach(formId => {
        const form = document.getElementById(formId);
        if (form) {
            form.addEventListener("submit", sendToken);
        }
    });
});
