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

  function mountCopilot() {
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
        '<div><h2>Mimosa Atelier</h2><p>Groq · Gemma · описи товарів</p></div>' +
        '<button type="button" id="mimosa-copilot-close" aria-label="Close">×</button>' +
      '</header>' +
      '<div id="mimosa-copilot-messages" role="log" aria-live="polite"></div>' +
      '<div class="copilot-input-area">' +
        '<textarea id="mimosa-copilot-input" rows="3" placeholder="Напр.: свічка-ракушка, соєвий віск, морські ноти…"></textarea>' +
        '<button type="button" id="mimosa-copilot-send">Send</button>' +
      '</div>';

    document.body.appendChild(tab);
    document.body.appendChild(panel);

    const closeBtn = document.getElementById("mimosa-copilot-close");
    const messagesEl = document.getElementById("mimosa-copilot-messages");
    const inputEl = document.getElementById("mimosa-copilot-input");
    const sendBtn = document.getElementById("mimosa-copilot-send");

    function getDescriptionField() {
      return document.getElementById("id_description");
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

    function appendMessage(role, text, aiTextForApply) {
      const wrap = document.createElement("div");
      wrap.className = "copilot-msg copilot-msg--" + role;

      if (role === "ai" && aiTextForApply) {
        const textNode = document.createElement("div");
        textNode.textContent = text;
        wrap.appendChild(textNode);

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
          descriptionField.value = aiTextForApply;
          descriptionField.dispatchEvent(new Event("input", { bubbles: true }));
          descriptionField.dispatchEvent(new Event("change", { bubbles: true }));
          applyBtn.textContent = "✓ Applied";
          applyBtn.disabled = true;
        });
        wrap.appendChild(applyBtn);
      } else {
        wrap.textContent = text;
      }

      messagesEl.appendChild(wrap);
      scrollToBottom();
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

    async function sendPrompt() {
      const prompt = inputEl.value.trim();
      if (!prompt) return;

      appendMessage("user", prompt);
      inputEl.value = "";
      setLoading(true);

      try {
        const response = await fetch(API_ENDPOINT, {
          method: "POST",
          headers: {
            "Content-Type": "application/json",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({ prompt: prompt }),
          credentials: "same-origin",
        });

        const data = await response.json();
        setLoading(false);

        if (!response.ok) {
          appendMessage("error", data.error || "Request failed (" + response.status + ")");
          return;
        }

        const enhanced = data.enhanced_description || "";
        appendMessage("ai", enhanced, enhanced);
      } catch (err) {
        setLoading(false);
        appendMessage("error", "❌ " + (err.message || "Network error"));
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
