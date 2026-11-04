
/* =========================================
   CONFIGURACION DE LA API
========================================= */

const API_URL = "http://127.0.0.1:8000";

const USER_ID_KEY = "soporteti_user_id";
const HISTORY_KEY = "soporteti_history";
const APPROVALS_KEY = "soporteti_approvals";

const userId = getUserId();

let conversations = loadData(HISTORY_KEY, []);
let approvals = loadData(APPROVALS_KEY, []);
let currentConversation = null;


/* =========================================
   ELEMENTOS HTML
========================================= */

const chatForm = document.getElementById("chatForm");
const messageInput = document.getElementById("messageInput");
const conversationElement = document.getElementById("conversation");
const sendButton = document.getElementById("sendButton");

const chatSection = document.getElementById("chatSection");
const historySection = document.getElementById("historySection");
const approvalSection = document.getElementById("approvalSection");

const historyList = document.getElementById("historyList");
const approvalList = document.getElementById("approvalList");

const pageTitle = document.getElementById("pageTitle");
const approvalNotice = document.getElementById("approvalNotice");
const approvalCount = document.getElementById("approvalCount");

const welcomeMessage = document.querySelector(".welcome-message");
const quickCards = document.querySelector(".quick-cards");


/* =========================================
   IDENTIFICACION DEL USUARIO
========================================= */

function getUserId() {
    let id = localStorage.getItem(USER_ID_KEY);

    if (!id) {
        const randomId = crypto.randomUUID()
            .replaceAll("-", "")
            .substring(0, 8)
            .toUpperCase();

        id = `USR-${randomId}`;

        localStorage.setItem(USER_ID_KEY, id);
    }

    return id;
}


/* =========================================
   ALMACENAMIENTO LOCAL
========================================= */

function loadData(key, fallback) {
    try {
        return JSON.parse(localStorage.getItem(key)) || fallback;
    } catch {
        return fallback;
    }
}

function saveHistory() {
    localStorage.setItem(
        HISTORY_KEY,
        JSON.stringify(conversations)
    );
}

function saveApprovals() {
    localStorage.setItem(
        APPROVALS_KEY,
        JSON.stringify(approvals)
    );

    updateApprovalCount();
}


/* =========================================
   CREAR CONVERSACIONES
========================================= */

function createConversation() {
    currentConversation = {
        id: crypto.randomUUID(),
        date: new Date().toISOString(),
        messages: []
    };

    conversationElement.innerHTML = "";

    welcomeMessage.classList.remove("hidden");
    quickCards.classList.remove("hidden");

    approvalNotice.classList.add("hidden");

    messageInput.value = "";
    messageInput.focus();

    showSection("chat");
}


/* =========================================
   MOSTRAR MENSAJES
========================================= */

function addMessage(role, content, details = {}) {

    const message = document.createElement("div");

    message.classList.add("message", role);

    const sender = document.createElement("strong");

    sender.textContent = role === "user"
        ? "Tú"
        : "SoporteTI-Agent";

    const text = document.createElement("div");

    text.textContent = content;

    message.appendChild(sender);
    message.appendChild(text);

    if (details.sources?.length) {

        const sources = document.createElement("p");

        sources.textContent =
            "Fuentes consultadas: " +
            details.sources.join(", ");

        sources.style.marginTop = "10px";
        sources.style.fontSize = "11px";

        message.appendChild(sources);
    }

    if (details.next_action) {

        const action = document.createElement("p");

        action.textContent =
            "Siguiente acción: " + details.next_action;

        action.style.marginTop = "8px";
        action.style.fontSize = "11px";

        message.appendChild(action);
    }

    conversationElement.appendChild(message);

    conversationElement.scrollTop =
        conversationElement.scrollHeight;
}


/* =========================================
   GUARDAR MENSAJES
========================================= */

