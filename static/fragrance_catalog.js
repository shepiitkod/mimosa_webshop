(function () {
  "use strict";

  /* ─────────────────────────────────────────────────────────────────────────
   * FRAGRANCE DATA — 18 signatures Mimosa Atelier
   * ───────────────────────────────────────────────────────────────────────── */

  const FRAGRANCES = [
    {
      id: "ambre",
      name: "Ambre",
      img: "ambre",
      family: "Oriental · Balsamique",
      intensity: 4,
      notes: [
        "Ambre solaire",
        "Résine précieuse",
        "Vanille bourbon",
        "Musc ambré",
      ],
      seasons: ["Automne", "Hiver"],
      moments: ["Soirée intimiste", "Méditation", "Lecture au coin du feu"],
      pairsWith: ["Musc", "Bois de santal", "Cachemire et soie"],
      description: `Distillé des résines millénaires de l'Orient, notre Ambre enveloppe l'espace d'une chaleur profonde et somptueuse. Des notes vanillées et balsamiques se fondent dans un musc doré, créant une présence enveloppante et indéfectible qui s'attarde longtemps après que la flamme s'est éteinte.`,
      mood: `Pour les soirs où le temps s'arrête, quand la lumière ambrée des bougies efface doucement le monde extérieur.`,
    },
    {
      id: "bergamote",
      name: "Bergamote",
      img: "bergamote",
      family: "Hespéridé · Frais",
      intensity: 2,
      notes: [
        "Bergamote de Calabre",
        "Thé vert",
        "Cèdre léger",
        "Zeste de citron",
      ],
      seasons: ["Printemps", "Été"],
      moments: ["Matin revigorant", "Pause créative", "Brunch dominical"],
      pairsWith: ["Citron vert", "Fleur d'oranger", "Eucalyptus"],
      description: `La bergamote de Calabre, cueillie à l'aube dans les vergers baignés de soleil du sud de l'Italie, distille une lumière citronnée d'une rare pureté. Son éclat hespéridé, finement relevé de thé vert et d'un cèdre aérien, éveille les sens avec une légèreté qui tient presque du miracle.`,
      mood: `L'éveil d'un matin méditerranéen, quand le soleil effleure à peine les toits dorés et que tout semble encore possible.`,
    },
    {
      id: "bois-de-oud",
      name: "Bois de oud",
      img: "bois-de-oud",
      family: "Boisé · Oriental",
      intensity: 5,
      notes: [
        "Oud précieux",
        "Encens sacré",
        "Rose de Damas",
        "Ambre noir",
        "Résine de myrrhe",
      ],
      seasons: ["Automne", "Hiver"],
      moments: ["Cérémonie", "Soirée de gala", "Rituel méditatif"],
      pairsWith: ["Ambre", "Rose ancienne", "Musc"],
      description: `Le bois d'oud, trésor millénaire de l'Arabie et des forêts d'Asie du Sud-Est, se déploie ici dans toute sa majesté ténébreuse et complexe. Mêlé à l'encens sacré et à la rose de Damas, il compose une symphonie olfactive d'une intensité inégalée, aux résonances presque sacrées qui transcendent le simple acte de parfumer un espace.`,
      mood: `Là où l'ombre devient velours et où chaque souffle est une prière murmurée à la nuit.`,
    },
    {
      id: "bois-de-rose",
      name: "Bois de rose",
      img: "bois-de-rose",
      family: "Floral · Boisé",
      intensity: 3,
      notes: ["Bois de rose", "Pétale de rose", "Cèdre doux", "Iris poudré"],
      seasons: ["Printemps", "Automne"],
      moments: ["Après-midi doux", "Lecture", "Bain parfumé"],
      pairsWith: ["Rose ancienne", "Jasmin", "Musc"],
      description: `Issu des essences précieuses des forêts brésiliennes avec la délicatesse d'un artisan parfumeur, le bois de rose exhale une douceur florale et boisée à la fois tendre et profondément raffinée. L'iris poudré apporte une profondeur romantique à cette composition d'une grâce naturelle.`,
      mood: `La douceur d'une fin d'après-midi rosée, quand le jardin respire encore la chaleur du soleil déclinant.`,
    },
    {
      id: "bois-de-santal",
      name: "Bois de santal",
      img: "bois-de-santal",
      family: "Boisé · Crémeux",
      intensity: 3,
      notes: [
        "Santal de Mysore",
        "Vanille crémeuse",
        "Cèdre Atlas",
        "Musc soyeux",
      ],
      seasons: ["Automne", "Hiver", "Printemps"],
      moments: ["Méditation", "Yoga", "Soirée zen"],
      pairsWith: ["Ambre", "Musc", "Cachemire et soie"],
      description: `Le santal de Mysore, aux notes lactées et crémeuses d'une onctuosité divine, incarne la quintessence du calme et de la sérénité intérieure. Sa texture olfactive enveloppante, dorée de vanille et soulignée d'un cèdre Atlas d'une austère beauté, invite à un voyage immobile vers les profondeurs de soi.`,
      mood: `Quand le silence devient confort et que chaque respiration lente devient, enfin, un acte de paix.`,
    },
    {
      id: "cachemire-et-soie",
      name: "Cachemire et soie",
      img: "cachemire-et-soie",
      family: "Poudrée · Musc",
      intensity: 3,
      notes: [
        "Musc cachemire",
        "Iris poudré",
        "Santal blanc",
        "Ambre doux",
        "Ylang-ylang",
      ],
      seasons: ["Automne", "Hiver"],
      moments: ["Soirée intime", "Cocooning", "Lecture au coin du feu"],
      pairsWith: ["Ambre", "Musc", "Bois de santal"],
      description: `Imaginée comme la caresse d'un tissu de haute couture sur la peau nue, cette fragrance conjugue le moelleux du cachemire et la fluidité de la soie dans un accord poudré d'une sophistication absolue. L'iris et le santal blanc y déposent leur signature de haute parfumerie, pendant que l'ylang-ylang insuffle une chaleur délicatement sensuelle.`,
      mood: `Le luxe discret des soirs d'hiver, enveloppée dans la douceur soyeuse de ce que l'on chérit le plus.`,
    },
    {
      id: "citron-vert",
      name: "Citron vert",
      img: "citron-vert",
      family: "Hespéridé · Vert",
      intensity: 2,
      notes: [
        "Citron vert pressé",
        "Menthe verte",
        "Basilic frais",
        "Vétiver léger",
      ],
      seasons: ["Été", "Printemps"],
      moments: ["Matin pétillant", "Brunch estival", "Séance sportive"],
      pairsWith: ["Bergamote", "Eucalyptus", "Fleur d'oranger"],
      description: `Le jus vif et acidulé du citron vert tropical éclate dans l'espace comme un rayon de lumière pure, ponctué de la vivacité de la menthe fraîche et de l'élégance herbacée du basilic. Une invitation directe à la légèreté et à la vitalité des matinées estivales.`,
      mood: `La pétillance d'un matin d'été qui promet une journée de lumière sans nuages ni compromis.`,
    },
    {
      id: "coquelicot",
      name: "Coquelicot",
      img: "coquelicot",
      family: "Floral · Poudré",
      intensity: 2,
      notes: ["Pétale de coquelicot", "Iris", "Rose légère", "Musc poudré"],
      seasons: ["Printemps", "Été"],
      moments: ["Promenade champêtre", "Dimanche matin", "Pique-nique"],
      pairsWith: ["Mimosa", "Fleur d'acacia", "Rose ancienne"],
      description: `Né dans les champs de Provence où le vent fait danser les corolles cramoisies à perte de vue, notre Coquelicot capture la légèreté poudreuse d'une fleur sauvage d'une sincérité touchante. Un floral délicat et nostalgique, tendre comme un souvenir d'enfance retrouvé au détour d'une promenade.`,
      mood: `Le vertige doux d'un champ fleuri traversé au petit matin, quand la rosée pèse encore sur chaque pétale fragile.`,
    },
    {
      id: "eucalyptus",
      name: "Eucalyptus",
      img: "eucalyptus",
      family: "Aromatique · Frais",
      intensity: 3,
      notes: [
        "Eucalyptus globulus",
        "Menthe poivrée",
        "Cèdre frais",
        "Cyprès vert",
      ],
      seasons: ["Printemps", "Hiver"],
      moments: ["Méditation matinale", "Exercice", "Clarté mentale"],
      pairsWith: ["Lavande", "Bergamote", "Citron vert"],
      description: `L'eucalyptus, distillé dans sa pureté la plus absolue, ouvre les sens d'un souffle camphré et cristallin qui purifie l'air de toute lourdeur. La menthe poivrée et le cyprès vert lui confèrent une dimension aromatique et forestière qui éveille l'esprit, clarifie les pensées, et rend l'impossible soudainement accessible.`,
      mood: `La sensation de respirer profondément au cœur d'une forêt au petit matin, l'esprit libre et le corps vif.`,
    },
    {
      id: "figue-et-santal",
      name: "Figue et Santal",
      img: "figue-et-santal",
      family: "Boisé · Fruité",
      intensity: 3,
      notes: ["Figue mûre", "Santal crémeux", "Lait de figuier", "Musc boisé"],
      seasons: ["Été", "Automne"],
      moments: [
        "Fin d'après-midi",
        "Apéritif méditerranéen",
        "Dîner en terrasse",
      ],
      pairsWith: ["Bois de santal", "Mimosa", "Fleur d'oranger"],
      description: `La figue gorgée de soleil méditerranéen se fond dans la chaleur crémeuse du santal dans une union olfactive d'une gourmandise exquise et d'une sensualité nonchalante. Le lait de figuier apporte une note lactée et légèrement verte qui évoque les jardins ombragés de la Provence en plein août.`,
      mood: `Un après-midi suspendu sous les figuiers anciens, où le temps s'écoule à la cadence des cigales et du vent tiède.`,
    },
    {
      id: "fleur-dacacia",
      name: "Fleur d'acacia",
      img: "fleur-dacacia",
      family: "Floral · Miellé",
      intensity: 2,
      notes: [
        "Fleur d'acacia",
        "Miel de Provence",
        "Jasmin blanc",
        "Musc floral",
      ],
      seasons: ["Printemps", "Été"],
      moments: ["Matin ensoleillé", "Jardin fleuri", "Goûter délicat"],
      pairsWith: ["Mimosa", "Coquelicot", "Fleur d'oranger"],
      description: `La fleur d'acacia, délicate et mellifère comme une bénédiction printanière, distille ses notes dorées et miellées avec une générosité ensoleillée. Le jasmin blanc lui prête sa sensualité discrète et envoûtante, créant un bouquet champêtre d'une douceur à la fois innocente et inoubliable.`,
      mood: `Le printemps dans sa plus tendre expression, quand les abeilles bourdonnent et que la lumière du matin est encore toute dorée.`,
    },
    {
      id: "fleur-doranger",
      name: "Fleur d'oranger",
      img: "fleur-doranger",
      family: "Floral · Néroli",
      intensity: 3,
      notes: [
        "Néroli absolu",
        "Fleur d'oranger",
        "Bergamote dorée",
        "Musc blanc",
        "Cèdre",
      ],
      seasons: ["Printemps", "Été"],
      moments: ["Cérémonie", "Spa", "Moment de sérénité"],
      pairsWith: ["Jasmin", "Mimosa", "Bergamote"],
      description: `Le néroli absolu, extrait à la main des fragiles fleurs d'oranger amer de Tunisie, porte en lui la quintessence lumineuse de la Méditerranée — solaire, d'une pureté presque ineffable, et d'une délicatesse infinie. Cette fragrance évoque les jardins d'Andalousie en fleur, entre blancheur éclatante et ivresse sucrée.`,
      mood: `La pureté d'un matin de cérémonie, quand les fleurs d'oranger parfument encore le vent marin et que tout commence.`,
    },
    {
      id: "jasmin",
      name: "Jasmin",
      img: "jasmin",
      family: "Floral · Sensuel",
      intensity: 4,
      notes: [
        "Jasmin de Grasse",
        "Rose absolue",
        "Ylang-ylang",
        "Musc sensuel",
        "Santal doux",
      ],
      seasons: ["Été", "Automne"],
      moments: ["Soirée romantique", "Bain précieux", "Coucher de soleil"],
      pairsWith: ["Rose ancienne", "Fleur d'oranger", "Musc"],
      description: `Le jasmin de Grasse, roi incontesté de la haute parfumerie française depuis des siècles, déploie ici ses facettes les plus sensuelles et envoûtantes, magnifiées par la rose absolue et l'ylang-ylang tropical. Un floral d'une intensité charnelle et profondément raffinée, destiné aux nuits qui méritent d'être mémorables.`,
      mood: `Les nuits tièdes où la peau garde encore la chaleur du soleil couché, et où chaque heure qui passe est un cadeau.`,
    },
    {
      id: "lavande",
      name: "Lavande",
      img: "lavande",
      family: "Aromatique · Lavande",
      intensity: 3,
      notes: [
        "Lavande fine de Haute-Provence",
        "Romarin sauvage",
        "Cèdre",
        "Musc frais",
      ],
      seasons: ["Été", "Printemps"],
      moments: ["Coucher", "Relaxation", "Bain du soir"],
      pairsWith: ["Eucalyptus", "Bergamote", "Musc"],
      description: `La lavande fine de Haute-Provence, cueillie sur les plateaux de Valensole au cœur de l'été provençal, déploie ses effluves aromatiques avec une authenticité et une sérénité sans égales. Le romarin sauvage et le cèdre viennent ancrer cette composition dans une profondeur sèche et méditerranéenne d'une beauté toute simple.`,
      mood: `Le soir tombant sur les champs mauves du Vaucluse, quand la chaleur de la journée cède enfin la place au silence et à la douceur.`,
    },
    {
      id: "mimosa",
      name: "Mimosa",
      img: "mimosa",
      family: "Floral · Solaire",
      intensity: 3,
      notes: [
        "Mimosa de Cannes",
        "Fleur d'acacia",
        "Vanille dorée",
        "Cèdre léger",
      ],
      seasons: ["Printemps", "Été"],
      moments: ["Réveil lumineux", "Brunch dominical", "Escapade en Riviera"],
      pairsWith: ["Fleur d'acacia", "Fleur d'oranger", "Bergamote"],
      description: `Hommage vibrant à la Côte d'Azur en février, quand les mimosas explosent de lumière jaune sur fond d'azur, cette fragrance capte l'essence même de la joie méditerranéenne. Dorée, légèrement miellée et poudrée comme un rayon de soleil hivernal, elle est l'évocation d'un bonheur simple, lumineux et sans calcul.`,
      mood: `L'allégresse d'un matin de février sur la promenade de Cannes, les bras chargés de mimosa et le cœur entièrement léger.`,
    },
    {
      id: "musc",
      name: "Musc",
      img: "musc",
      family: "Musqué · Propre",
      intensity: 2,
      notes: ["Musc blanc", "Iris poudré", "Cèdre doux", "Ambre gris"],
      seasons: ["Toutes saisons"],
      moments: ["Quotidien raffiné", "Télétravail", "Quiétude"],
      pairsWith: ["Ambre", "Cachemire et soie", "Bois de santal"],
      description: `Le musc blanc, intemporel et universel comme la peau propre après le bain, est ici distillé dans sa plus grande pureté, rehaussé d'iris poudrée et d'ambre gris pour une signature olfactive d'une discrétion absolument sensuelle. Une fragrance de fond que l'on ne remarque pas tout de suite, mais dont l'absence se ferait immédiatement ressentir.`,
      mood: `La présence invisible qui embellit l'ordinaire — le parfum de ce qui est simplement et profondément beau.`,
    },
    {
      id: "rose-ancienne",
      name: "Rose ancienne",
      img: "rose-ancienne",
      family: "Floral · Rose",
      intensity: 4,
      notes: [
        "Rose de Mai",
        "Rose de Damas",
        "Patchouli terre",
        "Musc ambré",
        "Oud léger",
      ],
      seasons: ["Printemps", "Automne"],
      moments: ["Soirée élégante", "Cérémonie", "Après-midi à la française"],
      pairsWith: ["Jasmin", "Bois de oud", "Ambre"],
      description: `Évocatrice des roseraies des châteaux de la Loire au tournant du siècle, notre Rose ancienne convoque les deux roses les plus précieuses de la haute parfumerie dans un accord d'une profondeur et d'une richesse remarquables. Le patchouli et l'oud y ajoutent une ombre séduisante qui confère à cette rose toute la noblesse qu'elle mérite.`,
      mood: `La grâce anachronique d'un jardin à la française, où chaque rose ouverte est un sonnet de pétales que personne n'a encore pensé à écrire.`,
    },
    {
      id: "rosa",
      name: "Rosa",
      img: "rosa",
      family: "Floral · Frais",
      intensity: 3,
      notes: [
        "Rose thé fraîche",
        "Pétale de rose d'Ispahan",
        "Cèdre blanc",
        "Musc vert",
      ],
      seasons: ["Printemps", "Été"],
      moments: ["Matin délicat", "Jardin anglais", "Pause gourmande"],
      pairsWith: ["Rose ancienne", "Coquelicot", "Fleur d'oranger"],
      description: `Lumineuse et légèrement aquatique, Rosa saisit la rose dans sa jeunesse la plus fraîche et sa beauté la plus cristalline, avant que le soleil n'ait encore eu le temps de sécher la rosée sur ses pétales. La rose thé, d'une finesse rare, s'unit au musc vert et au cèdre blanc dans une transparence printanière qui émeut par sa simplicité parfaite.`,
      mood: `La grâce des premières roses d'été au petit matin, quand le jardin est encore silencieux et que tout semble d'une fraîcheur miraculeuse.`,
    },
  ];

  /* ─────────────────────────────────────────────────────────────────────────
   * STATE
   * ───────────────────────────────────────────────────────────────────────── */

  let staticUrl = "";

  /* ─────────────────────────────────────────────────────────────────────────
   * HELPERS
   * ───────────────────────────────────────────────────────────────────────── */

  function getFragrance(id) {
    return (
      FRAGRANCES.find(function (f) {
        return f.id === id;
      }) || null
    );
  }

  function buildTags(items) {
    return items
      .map(function (item) {
        return '<span class="spc-tag">' + item + "</span>";
      })
      .join("");
  }

  /* ─────────────────────────────────────────────────────────────────────────
   * TAB SYNC
   * ───────────────────────────────────────────────────────────────────────── */

  function syncActiveTab(id) {
    document.querySelectorAll(".spc-tab[data-id]").forEach(function (tab) {
      tab.classList.toggle("is-active", tab.dataset.id === id);
    });
    /* Also scroll the tab strip so the active tab is centred */
    var activeTab = document.querySelector('.spc-tab[data-id="' + id + '"]');
    if (activeTab) {
      var strip = activeTab.closest(".spc-names");
      if (strip) {
        var tabRect = activeTab.getBoundingClientRect();
        var stripRect = strip.getBoundingClientRect();
        var delta =
          tabRect.left -
          stripRect.left -
          stripRect.width / 2 +
          tabRect.width / 2;
        strip.scrollBy({ left: delta, behavior: "smooth" });
      }
    }
  }

  /* ─────────────────────────────────────────────────────────────────────────
   * MODAL
   * ───────────────────────────────────────────────────────────────────────── */

  function openModal(id) {
    var fragrance = getFragrance(id);
    if (!fragrance) return;

    var modal = document.getElementById("spc-modal");
    if (!modal) return;

    var imgEl = document.getElementById("spc-modal-img");
    if (imgEl) {
      imgEl.src = staticUrl + "assets/images/sca-" + fragrance.img + ".ico";
      imgEl.alt = fragrance.name;
    }

    var familyEl = document.getElementById("spc-modal-family");
    if (familyEl) familyEl.textContent = fragrance.family;

    var nameEl = document.getElementById("spc-modal-name");
    if (nameEl) nameEl.textContent = fragrance.name;

    var descEl = document.getElementById("spc-modal-description");
    if (descEl) descEl.textContent = fragrance.description;

    var moodEl = document.getElementById("spc-modal-mood");
    if (moodEl) moodEl.textContent = fragrance.mood;

    var notesEl = document.getElementById("spc-modal-notes");
    if (notesEl) {
      notesEl.innerHTML = fragrance.notes
        .map(function (note) {
          return "<li>" + note + "</li>";
        })
        .join("");
    }

    var seasonsEl = document.getElementById("spc-modal-seasons");
    if (seasonsEl) seasonsEl.innerHTML = buildTags(fragrance.seasons);

    var momentsEl = document.getElementById("spc-modal-moments");
    if (momentsEl) momentsEl.innerHTML = buildTags(fragrance.moments);

    var pairsEl = document.getElementById("spc-modal-pairs");
    if (pairsEl) pairsEl.innerHTML = buildTags(fragrance.pairsWith);

    var dotsWrapper = document.getElementById("spc-intensity-dots");
    if (dotsWrapper) {
      var dots = dotsWrapper.querySelectorAll("span");
      dots.forEach(function (dot, i) {
        dot.classList.toggle("is-active", i < fragrance.intensity);
      });
    }

    modal.classList.add("is-open");
    modal.removeAttribute("aria-hidden");
    document.body.style.overflow = "hidden";

    /* Focus the close button for accessibility */
    var closeBtn = document.getElementById("spc-modal-close");
    if (closeBtn) {
      setTimeout(function () {
        closeBtn.focus();
      }, 60);
    }
  }

  function closeModal() {
    var modal = document.getElementById("spc-modal");
    if (!modal) return;
    modal.classList.remove("is-open");
    modal.setAttribute("aria-hidden", "true");
    document.body.style.overflow = "";
  }

  /* ─────────────────────────────────────────────────────────────────────────
   * INIT
   * ───────────────────────────────────────────────────────────────────────── */

  function initCatalog() {
    var root = document.getElementById("spc-root");
    if (!root) return;

    staticUrl = root.dataset.staticUrl || "";

    var gallery = root.querySelector(".spc-gallery");

    /* Tab clicks → scroll gallery to corresponding card */
    root.querySelectorAll(".spc-tab[data-id]").forEach(function (tab) {
      tab.addEventListener("click", function () {
        var id = tab.dataset.id;
        if (gallery) {
          var card = gallery.querySelector('.spc-card[data-id="' + id + '"]');
          if (card) {
            var galleryRect = gallery.getBoundingClientRect();
            var cardRect = card.getBoundingClientRect();
            gallery.scrollBy({
              left: cardRect.left - galleryRect.left,
              behavior: "smooth",
            });
          }
        }
        syncActiveTab(id);
      });
    });

    /* Gallery scroll → sync active tab via IntersectionObserver */
    if (gallery && "IntersectionObserver" in window) {
      var cards = gallery.querySelectorAll(".spc-card[data-id]");
      if (cards.length) {
        var ratioMap = new Map();
        var observer = new IntersectionObserver(
          function (entries) {
            entries.forEach(function (entry) {
              ratioMap.set(entry.target.dataset.id, entry.intersectionRatio);
            });
            var bestId = null;
            var bestRatio = -1;
            ratioMap.forEach(function (ratio, id) {
              if (ratio > bestRatio) {
                bestRatio = ratio;
                bestId = id;
              }
            });
            if (bestId !== null) syncActiveTab(bestId);
          },
          { root: gallery, threshold: [0, 0.25, 0.5, 0.75, 1.0] },
        );
        cards.forEach(function (card) {
          observer.observe(card);
        });
      }
    }

    /* Card clicks → open modal */
    if (gallery) {
      gallery.addEventListener("click", function (e) {
        var card = e.target.closest(".spc-card[data-id]");
        if (card) openModal(card.dataset.id);
      });
      /* Keyboard: Enter / Space on focused card */
      gallery.addEventListener("keydown", function (e) {
        if (e.key === "Enter" || e.key === " ") {
          var card = e.target.closest(".spc-card[data-id]");
          if (card) {
            e.preventDefault();
            openModal(card.dataset.id);
          }
        }
      });
    }

    /* Modal close controls */
    var modalBg = document.getElementById("spc-modal-bg");
    var modalClose = document.getElementById("spc-modal-close");
    if (modalBg) modalBg.addEventListener("click", closeModal);
    if (modalClose) modalClose.addEventListener("click", closeModal);

    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") closeModal();
    });
  }

  document.addEventListener("DOMContentLoaded", initCatalog);
})();
