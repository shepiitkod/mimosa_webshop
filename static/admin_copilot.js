(function () {
  "use strict";

  const API_ENDPOINT = "/admin/api/ai-enhance/";
  const PRODUCTS_CHANGE_URL = "/admin/shop/product/";

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

  function mountCopilot() {
    if (!isAdminPage()) return;
    if (document.getElementById("mimosa-copilot-tab")) return;

    const tab = document.createElement("button");
    tab.type = "button";
    tab.id = "mimosa-copilot-tab";
    tab.setAttribute("aria-expanded", "false");
    tab.setAttribute("aria-controls", "mimosa-copilot-panel");
    tab.textContent = "✨ AI Copilot";

    const panel = document.createElement("aside");
    panel.id = "mimosa-copilot-panel";
    panel.setAttribute("aria-hidden", "true");
    panel.innerHTML =
      '<header class="copilot-header">' +
        '<div><h2>Mimosa Atelier</h2><p>Розумний помічник · відповідає по суті</p></div>' +
        '<button type="button" id="mimosa-copilot-close" aria-label="Close">×</button>' +
      '</header>' +
      '<div id="mimosa-copilot-messages" role="log" aria-live="polite"></div>' +
      '<div class="copilot-input-area">' +
        '<textarea id="mimosa-copilot-input" rows="3" placeholder="Питання, ідея, опис товару, переклад…"></textarea>' +
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

    function attachApplyButton(wrap, fullText) {
      if (wrap.querySelector(".copilot-apply-btn")) return;

      const applyBtn = document.createElement("button");
      applyBtn.type = "button";
      applyBtn.className = "copilot-apply-btn";
      applyBtn.textContent = "Apply to Description";
      applyBtn.addEventListener("click", function () {
        const descriptionField = getDescriptionField();
        if (!descriptionField) {
          alert(
            "Поле опису недоступне на цій сторінці.\n\n" +
            "Відкрийте товар: Shop → Products → оберіть продукт → Change."
          );
          if (window.confirm("Перейти до списку товарів зараз?")) {
            window.location.href = PRODUCTS_CHANGE_URL;
          }
          return;
        }
        descriptionField.value = fullText;
        descriptionField.dispatchEvent(new Event("input", { bubbles: true }));
        descriptionField.dispatchEvent(new Event("change", { bubbles: true }));
        applyBtn.textContent = "✓ Applied";
        applyBtn.disabled = true;
      });
      wrap.appendChild(applyBtn);
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
      const decoder = new TextDecoder();
      let buffer = "";
      let fullText = "";

      while (true) {
        const chunk = await reader.read();
        if (chunk.done) break;

        buffer += decoder.decode(chunk.value, { stream: true });
        buffer = parseSseBuffer(buffer, function (payload) {
          if (payload.error) {
            throw new Error(payload.error);
          }
          if (payload.delta) {
            fullText += payload.delta;
            shell.textEl.textContent = fullText;
            scrollToBottom();
          }
        });
      }

      buffer += decoder.decode();
      parseSseBuffer(buffer + "\n", function (payload) {
        if (payload.error) throw new Error(payload.error);
        if (payload.delta) {
          fullText += payload.delta;
          shell.textEl.textContent = fullText;
        }
      });

      return fullText;
    }

    async function sendPromptJson(prompt) {
      const response = await fetch(API_ENDPOINT, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          "X-CSRFToken": getCsrfToken(),
        },
        body: JSON.stringify({ prompt: prompt, stream: false }),
        credentials: "same-origin",
      });

      const raw = await response.text();
      var data;
      try {
        data = raw ? JSON.parse(raw) : {};
      } catch (parseErr) {
        appendErrorMessage(
          "Сервер повернув HTML замість JSON (статус " + response.status + ")."
        );
        return;
      }

      if (!response.ok) {
        appendErrorMessage(data.error || "Request failed (" + response.status + ")");
        return;
      }

      const shell = createAiMessageShell();
      const text = data.enhanced_description || "";
      shell.textEl.textContent = text;
      shell.wrap.classList.remove("is-streaming");
      attachApplyButton(shell.wrap, text);
      scrollToBottom();
    }

    async function sendPrompt() {
      const prompt = inputEl.value.trim();
      if (!prompt) return;

      appendUserMessage(prompt);
      inputEl.value = "";
      setLoading(true);

      var shell = null;

      try {
        const response = await fetch(API_ENDPOINT, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({ prompt: prompt, stream: true }),
          credentials: "same-origin",
        });

        setLoading(false);

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

          attachApplyButton(shell.wrap, fullText);
          scrollToBottom();
          return;
        }

        await sendPromptJson(prompt);
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
