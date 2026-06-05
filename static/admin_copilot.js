(function () {
  "use strict";

  const API_ENDPOINT = "/admin/api/ai-enhance/";
  const PRODUCTS_LIST_URL = "/admin/shop/product/";
  const UTF8_DECODER = new TextDecoder("utf-8");

  const MAX_HISTORY = 14;
  const chatHistory = [];

  const PRODUCT_FIELD_KEYS = [
    "title",
    "description",
    "category",
    "hs_code",
    "price",
    "stock",
    "scent",
    "wick",
    "weight",
    "weight_grams",
    "burn_time",
    "composition",
    "form_capacity",
    "wax_type",
  ];

  function getCsrfToken() {
    const fromCookie = document.cookie
      .split(";")
      .map(function (c) { return c.trim().split("="); })
      .find(function (pair) { return pair[0] === "csrftoken"; });
    if (fromCookie) return decodeURIComponent(fromCookie[1]);
    const input = document.querySelector("[name=csrfmiddlewaretoken]");
    return input ? input.value : "";
  }

  function isAdminPage() {
    return (window.location.pathname || "").indexOf("/admin") === 0;
  }

  function isProductFormPage() {
    const path = window.location.pathname || "";
    if (path.indexOf("/admin/shop/product/") !== 0) return false;
    return path.endsWith("/add/") || path.indexOf("/change") !== -1;
  }

  function shouldFillProductForm(prompt) {
    if (!isProductFormPage()) return false;
    const p = prompt.toLowerCase();
    return /заполни|заповни|заполн|fill|поля|форм|рядк|строк|створи товар|создай товар|новий товар|новый товар|добав товар/.test(p);
  }

  function mountCopilot() {
    if (!isAdminPage()) return;
    if (document.getElementById("mimosa-copilot-tab")) return;

    const tab = document.createElement("button");
    tab.type = "button";
    tab.id = "mimosa-copilot-tab";
    tab.setAttribute("aria-expanded", "false");
    tab.setAttribute("aria-controls", "mimosa-copilot-panel");
    tab.textContent = "✨ ИИ Ассистент";

    const panel = document.createElement("aside");
    panel.id = "mimosa-copilot-panel";
    panel.setAttribute("aria-hidden", "true");
    panel.innerHTML =
      '<header class="copilot-header">' +
        '<div><h2>Mimosa Atelier</h2><p>Памʼять діалогу · відповідає по вашому запиту</p></div>' +
        '<button type="button" id="mimosa-copilot-close" aria-label="Close">×</button>' +
      '</header>' +
      '<div id="mimosa-copilot-messages" role="log" aria-live="polite"></div>' +
      '<div class="copilot-input-area">' +
        '<textarea id="mimosa-copilot-input" rows="3" placeholder="Питання або: заповни поля — свічка ракушка, соєвий віск…"></textarea>' +
        '<button type="button" id="mimosa-copilot-send">Send</button>' +
      '</div>';

    document.body.appendChild(tab);
    document.body.appendChild(panel);

    const closeBtn = document.getElementById("mimosa-copilot-close");
    const messagesEl = document.getElementById("mimosa-copilot-messages");
    const inputEl = document.getElementById("mimosa-copilot-input");
    const sendBtn = document.getElementById("mimosa-copilot-send");

    function getDescriptionField() {
      return (
        document.getElementById("id_description") ||
        document.querySelector('textarea[name="description"]')
      );
    }

    function setFieldValue(el, value) {
      el.value = value;
      el.dispatchEvent(new Event("input", { bubbles: true }));
      el.dispatchEvent(new Event("change", { bubbles: true }));
    }

    function recordTurn(userText, assistantText) {
      if (userText) {
        chatHistory.push({ role: "user", content: userText });
      }
      if (assistantText) {
        chatHistory.push({ role: "assistant", content: assistantText });
      }
      while (chatHistory.length > MAX_HISTORY * 2) {
        chatHistory.shift();
      }
    }

    function historyForApi() {
      return chatHistory.slice(-MAX_HISTORY);
    }

    function applyProductFormFields(fields) {
      var applied = 0;
      PRODUCT_FIELD_KEYS.forEach(function (key) {
        if (!fields[key]) return;
        const el = document.getElementById("id_" + key);
        if (!el) return;
        setFieldValue(el, fields[key]);
        applied += 1;
      });
      return applied;
    }

    function openPanel() {
      panel.classList.add("is-open");
      tab.classList.add("is-open");
      panel.setAttribute("aria-hidden", "false");
      tab.setAttribute("aria-expanded", "true");
      inputEl.focus();
    }

    function closePanel() {
      panel.classList.remove("is-open");
      tab.classList.remove("is-open");
      panel.setAttribute("aria-hidden", "true");
      tab.setAttribute("aria-expanded", "false");
    }

    tab.addEventListener("click", function () {
      if (panel.classList.contains("is-open")) closePanel();
      else openPanel();
    });

    closeBtn.addEventListener("click", closePanel);

    function scrollToBottom() {
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function appendUserMessage(text) {
      const wrap = document.createElement("div");
      wrap.className = "copilot-msg copilot-msg--user";
      wrap.textContent = text;
      messagesEl.appendChild(wrap);
      scrollToBottom();
    }

    function appendAiMessage(text, options) {
      options = options || {};
      const wrap = document.createElement("div");
      wrap.className = "copilot-msg copilot-msg--ai";
      const textEl = document.createElement("div");
      textEl.className = "copilot-ai-text";
      textEl.textContent = text;
      wrap.appendChild(textEl);

      if (options.applyDescription) {
        const applyBtn = document.createElement("button");
        applyBtn.type = "button";
        applyBtn.className = "copilot-apply-btn";
        applyBtn.textContent = "Apply to Description";
        applyBtn.addEventListener("click", function () {
          const descriptionField = getDescriptionField();
          if (!descriptionField) {
            alert("Відкрийте форму товару (Products → Add/Change).");
            return;
          }
          setFieldValue(descriptionField, options.applyDescription);
          applyBtn.textContent = "✓ Applied";
          applyBtn.disabled = true;
        });
        wrap.appendChild(applyBtn);
      }

      messagesEl.appendChild(wrap);
      scrollToBottom();
      return wrap;
    }

    function appendErrorMessage(text) {
      const wrap = document.createElement("div");
      wrap.className = "copilot-msg copilot-msg--error";
      wrap.textContent = text;
      messagesEl.appendChild(wrap);
      scrollToBottom();
    }

    function createAiMessageShell() {
      const wrap = document.createElement("div");
      wrap.className = "copilot-msg copilot-msg--ai is-streaming";
      const textEl = document.createElement("div");
      textEl.className = "copilot-ai-text";
      wrap.appendChild(textEl);
      messagesEl.appendChild(wrap);
      scrollToBottom();
      return { wrap: wrap, textEl: textEl };
    }

    function setLoading(on) {
      sendBtn.disabled = on;
      inputEl.disabled = on;
      if (on) {
        sendBtn.textContent = "Génération...";
        const el = document.createElement("div");
        el.className = "copilot-msg copilot-msg--loading";
        el.id = "copilot-loading";
        el.textContent = "Génération...";
        messagesEl.appendChild(el);
        scrollToBottom();
      } else {
        sendBtn.textContent = "Send";
        const loading = document.getElementById("copilot-loading");
        if (loading) loading.remove();
      }
    }

    function parseSseBuffer(buffer, onEvent) {
      const lines = buffer.split("\n");
      const rest = lines.pop() || "";
      lines.forEach(function (line) {
        if (!line.startsWith("data: ")) return;
        try {
          onEvent(JSON.parse(line.slice(6)));
        } catch (e) {
          /* ignore malformed chunks */
        }
      });
      return rest;
    }

    async function consumeStream(response, shell) {
      const reader = response.body.getReader();
      let buffer = "";
      let fullText = "";

      while (true) {
        const chunk = await reader.read();
        if (chunk.done) break;

        buffer += UTF8_DECODER.decode(chunk.value, { stream: true });
        buffer = parseSseBuffer(buffer, function (payload) {
          if (payload.error) throw new Error(payload.error);
          if (payload.delta) {
            fullText += payload.delta;
            shell.textEl.textContent = fullText;
            scrollToBottom();
          }
        });
      }

      buffer += UTF8_DECODER.decode();
      parseSseBuffer(buffer + "\n", function (payload) {
        if (payload.error) throw new Error(payload.error);
        if (payload.delta) {
          fullText += payload.delta;
          shell.textEl.textContent = fullText;
        }
      });

      return fullText;
    }

    async function parseJsonResponse(response) {
      const raw = await response.text();
      try {
        return raw ? JSON.parse(raw) : {};
      } catch (e) {
        throw new Error(
          "Сервер повернув не JSON (статус " + response.status + ")."
        );
      }
    }

    async function sendPrompt() {
      const prompt = inputEl.value.trim();
      if (!prompt) return;

      const fillForm = shouldFillProductForm(prompt);
      const onProductForm = isProductFormPage();

      appendUserMessage(prompt);
      inputEl.value = "";
      setLoading(true);

      var shell = null;

      try {
        const response = await fetch(API_ENDPOINT, {
          method: "POST",
          headers: {
            "Content-Type": "application/json; charset=utf-8",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({
            prompt: prompt,
            history: historyForApi(),
            stream: !fillForm,
            on_product_form: onProductForm,
            fill_product_form: fillForm,
          }),
          credentials: "same-origin",
        });

        setLoading(false);

        if (fillForm) {
          const data = await parseJsonResponse(response);
          if (!response.ok) {
            appendErrorMessage(data.error || "Request failed (" + response.status + ")");
            return;
          }

          const applied = applyProductFormFields(data.form_fields || {});
          const msg =
            (data.message || "Поля заповнено.") +
            (applied ? " (" + applied + " полів у формі)" : "");

          appendAiMessage(msg);
          recordTurn(prompt, msg);

          if (!onProductForm) {
            appendErrorMessage(
              "Відкрийте Shop → Products → Add product, щоб застосувати поля у формі."
            );
          }
          return;
        }

        const contentType = response.headers.get("content-type") || "";

        if (contentType.indexOf("text/event-stream") !== -1) {
          if (!response.ok) {
            appendErrorMessage("Stream failed (" + response.status + ")");
            return;
          }

          shell = createAiMessageShell();
          const fullText = await consumeStream(response, shell);
          shell.wrap.classList.remove("is-streaming");

          if (!fullText.trim()) {
            shell.wrap.remove();
            appendErrorMessage("Порожня відповідь від моделі.");
            return;
          }

          if (onProductForm) {
            const applyBtn = document.createElement("button");
            applyBtn.type = "button";
            applyBtn.className = "copilot-apply-btn";
            applyBtn.textContent = "Apply to Description";
            applyBtn.addEventListener("click", function () {
              const descriptionField = getDescriptionField();
              if (!descriptionField) return;
              setFieldValue(descriptionField, fullText);
              applyBtn.textContent = "✓ Applied";
              applyBtn.disabled = true;
            });
            shell.wrap.appendChild(applyBtn);
          }

          recordTurn(prompt, fullText);
          scrollToBottom();
          return;
        }

        const data = await parseJsonResponse(response);
        if (!response.ok) {
          appendErrorMessage(data.error || "Request failed (" + response.status + ")");
          return;
        }

        const reply = data.enhanced_description || "";
        appendAiMessage(reply, {
          applyDescription: onProductForm ? reply : null,
        });
        recordTurn(prompt, reply);
      } catch (err) {
        setLoading(false);
        if (shell && shell.wrap && shell.wrap.parentNode) {
          shell.wrap.remove();
        }
        appendErrorMessage("❌ " + (err.message || "Network error"));
      }
    }

    sendBtn.addEventListener("click", sendPrompt);
    inputEl.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendPrompt();
      }
    });
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", mountCopilot);
  } else {
    mountCopilot();
  }
})();
