const state = { token: localStorage.getItem("atlas_token"), user: null, documents: [], selected: null, conversation: null, register: false };
const $ = (selector) => document.querySelector(selector);

async function request(url, options = {}) {
  const headers = new Headers(options.headers || {});
  if (state.token) headers.set("Authorization", `Bearer ${state.token}`);
  const response = await fetch(url, { ...options, headers });
  const body = await response.json().catch(() => ({}));
  if (response.status === 401) logout();
  if (!response.ok) throw new Error(body.detail || "Ошибка запроса");
  return body;
}

function setAuthenticated(auth) {
  state.token = auth.access_token;
  state.user = auth;
  localStorage.setItem("atlas_token", state.token);
  $("#auth-view").classList.add("hidden");
  $("#app-view").classList.remove("hidden");
  $("#user-email").textContent = auth.email;
  loadDocuments().catch(showUploadError);
}

function logout() {
  state.token = null;
  localStorage.removeItem("atlas_token");
  $("#app-view").classList.add("hidden");
  $("#auth-view").classList.remove("hidden");
}

function showUploadError(error) { $("#upload-status").textContent = error.message; }

function renderDocuments() {
  $("#document-count").textContent = state.documents.length;
  $("#document-tabs").replaceChildren(...state.documents.map((item) => {
    const button = document.createElement("button");
    button.className = `tab ${state.selected?.id === item.id ? "active" : ""}`;
    button.type = "button";
    button.innerHTML = `<strong>${escapeHtml(item.topic)}</strong><small>${escapeHtml(item.filename)}</small>`;
    button.addEventListener("click", () => selectDocument(item));
    return button;
  }));
}

function renderConversations(items) {
  $("#conversation-tabs").replaceChildren(...items.map((item) => {
    const button = document.createElement("button");
    button.className = `tab ${state.conversation?.id === item.id ? "active" : ""}`;
    button.type = "button";
    button.textContent = item.title;
    button.addEventListener("click", () => loadConversation(item.id));
    return button;
  }));
}

async function loadDocuments() {
  state.documents = await request("/api/documents");
  renderDocuments();
  if (state.documents.length) await selectDocument(state.documents[0]);
}

async function selectDocument(item) {
  state.selected = item;
  state.conversation = null;
  $("#document-title").textContent = item.topic;
  $("#document-filename").textContent = `${item.filename} · ${item.chunk_count} фрагментов`;
  $("#new-chat").disabled = false;
  renderDocuments();
  const conversations = await request(`/api/documents/${item.id}/conversations`);
  renderConversations(conversations);
  if (conversations.length) await loadConversation(conversations[0].id);
  else await createConversation();
}

async function createConversation() {
  if (!state.selected) return;
  const item = await request(`/api/documents/${state.selected.id}/conversations`, { method: "POST" });
  state.conversation = { ...item, messages: [] };
  const conversations = await request(`/api/documents/${state.selected.id}/conversations`);
  renderConversations(conversations);
  renderMessages([]);
  $("#question").disabled = false;
  $("#question-form button").disabled = false;
  $("#question").focus();
}

async function loadConversation(id) {
  state.conversation = await request(`/api/conversations/${id}`);
  const conversations = await request(`/api/documents/${state.selected.id}/conversations`);
  renderConversations(conversations);
  renderMessages(state.conversation.messages);
  $("#question").disabled = false;
  $("#question-form button").disabled = false;
}

function renderMessages(messages) {
  if (!messages.length) {
    $("#messages").innerHTML = `<div class="empty-chat"><span>✦</span><h3>Начните разговор</h3><p>Задайте вопрос по выбранному документу.<br>Ответ будет основан только на его содержимом.</p></div>`;
    return;
  }
  $("#messages").replaceChildren(...messages.map((message) => {
    const wrapper = document.createElement("div");
    wrapper.className = `message ${message.role}`;
    const meta = message.role === "user" ? "Вы" : "Atlas · ответ по документу";
    wrapper.innerHTML = `<div class="message-meta">${meta}</div><div>${escapeHtml(message.content)}</div>`;
    if (message.sources?.length) {
      const sources = document.createElement("div");
      sources.className = "sources";
      sources.innerHTML = message.sources.map((source) => `<div class="source">Страница ${source.page ?? "не указана"}: ${escapeHtml(source.quote || "")}</div>`).join("");
      wrapper.appendChild(sources);
    }
    return wrapper;
  }));
  $("#messages").lastElementChild?.scrollIntoView({ behavior: "smooth" });
}

function escapeHtml(value) { const element = document.createElement("span"); element.textContent = value ?? ""; return element.innerHTML; }

$("#auth-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  $("#auth-status").textContent = "Проверяем данные...";
  try {
    const endpoint = state.register ? "/api/auth/register" : "/api/auth/login";
    const payload = { email: $("#auth-email").value, password: $("#auth-password").value };
    if (state.register) payload.password_confirm = $("#auth-password-confirm").value;
    const auth = await request(endpoint, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify(payload) });
    setAuthenticated(auth);
  } catch (error) { $("#auth-status").textContent = error.message; }
});

$("#auth-switch").addEventListener("click", () => {
  state.register = !state.register;
  $("#auth-title").textContent = state.register ? "Создать аккаунт" : "Войти в Atlas";
  $("#auth-submit").textContent = state.register ? "Зарегистрироваться" : "Войти";
  $("#auth-switch").textContent = state.register ? "У меня уже есть аккаунт" : "Создать аккаунт";
  $("#auth-password").autocomplete = state.register ? "new-password" : "current-password";
  $("#confirm-password-label").classList.toggle("hidden", !state.register);
  $("#auth-password-confirm").required = state.register;
});
$("#logout").addEventListener("click", logout);
$("#new-chat").addEventListener("click", createConversation);

$("#file-input").addEventListener("change", async () => {
  if (!$("#file-input").files[0]) return;
  $("#upload-status").textContent = "Извлекаем текст и создаём тему...";
  const data = new FormData(); data.append("file", $("#file-input").files[0]);
  try { const item = await request("/api/documents", { method: "POST", body: data }); state.documents.unshift(item); await selectDocument(item); $("#upload-status").textContent = "Документ добавлен"; }
  catch (error) { showUploadError(error); }
  finally { $("#file-input").value = ""; }
});

$("#question-form").addEventListener("submit", async (event) => {
  event.preventDefault();
  const text = $("#question").value.trim();
  if (!text || !state.conversation) return;
  $("#question-status").textContent = "Atlas ищет ответ в документе...";
  $("#question").disabled = true; $("#question-form button").disabled = true;
  try { await request(`/api/conversations/${state.conversation.id}/questions`, { method: "POST", headers: { "Content-Type": "application/json" }, body: JSON.stringify({ question: text }) }); $("#question").value = ""; await loadConversation(state.conversation.id); $("#question-status").textContent = ""; }
  catch (error) { $("#question-status").textContent = error.message; $("#question").disabled = false; $("#question-form button").disabled = false; }
});

if (state.token) { $("#auth-view").classList.add("hidden"); $("#app-view").classList.remove("hidden"); loadDocuments().catch(logout); }