function saveMessage(role, content, details = {}) {

    if (!currentConversation) {
        createConversation();
    }

    const message = {
        role,
        content,
        date: new Date().toISOString(),
        ...details
    };

    currentConversation.messages.push(message);

    let index = conversations.findIndex(
        item => item.id === currentConversation.id
    );

    if (index === -1) {
        conversations.push(currentConversation);
    }

    saveHistory();
}


/* =========================================
   ENVIAR PREGUNTA AL AGENTE
========================================= */

async function sendQuestion(question) {

    const cleanQuestion = question.trim();

    if (cleanQuestion.length < 5) {
        alert("Escribe una pregunta de al menos 5 caracteres.");
        return;
    }

    if (cleanQuestion.length > 500) {
        alert("La pregunta no puede superar 500 caracteres.");
        return;
    }

    if (!currentConversation) {
        createConversation();
    }

    welcomeMessage.classList.add("hidden");
    quickCards.classList.add("hidden");

    approvalNotice.classList.add("hidden");

    addMessage("user", cleanQuestion);

    saveMessage("user", cleanQuestion);

    messageInput.value = "";

    sendButton.disabled = true;
    sendButton.textContent = "Consultando...";

    const loadingMessage = document.createElement("div");

    loadingMessage.classList.add("message", "agent");
    loadingMessage.textContent =
        "SoporteTI-Agent está analizando tu incidencia...";

    conversationElement.appendChild(loadingMessage);

    try {

        const response = await fetch(
            `${API_URL}/agent/ask`,
            {
                method: "POST",

                headers: {
                    "Content-Type": "application/json"
                },

                body: JSON.stringify({
                    question: cleanQuestion,
                    user_id: userId,
                    context: {
                        device: "computador",
                        operating_system: "Windows 11"
                    }
                })
            }
        );

        if (!response.ok) {

            const errorData = await response.json();

            throw new Error(
                errorData.detail ||
                "No fue posible procesar la solicitud."
            );
        }

        const data = await response.json();

        loadingMessage.remove();

        addMessage(
            "agent",
            data.answer,
            {
                sources: data.sources,
                next_action: data.next_action
            }
        );

        saveMessage(
            "agent",
            data.answer,
            {
                sources: data.sources,
                needs_approval: data.needs_approval,
                next_action: data.next_action
            }
        );

        if (data.needs_approval) {

            approvalNotice.classList.remove("hidden");

            approvals.push({
                id: crypto.randomUUID(),
                conversationId: currentConversation.id,
                question: cleanQuestion,
                answer: data.answer,
                next_action: data.next_action,
                date: new Date().toISOString(),
                status: "Pendiente"
            });

            saveApprovals();

            renderApprovals();
        }

        renderHistory();

    } catch (error) {

        loadingMessage.remove();

        addMessage(
            "agent",
            "No pude comunicarme con el servicio de soporte. " +
            error.message +
            ". Verifica que FastAPI esté funcionando."
        );

    } finally {

        sendButton.disabled = false;
        sendButton.textContent = "Enviar ➤";

        messageInput.focus();
    }
}


/* =========================================
   EVENTO DEL FORMULARIO
========================================= */

chatForm.addEventListener("submit", function(event) {

    event.preventDefault();

    sendQuestion(messageInput.value);

});


/* =========================================
   ENTER PARA ENVIAR MENSAJES
========================================= */

messageInput.addEventListener("keydown", function(event) {

    if (event.key === "Enter" && !event.shiftKey) {

        event.preventDefault();

        chatForm.requestSubmit();
    }

});


/* =========================================
   PROBLEMAS FRECUENTES
========================================= */

document.querySelectorAll("[data-question]").forEach(button => {

    button.addEventListener("click", function() {

        const question = this.dataset.question;

        sendQuestion(question);

    });

});


/* =========================================
   NAVEGACION
========================================= */

