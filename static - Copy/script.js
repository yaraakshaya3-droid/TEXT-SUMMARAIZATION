const inputField = document.getElementById("inputText");
const outputField = document.getElementById("outputText");
const loader = document.getElementById("loader");
const summarizeButton = document.getElementById("sumBtn");
const copyButton = document.getElementById("copyBtn");
const clearButton = document.getElementById("clearBtn");
const downloadButton = document.getElementById("downloadBtn");
const statusText = document.getElementById("statusText");
const fileInput = document.getElementById("fileInput");
const speechButton = document.getElementById("speechBtn");
const themeToggle = document.getElementById("themeToggle");
const inputWordCount = document.getElementById("inputWordCount");
const outputWordCount = document.getElementById("outputWordCount");
const inputCharacterCount = document.getElementById("inputCharacterCount");
const compressionRatio = document.getElementById("compressionRatio");
const summaryProvider = document.getElementById("summaryProvider");
const selectedLengthLabel = document.getElementById("selectedLengthLabel");
const historyList = document.getElementById("historyList");
const clearHistoryButton = document.getElementById("clearHistoryBtn");
const lengthButtons = Array.from(document.querySelectorAll("[data-length]"));

const HISTORY_KEY = "story-summary-history";
const THEME_KEY = "story-summary-theme";
const recognition = window.SpeechRecognition || window.webkitSpeechRecognition;

let currentLength = "short";
let currentSummary = "";

