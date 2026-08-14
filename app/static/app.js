const state = { documents: [], selected: null };
const tabs = document.querySelector("#document-tabs");
const fileInput = document.querySelector("#file-input");
const uploadStatus = document.querySelector("#upload-status");
const questionForm = document.querySelector("#question-form");
const question = document.querySelector("#question");
const questionStatus = document.querySelector("#question-status");
const answerCard = document.querySelector("#answer-card");

async function request(url, options) {
  const response = await fetch(url, options);
  const body = await response.json();
  if (!response.ok) throw new Error(body.detail || "Ошибка запроса");
  return body;
}

function selectDocument(selectedDocument) {
  state.selected = selectedDocument;
  document.querySelector("#document-title").textContent = selectedDocument.topic;
  document.querySelector("#document-meta").textContent = `${selectedDocument.filename} · ${selectedDocument.chunk_count} фрагментов`;
  question.disabled = false;
  questionForm.querySelector("button").disabled = false;
  renderTabs();
}

function renderTabs() {
  tabs.replaceChildren(...state.documents.map((selectedDocument) => {
    const button = document.createElement("button");
    button.className = `tab ${state.selected?.id === selectedDocument.id ? "active" : ""}`;
    button.textContent = selectedDocument.topic;
    button.type = "button";
    button.addEventListener("click", () => selectDocument(selectedDocument));
    return button;
  }));
}

async function loadDocuments() {
  state.documents = await request("/api/documents");
  renderTabs();
  if (state.documents.length) selectDocument(state.documents[0]);
}

fileInput.addEventListener("change", async () => {
  if (!fileInput.files[0]) return;
  uploadStatus.textContent = "Индексация документа...";
  const data = new FormData();
  data.append("file", fileInput.files[0]);
  try {
    const document = await request("/api/documents", { method: "POST", body: data });
    state.documents.unshift(document);
    selectDocument(document);
    uploadStatus.textContent = "Документ добавлен";
  } catch (error) {
    uploadStatus.textContent = error.message;
  } finally {
    fileInput.value = "";
  }
});

questionForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (!state.selected || !question.value.trim()) return;
  questionStatus.textContent = "Ищу релевантные фрагменты...";
  answerCard.classList.add("hidden");
  try {
    const result = await request(`/api/documents/${state.selected.id}/questions`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question: question.value.trim() }),
    });
    document.querySelector("#answer").textContent = result.found ? result.answer : "В документе не найдено информации по этому вопросу.";
    document.querySelector("#sources").replaceChildren(...result.sources.map((source) => {
      const element = document.createElement("div");
      element.className = "source";
      element.textContent = `Страница ${source.page ?? "не указана"}: ${source.quote}`;
      return element;
    }));
    answerCard.classList.remove("hidden");
    questionStatus.textContent = "";
  } catch (error) {
    questionStatus.textContent = error.message;
  }
});

loadDocuments().catch((error) => { uploadStatus.textContent = error.message; });