function showSection(section) {

    chatSection.classList.toggle(
        "hidden",
        section !== "chat"
    );

    historySection.classList.toggle(
        "hidden",
        section !== "history"
    );

    approvalSection.classList.toggle(
        "hidden",
        section !== "approval"
    );

    document.querySelectorAll(".nav-link").forEach(link => {

        link.classList.toggle(
            "active",
            link.dataset.section === section
        );

    });

    const titles = {
        chat: "Chat de soporte",
        history: "Historial de conversaciones",
        approval: "Aprobaciones"
    };

    pageTitle.textContent = titles[section];
}


document.querySelectorAll(".nav-link").forEach(link => {

    link.addEventListener("click", function(event) {

        event.preventDefault();

        const section = this.dataset.section;

        if (section === "history") {
            renderHistory();
        }

        if (section === "approval") {
            renderApprovals();
        }

        showSection(section);

    });

});


/* =========================================
   NUEVO CHAT
========================================= */

document.getElementById("newChat")
    .addEventListener("click", createConversation);


/* =========================================
   MOSTRAR HISTORIAL
========================================= */

function renderHistory() {

    historyList.innerHTML = "";

    if (conversations.length === 0) {

        historyList.innerHTML = `
            <div class="empty-state">
                <span>🕘</span>
                <h3>No hay conversaciones todavía</h3>
                <p>Cuando utilices el agente, aparecerán aquí.</p>
            </div>
        `;

        return;
    }

    [...conversations].reverse().forEach(item => {

        const card = document.createElement("button");

        card.type = "button";
        card.className = "history-card";

        const firstMessage = item.messages.find(
            message => message.role === "user"
        );

        const title = firstMessage
            ? firstMessage.content
            : "Nueva conversación";

        const date = new Date(item.date).toLocaleString("es-CO");

        card.innerHTML = `
            <strong></strong>
            <small></small>
        `;

        card.querySelector("strong").textContent = title;
        card.querySelector("small").textContent = date;

        card.addEventListener("click", () => {
            openConversation(item.id);
        });

        historyList.appendChild(card);

    });

}


/* =========================================
   ABRIR CONVERSACION ANTERIOR
========================================= */

function openConversation(id) {

    const selected = conversations.find(
        item => item.id === id
    );

    if (!selected) return;

    currentConversation = selected;

    conversationElement.innerHTML = "";

    welcomeMessage.classList.add("hidden");
    quickCards.classList.add("hidden");

    selected.messages.forEach(message => {

        addMessage(
            message.role,
            message.content,
            message
        );

    });

    const hasApproval = selected.messages.some(
        message => message.needs_approval
    );

    approvalNotice.classList.toggle(
        "hidden",
        !hasApproval
    );

    showSection("chat");
}


/* =========================================
   MOSTRAR APROBACIONES
========================================= */

function renderApprovals() {

    approvalList.innerHTML = "";

    if (approvals.length === 0) {

        approvalList.innerHTML = `
            <div class="empty-state">
                <span>🛡️</span>
                <h3>No tienes casos pendientes</h3>
                <p>Los casos que necesiten autorización aparecerán aquí.</p>
            </div>
        `;

        return;
    }

    approvals.slice().reverse().forEach(item => {

        const card = document.createElement("div");

        card.className = "approval-card";

        const title = document.createElement("h3");
        title.textContent = item.question;

        const answer = document.createElement("p");
        answer.textContent = item.answer;

        const status = document.createElement("span");
        status.textContent = item.status;

        card.appendChild(title);
        card.appendChild(answer);
        card.appendChild(status);

        approvalList.appendChild(card);

    });

}


/* =========================================
   CONTADOR DE APROBACIONES
========================================= */

function updateApprovalCount() {

    const pending = approvals.filter(
        item => item.status === "Pendiente"
    ).length;

    approvalCount.textContent = pending;
}


/* =========================================
   INICIALIZACION
========================================= */

function initializeApp() {

    renderHistory();

    renderApprovals();

    updateApprovalCount();

    console.log("SoporteTI-Agent iniciado correctamente.");

    console.log("Usuario:", userId);

}

initializeApp();