function countWords(text) {
    return (text.trim().match(/[A-Za-z0-9']+/g) || []).length;
}

function updateInputMetrics() {
    const text = inputField.value.trim();
    inputWordCount.textContent = countWords(text);
    inputCharacterCount.textContent = text.length;
}

function updateOutputMetrics(words = 0, ratio = 0, provider = "Waiting") {
    outputWordCount.textContent = words;
    compressionRatio.textContent = `${Math.round(ratio * 100)}%`;
    summaryProvider.textContent = provider;
}

function setSelectedLength(length) {
    currentLength = length;
    selectedLengthLabel.textContent = length.charAt(0).toUpperCase() + length.slice(1);

    lengthButtons.forEach((button) => {
        button.classList.toggle("active", button.dataset.length === length);
    });
}

function setOutputText(message, isPlaceholder = false) {
    outputField.textContent = message;
    outputField.classList.toggle("placeholder-text", isPlaceholder);
}

function readHistory() {
    try {
        return JSON.parse(localStorage.getItem(HISTORY_KEY) || "[]");
    } catch {
        return [];
    }
}

function writeHistory(items) {
    localStorage.setItem(HISTORY_KEY, JSON.stringify(items));
}

function saveHistoryItem(item) {
    const current = readHistory();
    const next = [item, ...current].slice(0, 6);
    writeHistory(next);
    renderHistory();
}

function restoreHistoryItem(index) {
    const historyItems = readHistory();
    const item = historyItems[index];
    if (!item) {
        return;
    }

    inputField.value = item.input;
    currentSummary = item.summary;
    setSelectedLength(item.length);
    setOutputText(item.summary);
    updateInputMetrics();
    updateOutputMetrics(item.outputWordCount, item.compressionRatio, item.provider);
    copyButton.disabled = false;
    downloadButton.disabled = false;
    statusText.textContent = "Loaded a previous summary from history.";
}

function renderHistory() {
    const items = readHistory();
    if (!items.length) {
        historyList.innerHTML = `
            <article class="history-empty">
                <p>Your recent summaries will appear here for quick reuse.</p>
            </article>
        `;
        return;
    }

    historyList.innerHTML = items
        .map((item, index) => {
            const createdAt = new Date(item.createdAt).toLocaleString();
            return `
                <article class="history-card">
                    <div class="history-card-top">
                        <span class="history-tag">${item.length}</span>
                        <span class="history-time">${createdAt}</span>
                    </div>
                    <h3>${item.inputPreview}</h3>
                    <p>${item.summaryPreview}</p>
                    <button class="ghost-button compact-button history-load-button" type="button" data-history-index="${index}">
                        Load Summary
                    </button>
                </article>
            `;
        })
        .join("");

    document.querySelectorAll("[data-history-index]").forEach((button) => {
        button.addEventListener("click", () => {
            restoreHistoryItem(Number(button.dataset.historyIndex));
        });
    });
}

function applyTheme(theme) {
    document.body.dataset.theme = theme;
    themeToggle.textContent = theme === "dark" ? "Light Mode" : "Dark Mode";
    themeToggle.setAttribute("aria-pressed", String(theme === "dark"));
}

function bootstrapTheme() {
    const savedTheme = localStorage.getItem(THEME_KEY) || "light";
    applyTheme(savedTheme);
}

function setLoadingState(isLoading) {
    summarizeButton.disabled = isLoading;
    summarizeButton.textContent = isLoading ? "Summarizing..." : "Summarize Text";
    loader.classList.toggle("hidden", !isLoading);
    outputField.classList.toggle("hidden", isLoading);
}

async function handleSummarize() {
    const text = inputField.value.trim();

    if (text.length < 120 || countWords(text) < 25) {
        statusText.textContent = "Please enter at least 120 characters and 25 words so the summary can capture the key ideas.";
        setOutputText("Your summary will appear here after you submit enough text.", true);
        copyButton.disabled = true;
        downloadButton.disabled = true;
        updateOutputMetrics(0, 0, "Waiting");
        return;
    }

    setLoadingState(true);
    statusText.textContent = "Processing your text and compressing it into a shorter, cleaner summary.";

    try {
        const response = await fetch("/summarize", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({ text, length: currentLength })
        });

        const data = await response.json();

        if (!response.ok) {
            throw new Error(data.error || "Unable to summarize the text right now.");
        }

        currentSummary = data.summary;
        setOutputText(data.summary);
        copyButton.disabled = false;
        downloadButton.disabled = false;
        updateOutputMetrics(data.output_word_count, data.compression_ratio, data.provider);
        statusText.textContent = "Summary ready. You can copy it, export it as a PDF, or reopen it later from history.";

        saveHistoryItem({
            createdAt: new Date().toISOString(),
            input: text,
            summary: data.summary,
            length: currentLength,
            provider: data.provider,
            compressionRatio: data.compression_ratio,
            outputWordCount: data.output_word_count,
            inputPreview: `${text.slice(0, 70).trim()}${text.length > 70 ? "..." : ""}`,
            summaryPreview: `${data.summary.slice(0, 120).trim()}${data.summary.length > 120 ? "..." : ""}`
        });
    } catch (error) {
        currentSummary = "";
        setOutputText(error.message);
        copyButton.disabled = true;
        downloadButton.disabled = true;
        updateOutputMetrics(0, 0, "Error");
        statusText.textContent = "Something went wrong while generating the summary.";
    } finally {
        setLoadingState(false);
    }
}

async function copyToClipboard() {
    if (!currentSummary) {
        return;
    }

    await navigator.clipboard.writeText(currentSummary);
    statusText.textContent = "Summary copied to your clipboard.";
}

function clearWorkspace() {
    inputField.value = "";
    currentSummary = "";
    updateInputMetrics();
    setOutputText("Your summary will appear here after you submit text.", true);
    updateOutputMetrics(0, 0, "Waiting");
    copyButton.disabled = true;
    downloadButton.disabled = true;
    statusText.textContent = "Workspace cleared. Add new text whenever you're ready.";
}

function handleFileUpload(event) {
    const [file] = event.target.files;
    if (!file) {
        return;
    }

    const reader = new FileReader();
    reader.onload = () => {
        inputField.value = String(reader.result || "");
        updateInputMetrics();
        statusText.textContent = `Loaded ${file.name}.`;
    };
    reader.readAsText(file);
}

function startSpeechInput() {
    if (!recognition) {
        statusText.textContent = "Speech recognition is not supported in this browser.";
        return;
    }

    const speechSession = new recognition();
    speechSession.lang = "en-US";
    speechSession.interimResults = false;
    speechSession.maxAlternatives = 1;

    speechSession.onstart = () => {
        statusText.textContent = "Listening... speak clearly and pause when you are done.";
    };

    speechSession.onresult = (event) => {
        const transcript = event.results[0][0].transcript || "";
        inputField.value = `${inputField.value.trim()} ${transcript}`.trim();
        updateInputMetrics();
        statusText.textContent = "Speech captured and added to the input.";
    };

    speechSession.onerror = () => {
        statusText.textContent = "Speech input could not be completed. Please try again.";
    };

    speechSession.start();
}

async function downloadSummaryPdf() {
    if (!currentSummary) {
        return;
    }

    const response = await fetch("/download-summary", {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify({ summary: currentSummary, length: currentLength })
    });

    if (!response.ok) {
        statusText.textContent = "The PDF could not be created right now.";
        return;
    }

    const blob = await response.blob();
    const url = URL.createObjectURL(blob);
    const anchor = document.createElement("a");
    anchor.href = url;
    anchor.download = "story-summary.pdf";
    anchor.click();
    URL.revokeObjectURL(url);
    statusText.textContent = "PDF downloaded successfully.";
}

lengthButtons.forEach((button) => {
    button.addEventListener("click", () => setSelectedLength(button.dataset.length));
});

themeToggle.addEventListener("click", () => {
    const nextTheme = document.body.dataset.theme === "dark" ? "light" : "dark";
    localStorage.setItem(THEME_KEY, nextTheme);
    applyTheme(nextTheme);
});

summarizeButton.addEventListener("click", handleSummarize);
copyButton.addEventListener("click", copyToClipboard);
clearButton.addEventListener("click", clearWorkspace);
downloadButton.addEventListener("click", downloadSummaryPdf);
fileInput.addEventListener("change", handleFileUpload);
speechButton.addEventListener("click", startSpeechInput);
clearHistoryButton.addEventListener("click", () => {
    writeHistory([]);
    renderHistory();
    statusText.textContent = "History cleared.";
});
inputField.addEventListener("input", updateInputMetrics);

bootstrapTheme();
renderHistory();
updateInputMetrics();
setSelectedLength(currentLength);
setOutputText("Your summary will appear here after you submit text.", true);
