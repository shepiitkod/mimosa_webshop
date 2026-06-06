(function () {
  "use strict";

  const API_ENDPOINT = "/admin/api/ai-enhance/";
  const UTF8_DECODER = new TextDecoder("utf-8");
  const MAX_HISTORY = 20;
  const STORAGE_CHATS = "mimosa_chats_v3";
  const STORAGE_PROFILE = "mimosa_profile_v3";

  // ─── User profile (learning) ──────────────────────────────────────────────
  function loadProfile() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_PROFILE)) || {};
    } catch {
      return {};
    }
  }
  function saveProfile(p) {
    try {
      localStorage.setItem(STORAGE_PROFILE, JSON.stringify(p));
    } catch {}
  }
  function updateProfile(userText) {
    const p = loadProfile();
    // Detect language
    const ruChars = (userText.match(/[а-яёА-ЯЁ]/g) || []).length;
    const uaChars = (userText.match(/[іїєґІЇЄҐ]/g) || []).length;
    if (uaChars > 1) p.lang = "uk";
    else if (ruChars > 2) p.lang = "ru";
    else if (/[a-zA-Z]/.test(userText) && ruChars === 0) p.lang = "en";
    // Track word patterns (words 2-8 chars used repeatedly)
    const words = userText.toLowerCase().match(/[а-яёa-zіїєґ]{2,8}/g) || [];
    p.wordFreq = p.wordFreq || {};
    words.forEach((w) => {
      p.wordFreq[w] = (p.wordFreq[w] || 0) + 1;
    });
    // Track action type
    p.actionCounts = p.actionCounts || {};
    const txt = userText.toLowerCase();
    if (/заполни|fill|поля|форм/.test(txt))
      p.actionCounts.fill = (p.actionCounts.fill || 0) + 1;
    if (/опис|descri|контент|пост|post/.test(txt))
      p.actionCounts.content = (p.actionCounts.content || 0) + 1;
    if (/заказ|order|клиент/.test(txt))
      p.actionCounts.orders = (p.actionCounts.orders || 0) + 1;
    p.messageCount = (p.messageCount || 0) + 1;
    saveProfile(p);
    return p;
  }
  function buildProfileContext(p) {
    if (!p || !p.messageCount) return "";
    const topWords = Object.entries(p.wordFreq || {})
      .filter(([, c]) => c >= 3)
      .sort((a, b) => b[1] - a[1])
      .slice(0, 8)
      .map(([w]) => w);
    const topAction = Object.entries(p.actionCounts || {}).sort(
      (a, b) => b[1] - a[1],
    )[0];
    let ctx = "<user_profile>\n";
    if (p.lang) ctx += `Preferred language: ${p.lang}\n`;
    if (topWords.length)
      ctx += `Frequent words/style markers: ${topWords.join(", ")}\n`;
    if (topAction) ctx += `Most common task: ${topAction[0]}\n`;
    ctx += `Total messages: ${p.messageCount}\n`;
    ctx += "</user_profile>";
    return ctx;
  }

  // ─── Chat storage ─────────────────────────────────────────────────────────
  function loadChats() {
    try {
      return JSON.parse(localStorage.getItem(STORAGE_CHATS)) || [];
    } catch {
      return [];
    }
  }
  function saveChats(chats) {
    try {
      localStorage.setItem(STORAGE_CHATS, JSON.stringify(chats));
    } catch {}
  }
  function generateTitle(text) {
    const clean = text.replace(/\s+/g, " ").trim();
    return clean.length > 40 ? clean.slice(0, 38) + "…" : clean;
  }
  function createChat() {
    return {
      id: Date.now().toString(36) + Math.random().toString(36).slice(2),
      title: "Новый чат",
      messages: [],
      created: Date.now(),
    };
  }

  // ─── Nav command parser ───────────────────────────────────────────────────
  function parseNavCommands(text) {
    const found = [];
    const re = /\[\[NAV:([^\]|]+)\|([^\]]+)\]\]/g;
    let m;
    while ((m = re.exec(text)) !== null)
      found.push({ url: m[1].trim(), label: m[2].trim() });
    return found;
  }
  function stripNavCommands(text) {
    return text.replace(/\[\[NAV:[^\]]+\]\]/g, "").trim();
  }

  // ─── Admin page detection ─────────────────────────────────────────────────
  function isAdminPage() {
    return (window.location.pathname || "").indexOf("/admin") === 0;
  }
  function isProductFormPage() {
    const p = window.location.pathname || "";
    return (
      p.indexOf("/admin/shop/product/") === 0 &&
      (p.endsWith("/add/") || p.includes("/change"))
    );
  }
  function getPageContext() {
    const path = window.location.pathname;
    if (path.includes("/shop/product/add"))
      return "Страница: добавление нового товара";
    if (path.includes("/shop/product/") && path.includes("/change"))
      return "Страница: редактирование товара";
    if (path.includes("/shop/product")) return "Страница: список товаров";
    if (path.includes("/shop/order")) return "Страница: заказы";
    if (path.includes("/auth/user")) return "Страница: пользователи";
    if (path.includes("/shop/newsletteruser"))
      return "Страница: подписчики рассылки";
    if (path === "/admin/" || path === "/admin")
      return "Страница: главная панель";
    return "Страница: " + path;
  }
  function shouldFillForm(prompt) {
    if (!isProductFormPage()) return false;
    return /заполни|заповни|fill|поля|форм|создай товар|новый товар|новий товар|добав/.test(
      prompt.toLowerCase(),
    );
  }

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

  // ─── Main mount ───────────────────────────────────────────────────────────
  function mountCopilot() {
    if (!isAdminPage()) return;
    if (document.getElementById("mimosa-copilot-tab")) return;

    let chats = loadChats();
    let currentChatId = null;

    function currentChat() {
      return chats.find((c) => c.id === currentChatId) || null;
    }

    function switchToChat(id) {
      currentChatId = id;
      renderChatList();
      renderMessages();
    }

    function startNewChat() {
      const chat = createChat();
      chats.unshift(chat);
      saveChats(chats);
      switchToChat(chat.id);
    }

    if (!chats.length) {
      const c = createChat();
      chats.push(c);
      saveChats(chats);
    }
    currentChatId = chats[0].id;

    // ── Build DOM ─────────────────────────────────────────────────────────
    const tab = document.createElement("button");
    tab.type = "button";
    tab.id = "mimosa-copilot-tab";
    tab.setAttribute("aria-expanded", "false");
    tab.setAttribute("aria-controls", "mimosa-copilot-panel");
    tab.innerHTML =
      '<span class="copilot-tab-icon">✨</span><span class="copilot-tab-label">ИИ Ассистент</span>';

    const panel = document.createElement("aside");
    panel.id = "mimosa-copilot-panel";
    panel.setAttribute("aria-hidden", "true");
    panel.innerHTML = `
      <div class="copilot-sidebar">
        <div class="copilot-sidebar-header">
          <span class="copilot-sidebar-title">Чаты</span>
          <button type="button" id="copilot-new-chat" title="Новый чат">＋</button>
        </div>
        <div id="copilot-chat-list" class="copilot-chat-list"></div>
      </div>
      <div class="copilot-main">
        <header class="copilot-header">
          <div>
            <h2>Mimosa Copilot</h2>
            <p id="copilot-page-ctx" class="copilot-page-ctx"></p>
          </div>
          <button type="button" id="mimosa-copilot-close" aria-label="Close">×</button>
        </header>
        <div id="mimosa-copilot-messages" role="log" aria-live="polite"></div>
        <div class="copilot-input-area">
          <textarea id="mimosa-copilot-input" rows="3" placeholder="Спросите что угодно или: заполни поля — свечка из соевого воска…"></textarea>
          <div class="copilot-input-row">
            <span id="copilot-hint" class="copilot-hint"></span>
            <button type="button" id="mimosa-copilot-send">Отправить</button>
          </div>
        </div>
      </div>`;

    document.body.appendChild(tab);
    document.body.appendChild(panel);

    const closeBtn = document.getElementById("mimosa-copilot-close");
    const newChatBtn = document.getElementById("copilot-new-chat");
    const chatListEl = document.getElementById("copilot-chat-list");
    const messagesEl = document.getElementById("mimosa-copilot-messages");
    const inputEl = document.getElementById("mimosa-copilot-input");
    const sendBtn = document.getElementById("mimosa-copilot-send");
    const pageCtxEl = document.getElementById("copilot-page-ctx");
    const hintEl = document.getElementById("copilot-hint");

    // Set page context label
    pageCtxEl.textContent = getPageContext();

    // Smart hint based on profile
    function updateHint() {
      const p = loadProfile();
      const topAction = Object.entries(p.actionCounts || {}).sort(
        (a, b) => b[1] - a[1],
      )[0];
      if (isProductFormPage()) {
        hintEl.textContent = "💡 Скажи «заполни поля» + описание товара";
      } else if (topAction && topAction[0] === "orders") {
        hintEl.textContent = "💡 Часто смотришь заказы — перейти?";
      } else {
        hintEl.textContent = "";
      }
    }
    updateHint();

    // ── Chat list rendering ───────────────────────────────────────────────
    function renderChatList() {
      chatListEl.innerHTML = "";
      chats.forEach(function (chat) {
        const item = document.createElement("button");
        item.type = "button";
        item.className =
          "copilot-chat-item" + (chat.id === currentChatId ? " is-active" : "");
        item.dataset.id = chat.id;
        const titleSpan = document.createElement("span");
        titleSpan.className = "copilot-chat-item-title";
        titleSpan.textContent = chat.title;
        const delBtn = document.createElement("button");
        delBtn.type = "button";
        delBtn.className = "copilot-chat-del";
        delBtn.textContent = "×";
        delBtn.title = "Удалить чат";
        delBtn.addEventListener("click", function (e) {
          e.stopPropagation();
          chats = chats.filter((c) => c.id !== chat.id);
          if (!chats.length) {
            const c = createChat();
            chats.push(c);
          }
          saveChats(chats);
          if (currentChatId === chat.id) switchToChat(chats[0].id);
          else renderChatList();
        });
        item.appendChild(titleSpan);
        item.appendChild(delBtn);
        item.addEventListener("click", function () {
          switchToChat(chat.id);
        });
        chatListEl.appendChild(item);
      });
    }

    // ── Messages rendering ────────────────────────────────────────────────
    function renderMessages() {
      messagesEl.innerHTML = "";
      const chat = currentChat();
      if (!chat) return;
      chat.messages.forEach(function (msg) {
        if (msg.role === "user") {
          appendUserMessageEl(msg.content);
        } else if (msg.role === "assistant") {
          const clean = stripNavCommands(msg.content);
          const wrap = appendAiMessageEl(clean);
          const navs = parseNavCommands(msg.content);
          navs.forEach(function (nav) {
            appendNavButton(wrap, nav.url, nav.label);
          });
          if (msg.applyDescription && isProductFormPage()) {
            appendApplyBtn(wrap, msg.content);
          }
        }
      });
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function getCsrfToken() {
      const c = document.cookie
        .split(";")
        .map((s) => s.trim().split("="))
        .find((p) => p[0] === "csrftoken");
      if (c) return decodeURIComponent(c[1]);
      const inp = document.querySelector("[name=csrfmiddlewaretoken]");
      return inp ? inp.value : "";
    }

    function appendUserMessageEl(text) {
      const el = document.createElement("div");
      el.className = "copilot-msg copilot-msg--user";
      el.textContent = text;
      messagesEl.appendChild(el);
      return el;
    }

    function appendAiMessageEl(text) {
      const wrap = document.createElement("div");
      wrap.className = "copilot-msg copilot-msg--ai";
      const textEl = document.createElement("div");
      textEl.className = "copilot-ai-text";
      textEl.textContent = text;
      wrap.appendChild(textEl);
      messagesEl.appendChild(wrap);
      messagesEl.scrollTop = messagesEl.scrollHeight;
      return wrap;
    }

    function appendNavButton(wrap, url, label) {
      const btn = document.createElement("a");
      btn.href = url;
      btn.className = "copilot-nav-btn";
      btn.textContent = "→ " + label;
      wrap.appendChild(btn);
    }

    function appendApplyBtn(wrap, text) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "copilot-apply-btn";
      btn.textContent = "Вставить в описание";
      btn.addEventListener("click", function () {
        const field =
          document.getElementById("id_description") ||
          document.querySelector('textarea[name="description"]');
        if (!field) {
          alert("Откройте форму товара.");
          return;
        }
        field.value = text;
        field.dispatchEvent(new Event("input", { bubbles: true }));
        field.dispatchEvent(new Event("change", { bubbles: true }));
        btn.textContent = "✓ Вставлено";
        btn.disabled = true;
      });
      wrap.appendChild(btn);
    }

    function appendErrorMessage(text) {
      const el = document.createElement("div");
      el.className = "copilot-msg copilot-msg--error";
      el.textContent = text;
      messagesEl.appendChild(el);
      messagesEl.scrollTop = messagesEl.scrollHeight;
    }

    function setLoading(on) {
      sendBtn.disabled = on;
      inputEl.disabled = on;
      sendBtn.textContent = on ? "…" : "Отправить";
      const existing = document.getElementById("copilot-loading");
      if (on && !existing) {
        const el = document.createElement("div");
        el.className = "copilot-msg copilot-msg--loading";
        el.id = "copilot-loading";
        el.textContent = "Думаю…";
        messagesEl.appendChild(el);
        messagesEl.scrollTop = messagesEl.scrollHeight;
      } else if (!on && existing) {
        existing.remove();
      }
    }

    function applyProductFormFields(fields) {
      let applied = 0;
      PRODUCT_FIELD_KEYS.forEach(function (key) {
        if (!fields[key]) return;
        const el = document.getElementById("id_" + key);
        if (!el) return;
        el.value = fields[key];
        el.dispatchEvent(new Event("input", { bubbles: true }));
        el.dispatchEvent(new Event("change", { bubbles: true }));
        applied++;
      });
      return applied;
    }

    function parseSseBuffer(buffer, onEvent) {
      const lines = buffer.split("\n");
      const rest = lines.pop() || "";
      lines.forEach(function (line) {
        if (!line.startsWith("data: ")) return;
        try {
          onEvent(JSON.parse(line.slice(6)));
        } catch {}
      });
      return rest;
    }

    async function consumeStream(response, textEl, wrapEl) {
      const reader = response.body.getReader();
      let buffer = "";
      let fullText = "";
      wrapEl.classList.add("is-streaming");
      while (true) {
        const chunk = await reader.read();
        if (chunk.done) break;
        buffer += UTF8_DECODER.decode(chunk.value, { stream: true });
        buffer = parseSseBuffer(buffer, function (payload) {
          if (payload.error) throw new Error(payload.error);
          if (payload.delta) {
            fullText += payload.delta;
            textEl.textContent = stripNavCommands(fullText);
            messagesEl.scrollTop = messagesEl.scrollHeight;
          }
        });
      }
      buffer += UTF8_DECODER.decode();
      parseSseBuffer(buffer + "\n", function (payload) {
        if (payload.error) throw new Error(payload.error);
        if (payload.delta) {
          fullText += payload.delta;
          textEl.textContent = stripNavCommands(fullText);
        }
      });
      wrapEl.classList.remove("is-streaming");
      return fullText;
    }

    // ── Send ──────────────────────────────────────────────────────────────
    async function sendPrompt() {
      const prompt = inputEl.value.trim();
      if (!prompt) return;

      const chat = currentChat();
      if (!chat) return;

      // Update title from first message
      if (!chat.messages.length) {
        chat.title = generateTitle(prompt);
        saveChats(chats);
        renderChatList();
      }

      // Update user profile
      const profile = updateProfile(prompt);

      // Save user message
      chat.messages.push({ role: "user", content: prompt });
      saveChats(chats);
      appendUserMessageEl(prompt);
      inputEl.value = "";
      setLoading(true);

      const fillForm = shouldFillForm(prompt);
      const onProductForm = isProductFormPage();
      const pageCtx = getPageContext();
      const profileCtx = buildProfileContext(profile);

      // Build history with profile context injected as first system message
      const historyForApi = chat.messages
        .slice(-MAX_HISTORY)
        .slice(0, -1)
        .map((m) => ({ role: m.role, content: m.content }));
      if (profileCtx) {
        historyForApi.unshift({
          role: "user",
          content:
            profileCtx + "\n\n(это контекст профиля, не отвечай на него)",
        });
        historyForApi.unshift({
          role: "assistant",
          content: "Профиль учтён. Отвечаю в вашем стиле.",
        });
      }

      const promptWithCtx = `[${pageCtx}]\n${prompt}`;

      let shell = null;

      try {
        const response = await fetch(API_ENDPOINT, {
          method: "POST",
          headers: {
            "Content-Type": "application/json; charset=utf-8",
            "X-CSRFToken": getCsrfToken(),
          },
          body: JSON.stringify({
            prompt: promptWithCtx,
            history: historyForApi,
            stream: !fillForm,
            on_product_form: onProductForm,
            fill_product_form: fillForm,
          }),
          credentials: "same-origin",
        });

        setLoading(false);

        if (fillForm) {
          const raw = await response.text();
          let data;
          try {
            data = JSON.parse(raw);
          } catch {
            appendErrorMessage("Ошибка ответа сервера.");
            return;
          }
          if (!response.ok) {
            appendErrorMessage(data.error || "Ошибка " + response.status);
            return;
          }
          const applied = applyProductFormFields(data.form_fields || {});
          const msg =
            (data.message || "Поля заполнены.") +
            (applied ? " (" + applied + " полей)" : "");
          chat.messages.push({ role: "assistant", content: msg });
          saveChats(chats);
          const wrap = appendAiMessageEl(msg);
          if (!onProductForm)
            appendNavButton(wrap, "/admin/shop/product/add/", "Добавить товар");
          return;
        }

        const ctype = response.headers.get("content-type") || "";
        if (ctype.includes("text/event-stream")) {
          if (!response.ok) {
            appendErrorMessage("Stream failed " + response.status);
            return;
          }
          const wrap = document.createElement("div");
          wrap.className = "copilot-msg copilot-msg--ai";
          const textEl = document.createElement("div");
          textEl.className = "copilot-ai-text";
          wrap.appendChild(textEl);
          messagesEl.appendChild(wrap);
          shell = { wrap, textEl };

          const fullText = await consumeStream(response, textEl, wrap);
          if (!fullText.trim()) {
            wrap.remove();
            appendErrorMessage("Пустой ответ.");
            return;
          }

          // Parse nav commands and add buttons
          const navs = parseNavCommands(fullText);
          navs.forEach((nav) => appendNavButton(wrap, nav.url, nav.label));

          // Apply to description button on product form
          if (onProductForm) appendApplyBtn(wrap, stripNavCommands(fullText));

          chat.messages.push({ role: "assistant", content: fullText });
          saveChats(chats);
          messagesEl.scrollTop = messagesEl.scrollHeight;
          return;
        }

        const raw = await response.text();
        let data;
        try {
          data = JSON.parse(raw);
        } catch {
          appendErrorMessage("Ошибка ответа.");
          return;
        }
        if (!response.ok) {
          appendErrorMessage(data.error || "Ошибка " + response.status);
          return;
        }
        const reply = data.enhanced_description || "";
        chat.messages.push({ role: "assistant", content: reply });
        saveChats(chats);
        const wrap = appendAiMessageEl(stripNavCommands(reply));
        parseNavCommands(reply).forEach((nav) =>
          appendNavButton(wrap, nav.url, nav.label),
        );
        if (onProductForm) appendApplyBtn(wrap, reply);
      } catch (err) {
        setLoading(false);
        if (shell && shell.wrap.parentNode) shell.wrap.remove();
        appendErrorMessage("❌ " + (err.message || "Network error"));
      }
    }

    // ── Panel open/close ──────────────────────────────────────────────────
    function openPanel() {
      panel.classList.add("is-open");
      tab.classList.add("is-open");
      panel.setAttribute("aria-hidden", "false");
      tab.setAttribute("aria-expanded", "true");
      renderChatList();
      renderMessages();
      inputEl.focus();
    }
    function closePanel() {
      panel.classList.remove("is-open");
      tab.classList.remove("is-open");
      panel.setAttribute("aria-hidden", "true");
      tab.setAttribute("aria-expanded", "false");
    }

    tab.addEventListener("click", function () {
      panel.classList.contains("is-open") ? closePanel() : openPanel();
    });
    closeBtn.addEventListener("click", closePanel);
    newChatBtn.addEventListener("click", function () {
      startNewChat();
    });
    sendBtn.addEventListener("click", sendPrompt);
    inputEl.addEventListener("keydown", function (e) {
      if (e.key === "Enter" && !e.shiftKey) {
        e.preventDefault();
        sendPrompt();
      }
    });
  }

  if (document.readyState === "loading")
    document.addEventListener("DOMContentLoaded", mountCopilot);
  else mountCopilot();
})();
