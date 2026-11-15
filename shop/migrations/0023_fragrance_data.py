"""Fill the 18 fragrances of the atelier (were hard-coded in fragrance_catalog.js)."""

from django.db import migrations

FRAGRANCES = [{'slug': 'ambre',
  'name': 'Ambre',
  'family': 'Oriental · Balsamique',
  'family_group': 'oriental',
  'notes': ['Ambre solaire', 'Résine précieuse', 'Vanille bourbon', 'Musc ambré'],
  'intensity': 4,
  'seasons': ['automne', 'hiver'],
  'moments': ['Soirée intimiste', 'Méditation', 'Lecture au coin du feu'],
  'pairs_with': ['Musc', 'Bois de santal', 'Cachemire et soie'],
  'description': "Distillé des résines millénaires de l'Orient, notre Ambre enveloppe l'espace d'une chaleur "
                 'profonde et somptueuse. Des notes vanillées et balsamiques se fondent dans un musc doré, '
                 "créant une présence enveloppante et indéfectible qui s'attarde longtemps après que la "
                 "flamme s'est éteinte.",
  'mood': "Pour les soirs où le temps s'arrête, quand la lumière ambrée des bougies efface doucement le "
          'monde extérieur.',
  'i18n': {'en': {'description': 'Distilled from the age-old resins of the Orient, our Amber wraps the room '
                                 'in deep, sumptuous warmth. Vanilla and balsamic notes melt into a golden '
                                 'musk, an enveloping presence that lingers long after the flame is out.',
                  'mood': 'For evenings when time stands still and the amber glow of candles gently erases '
                          'the world outside.'},
           'ua': {'description': 'Створена з давніх смол Сходу, наша Амбра огортає простір глибоким '
                                 'розкішним теплом. Ванільні та бальзамічні ноти розчиняються в золотистому '
                                 'мускусі й тримаються довго після того, як полум’я згасло.',
                  'mood': 'Для вечорів, коли час зупиняється, а бурштинове світло свічок тихо стирає '
                          'зовнішній світ.'},
           'ru': {'description': 'Созданная из древних смол Востока, наша Амбра окутывает пространство '
                                 'глубоким роскошным теплом. Ванильные и бальзамические ноты растворяются в '
                                 'золотистом мускусе и держатся ещё долго после того, как пламя погасло.',
                  'mood': 'Для вечеров, когда время останавливается, а янтарный свет свечей мягко стирает '
                          'внешний мир.'}},
  'static_image': 'assets/images/fragrances/ambre',
  'position': 0},
 {'slug': 'bergamote',
  'name': 'Bergamote',
  'family': 'Hespéridé · Frais',
  'family_group': 'hesperide',
  'notes': ['Bergamote de Calabre', 'Thé vert', 'Cèdre léger', 'Zeste de citron'],
  'intensity': 2,
  'seasons': ['printemps', 'ete'],
  'moments': ['Matin revigorant', 'Pause créative', 'Brunch dominical'],
  'pairs_with': ['Citron vert', "Fleur d'oranger", 'Eucalyptus'],
  'description': "La bergamote de Calabre, cueillie à l'aube dans les vergers baignés de soleil du sud de "
                 "l'Italie, distille une lumière citronnée d'une rare pureté. Son éclat hespéridé, finement "
                 "relevé de thé vert et d'un cèdre aérien, éveille les sens avec une légèreté qui tient "
                 'presque du miracle.',
  'mood': "L'éveil d'un matin méditerranéen, quand le soleil effleure à peine les toits dorés et que tout "
          'semble encore possible.',
  'i18n': {'en': {'description': 'Calabrian bergamot, picked at dawn in the sunlit orchards of southern '
                                 'Italy, gives off a lemony light of rare purity. Lifted with green tea and '
                                 'an airy cedar, it wakes the senses with an almost miraculous lightness.',
                  'mood': 'A Mediterranean morning, when the sun barely touches the golden roofs and '
                          'everything still seems possible.'},
           'ua': {'description': 'Калабрійський бергамот, зібраний на світанку в сонячних садах півдня '
                                 'Італії, дарує лимонне світло рідкісної чистоти. Зелений чай і легкий кедр '
                                 'додають йому повітряності, що м’яко пробуджує відчуття.',
                  'mood': 'Середземноморський ранок, коли сонце ледь торкається золотих дахів і все ще '
                          'здається можливим.'},
           'ru': {'description': 'Калабрийский бергамот, собранный на рассвете в солнечных садах юга Италии, '
                                 'дарит лимонный свет редкой чистоты. Зелёный чай и лёгкий кедр добавляют '
                                 'ему воздушности, мягко пробуждая чувства.',
                  'mood': 'Средиземноморское утро, когда солнце едва касается золотых крыш и всё ещё кажется '
                          'возможным.'}},
  'static_image': 'assets/images/fragrances/bergamote',
  'position': 1},
 {'slug': 'bois-de-oud',
  'name': 'Bois de oud',
  'family': 'Boisé · Oriental',
  'family_group': 'boise',
  'notes': ['Oud précieux', 'Encens sacré', 'Rose de Damas', 'Ambre noir', 'Résine de myrrhe'],
  'intensity': 5,
  'seasons': ['automne', 'hiver'],
  'moments': ['Cérémonie', 'Soirée de gala', 'Rituel méditatif'],
  'pairs_with': ['Ambre', 'Rose ancienne', 'Musc'],
  'description': "Le bois d'oud, trésor millénaire de l'Arabie et des forêts d'Asie du Sud-Est, se déploie "
                 "ici dans toute sa majesté ténébreuse et complexe. Mêlé à l'encens sacré et à la rose de "
                 "Damas, il compose une symphonie olfactive d'une intensité inégalée, aux résonances presque "
                 'sacrées qui transcendent le simple acte de parfumer un espace.',
  'mood': "Là où l'ombre devient velours et où chaque souffle est une prière murmurée à la nuit.",
  'i18n': {'en': {'description': 'Oud wood, an ancient treasure of Arabia and the forests of Southeast Asia, '
                                 'unfolds here in all its dark, complex majesty. With sacred incense and '
                                 'Damask rose it forms a scent of rare intensity, almost ceremonial.',
                  'mood': 'Where shadow turns to velvet and every breath is a prayer whispered to the '
                          'night.'},
           'ua': {'description': 'Уд — давній скарб Аравії та лісів Південно-Східної Азії — розкривається '
                                 'тут у всій своїй темній і складній величі. Зі священним ладаном і '
                                 'дамаською трояндою він створює аромат рідкісної, майже церемоніальної '
                                 'глибини.',
                  'mood': 'Там, де тінь стає оксамитом, а кожен подих — молитвою, прошепотіною ночі.'},
           'ru': {'description': 'Уд — древнее сокровище Аравии и лесов Юго-Восточной Азии — раскрывается '
                                 'здесь во всём своём тёмном и сложном величии. Со священным ладаном и '
                                 'дамасской розой он создаёт аромат редкой, почти церемониальной глубины.',
                  'mood': 'Там, где тень становится бархатом, а каждый вдох — молитвой, прошёптанной ночи.'}},
  'static_image': 'assets/images/fragrances/bois-de-oud',
  'position': 2},
 {'slug': 'bois-de-rose',
  'name': 'Bois de rose',
  'family': 'Floral · Boisé',
  'family_group': 'floral',
  'notes': ['Bois de rose', 'Pétale de rose', 'Cèdre doux', 'Iris poudré'],
  'intensity': 3,
  'seasons': ['printemps', 'automne'],
  'moments': ['Après-midi doux', 'Lecture', 'Bain parfumé'],
  'pairs_with': ['Rose ancienne', 'Jasmin', 'Musc'],
  'description': "Issu des essences précieuses des forêts brésiliennes avec la délicatesse d'un artisan "
                 'parfumeur, le bois de rose exhale une douceur florale et boisée à la fois tendre et '
                 "profondément raffinée. L'iris poudré apporte une profondeur romantique à cette composition "
                 "d'une grâce naturelle.",
  'mood': "La douceur d'une fin d'après-midi rosée, quand le jardin respire encore la chaleur du soleil "
          'déclinant.',
  'i18n': {'en': {'description': 'Rosewood breathes a floral, woody softness, tender and deeply refined. '
                                 'Powdery iris adds a romantic depth to a composition of natural grace.',
                  'mood': 'The softness of a rosy late afternoon, when the garden still breathes the warmth '
                          'of the setting sun.'},
           'ua': {'description': 'Рожеве дерево дихає квітковою деревною м’якістю — ніжною і вишуканою. '
                                 'Пудровий ірис додає романтичної глибини композиції природної грації.',
                  'mood': 'Ніжність рожевого надвечір’я, коли сад ще дихає теплом призахідного сонця.'},
           'ru': {'description': 'Розовое дерево дышит цветочной древесной мягкостью — нежной и утончённой. '
                                 'Пудровый ирис добавляет романтической глубины композиции природной грации.',
                  'mood': 'Нежность розового предвечерья, когда сад ещё дышит теплом заходящего солнца.'}},
  'static_image': 'assets/images/fragrances/bois-de-rose',
  'position': 3},
 {'slug': 'bois-de-santal',
  'name': 'Bois de santal',
  'family': 'Boisé · Crémeux',
  'family_group': 'boise',
  'notes': ['Santal de Mysore', 'Vanille crémeuse', 'Cèdre Atlas', 'Musc soyeux'],
  'intensity': 3,
  'seasons': ['printemps', 'automne', 'hiver'],
  'moments': ['Méditation', 'Yoga', 'Soirée zen'],
  'pairs_with': ['Ambre', 'Musc', 'Cachemire et soie'],
  'description': "Le santal de Mysore, aux notes lactées et crémeuses d'une onctuosité divine, incarne la "
                 'quintessence du calme et de la sérénité intérieure. Sa texture olfactive enveloppante, '
                 "dorée de vanille et soulignée d'un cèdre Atlas d'une austère beauté, invite à un voyage "
                 'immobile vers les profondeurs de soi.',
  'mood': 'Quand le silence devient confort et que chaque respiration lente devient, enfin, un acte de paix.',
  'i18n': {'en': {'description': 'Mysore sandalwood, milky and creamy, is the very essence of calm. Its '
                                 'enveloping texture, gilded with vanilla and underlined by an austere Atlas '
                                 'cedar, invites a still journey inward.',
                  'mood': 'When silence becomes comfort and every slow breath is, at last, an act of peace.'},
           'ua': {'description': 'Майсурський сандал, молочний і вершковий, — сама суть спокою. Його '
                                 'обволікаюча текстура з ваніллю та стриманим атлаським кедром запрошує до '
                                 'тихої подорожі всередину себе.',
                  'mood': 'Коли тиша стає затишком, а кожен повільний подих — нарешті актом спокою.'},
           'ru': {'description': 'Майсурский сандал, молочный и сливочный, — сама суть спокойствия. Его '
                                 'обволакивающая текстура с ванилью и строгим атласским кедром приглашает в '
                                 'тихое путешествие внутрь себя.',
                  'mood': 'Когда тишина становится уютом, а каждый медленный вдох — наконец актом покоя.'}},
  'static_image': 'assets/images/fragrances/bois-de-santal',
  'position': 4},
 {'slug': 'cachemire-et-soie',
  'name': 'Cachemire et soie',
  'family': 'Poudrée · Musc',
  'family_group': 'poudre',
  'notes': ['Musc cachemire', 'Iris poudré', 'Santal blanc', 'Ambre doux', 'Ylang-ylang'],
  'intensity': 3,
  'seasons': ['automne', 'hiver'],
  'moments': ['Soirée intime', 'Cocooning', 'Lecture au coin du feu'],
  'pairs_with': ['Ambre', 'Musc', 'Bois de santal'],
  'description': "Imaginée comme la caresse d'un tissu de haute couture sur la peau nue, cette fragrance "
                 "conjugue le moelleux du cachemire et la fluidité de la soie dans un accord poudré d'une "
                 "sophistication absolue. L'iris et le santal blanc y déposent leur signature de haute "
                 "parfumerie, pendant que l'ylang-ylang insuffle une chaleur délicatement sensuelle.",
  'mood': "Le luxe discret des soirs d'hiver, enveloppée dans la douceur soyeuse de ce que l'on chérit le "
          'plus.',
  'i18n': {'en': {'description': 'Imagined as the touch of couture fabric on bare skin, this fragrance joins '
                                 'the softness of cashmere and the flow of silk in a powdery accord. Iris '
                                 'and white sandalwood sign it; ylang-ylang adds a gently sensual warmth.',
                  'mood': 'The quiet luxury of winter evenings, wrapped in the silky softness of what we '
                          'cherish most.'},
           'ua': {'description': 'Задуманий як дотик кутюрної тканини до шкіри, цей аромат поєднує м’якість '
                                 'кашеміру та плинність шовку в пудровому акорді. Ірис і білий сандал '
                                 'підписують його, іланг-іланг додає ніжного чуттєвого тепла.',
                  'mood': 'Тиха розкіш зимових вечорів, огорнутих шовковою м’якістю того, що нам '
                          'найдорожче.'},
           'ru': {'description': 'Задуманный как прикосновение кутюрной ткани к коже, этот аромат соединяет '
                                 'мягкость кашемира и текучесть шёлка в пудровом аккорде. Ирис и белый '
                                 'сандал подписывают его, иланг-иланг добавляет нежного чувственного тепла.',
                  'mood': 'Тихая роскошь зимних вечеров, окутанных шёлковой мягкостью того, что нам дороже '
                          'всего.'}},
  'static_image': 'assets/images/fragrances/cachemire-et-soie',
  'position': 5},
 {'slug': 'citron-vert',
  'name': 'Citron vert',
  'family': 'Hespéridé · Vert',
  'family_group': 'hesperide',
  'notes': ['Citron vert pressé', 'Menthe verte', 'Basilic frais', 'Vétiver léger'],
  'intensity': 2,
  'seasons': ['printemps', 'ete'],
  'moments': ['Matin pétillant', 'Brunch estival', 'Séance sportive'],
  'pairs_with': ['Bergamote', 'Eucalyptus', "Fleur d'oranger"],
  'description': "Le jus vif et acidulé du citron vert tropical éclate dans l'espace comme un rayon de "
                 "lumière pure, ponctué de la vivacité de la menthe fraîche et de l'élégance herbacée du "
                 'basilic. Une invitation directe à la légèreté et à la vitalité des matinées estivales.',
  'mood': "La pétillance d'un matin d'été qui promet une journée de lumière sans nuages ni compromis.",
  'i18n': {'en': {'description': 'The bright, tangy juice of lime bursts into the room like pure light, with '
                                 'fresh mint and the herbal elegance of basil. A straightforward invitation '
                                 'to the lightness of summer mornings.',
                  'mood': 'The sparkle of a summer morning that promises a cloudless day.'},
           'ua': {'description': 'Яскравий кислуватий сік лайма спалахує в просторі, мов чисте світло, разом '
                                 'зі свіжою м’ятою та трав’янистою елегантністю базиліку. Пряме запрошення '
                                 'до легкості літніх ранків.',
                  'mood': 'Іскристість літнього ранку, що обіцяє безхмарний день.'},
           'ru': {'description': 'Яркий кисловатый сок лайма вспыхивает в пространстве, словно чистый свет, '
                                 'вместе со свежей мятой и травянистой элегантностью базилика. Прямое '
                                 'приглашение к лёгкости летних утр.',
                  'mood': 'Искристость летнего утра, обещающего безоблачный день.'}},
  'static_image': 'assets/images/fragrances/citron-vert',
  'position': 6},
 {'slug': 'coquelicot',
  'name': 'Coquelicot',
  'family': 'Floral · Poudré',
  'family_group': 'floral',
  'notes': ['Pétale de coquelicot', 'Iris', 'Rose légère', 'Musc poudré'],
  'intensity': 2,
  'seasons': ['printemps', 'ete'],
  'moments': ['Promenade champêtre', 'Dimanche matin', 'Pique-nique'],
  'pairs_with': ['Mimosa', "Fleur d'acacia", 'Rose ancienne'],
  'description': 'Né dans les champs de Provence où le vent fait danser les corolles cramoisies à perte de '
                 "vue, notre Coquelicot capture la légèreté poudreuse d'une fleur sauvage d'une sincérité "
                 "touchante. Un floral délicat et nostalgique, tendre comme un souvenir d'enfance retrouvé "
                 "au détour d'une promenade.",
  'mood': "Le vertige doux d'un champ fleuri traversé au petit matin, quand la rosée pèse encore sur chaque "
          'pétale fragile.',
  'i18n': {'en': {'description': 'Born in the fields of Provence where the wind sets crimson petals dancing, '
                                 'our Poppy captures the powdery lightness of a wild flower. Delicate and '
                                 'nostalgic, like a childhood memory found on a walk.',
                  'mood': 'The gentle dizziness of a field crossed at dawn, when dew still weighs on every '
                          'petal.'},
           'ua': {'description': 'Народжений у полях Провансу, де вітер колише багряні пелюстки, наш Мак '
                                 'передає пудрову легкість дикої квітки. Ніжний і ностальгічний, як дитячий '
                                 'спогад, знайдений на прогулянці.',
                  'mood': 'Легке запаморочення від поля, перейденого на світанку, коли роса ще важить на '
                          'кожній пелюстці.'},
           'ru': {'description': 'Рождённый в полях Прованса, где ветер колышет багряные лепестки, наш Мак '
                                 'передаёт пудровую лёгкость дикого цветка. Нежный и ностальгический, как '
                                 'детское воспоминание, найденное на прогулке.',
                  'mood': 'Лёгкое головокружение от поля, пройденного на рассвете, когда роса ещё тяжела на '
                          'каждом лепестке.'}},
  'static_image': 'assets/images/fragrances/coquelicot',
  'position': 7},
 {'slug': 'eucalyptus',
  'name': 'Eucalyptus',
  'family': 'Aromatique · Frais',
  'family_group': 'aromatique',
  'notes': ['Eucalyptus globulus', 'Menthe poivrée', 'Cèdre frais', 'Cyprès vert'],
  'intensity': 3,
  'seasons': ['printemps', 'hiver'],
  'moments': ['Méditation matinale', 'Exercice', 'Clarté mentale'],
  'pairs_with': ['Lavande', 'Bergamote', 'Citron vert'],
  'description': "L'eucalyptus, distillé dans sa pureté la plus absolue, ouvre les sens d'un souffle camphré "
                 "et cristallin qui purifie l'air de toute lourdeur. La menthe poivrée et le cyprès vert lui "
                 "confèrent une dimension aromatique et forestière qui éveille l'esprit, clarifie les "
                 "pensées, et rend l'impossible soudainement accessible.",
  'mood': "La sensation de respirer profondément au cœur d'une forêt au petit matin, l'esprit libre et le "
          'corps vif.',
  'i18n': {'en': {'description': 'Eucalyptus in its purest form opens the senses with a clear, camphor '
                                 'breath that clears the air. Peppermint and green cypress add an aromatic, '
                                 'forest depth that wakes the mind.',
                  'mood': 'Breathing deeply in a forest early in the morning, mind free and body awake.'},
           'ua': {'description': 'Евкаліпт у найчистішому вигляді відкриває відчуття прозорим камфорним '
                                 'подихом, що очищує повітря. Перцева м’ята й зелений кипарис додають '
                                 'ароматичної лісової глибини, що бадьорить розум.',
                  'mood': 'Глибокий подих у лісі рано-вранці — вільна думка й бадьоре тіло.'},
           'ru': {'description': 'Эвкалипт в чистейшем виде открывает чувства прозрачным камфорным дыханием, '
                                 'очищающим воздух. Перечная мята и зелёный кипарис добавляют ароматической '
                                 'лесной глубины, бодрящей ум.',
                  'mood': 'Глубокий вдох в лесу ранним утром — свободная мысль и бодрое тело.'}},
  'static_image': 'assets/images/fragrances/eucalyptus',
  'position': 8},
 {'slug': 'figue-et-santal',
  'name': 'Figue et Santal',
  'family': 'Boisé · Fruité',
  'family_group': 'boise',
  'notes': ['Figue mûre', 'Santal crémeux', 'Lait de figuier', 'Musc boisé'],
  'intensity': 3,
  'seasons': ['ete', 'automne'],
  'moments': ["Fin d'après-midi", 'Apéritif méditerranéen', 'Dîner en terrasse'],
  'pairs_with': ['Bois de santal', 'Mimosa', "Fleur d'oranger"],
  'description': 'La figue gorgée de soleil méditerranéen se fond dans la chaleur crémeuse du santal dans '
                 "une union olfactive d'une gourmandise exquise et d'une sensualité nonchalante. Le lait de "
                 'figuier apporte une note lactée et légèrement verte qui évoque les jardins ombragés de la '
                 'Provence en plein août.',
  'mood': "Un après-midi suspendu sous les figuiers anciens, où le temps s'écoule à la cadence des cigales "
          'et du vent tiède.',
  'i18n': {'en': {'description': 'Sun-ripened Mediterranean fig melts into creamy sandalwood, gourmand and '
                                 'nonchalantly sensual. Fig milk adds a milky, slightly green note that '
                                 'recalls the shaded gardens of Provence in August.',
                  'mood': 'An afternoon held under old fig trees, time flowing to the rhythm of cicadas and '
                          'warm wind.'},
           'ua': {'description': 'Стигла середземноморська фіга розчиняється у вершковому сандалі — ласо й '
                                 'невимушено чуттєво. Фігове молочко додає молочної, злегка зеленої ноти, що '
                                 'нагадує тінисті сади Провансу в серпні.',
                  'mood': 'День, що завмер під старими фіговими деревами, де час тече в ритмі цикад і '
                          'теплого вітру.'},
           'ru': {'description': 'Спелый средиземноморский инжир растворяется в сливочном сандале — лакомо и '
                                 'непринуждённо чувственно. Инжирное молочко добавляет молочной, слегка '
                                 'зелёной ноты, напоминающей тенистые сады Прованса в августе.',
                  'mood': 'День, застывший под старыми инжирными деревьями, где время течёт в ритме цикад и '
                          'тёплого ветра.'}},
  'static_image': 'assets/images/fragrances/figue-et-santal',
  'position': 9},
 {'slug': 'fleur-dacacia',
  'name': "Fleur d'acacia",
  'family': 'Floral · Miellé',
  'family_group': 'floral',
  'notes': ["Fleur d'acacia", 'Miel de Provence', 'Jasmin blanc', 'Musc floral'],
  'intensity': 2,
  'seasons': ['printemps', 'ete'],
  'moments': ['Matin ensoleillé', 'Jardin fleuri', 'Goûter délicat'],
  'pairs_with': ['Mimosa', 'Coquelicot', "Fleur d'oranger"],
  'description': "La fleur d'acacia, délicate et mellifère comme une bénédiction printanière, distille ses "
                 'notes dorées et miellées avec une générosité ensoleillée. Le jasmin blanc lui prête sa '
                 "sensualité discrète et envoûtante, créant un bouquet champêtre d'une douceur à la fois "
                 'innocente et inoubliable.',
  'mood': 'Le printemps dans sa plus tendre expression, quand les abeilles bourdonnent et que la lumière du '
          'matin est encore toute dorée.',
  'i18n': {'en': {'description': 'Acacia flower, delicate and honeyed like a spring blessing, gives off '
                                 'golden notes with sunny generosity. White jasmine adds a discreet '
                                 'sensuality to a country bouquet, innocent and unforgettable.',
                  'mood': 'Spring at its most tender, when bees hum and the morning light is still golden.'},
           'ua': {'description': 'Квітка акації, ніжна й медова, мов весняне благословення, щедро дарує '
                                 'золотисті ноти. Білий жасмин додає стриманої чуттєвості цьому сільському '
                                 'букету — невинному й незабутньому.',
                  'mood': 'Весна в найніжнішому прояві, коли гудуть бджоли, а ранкове світло ще золоте.'},
           'ru': {'description': 'Цветок акации, нежный и медовый, словно весеннее благословение, щедро '
                                 'дарит золотистые ноты. Белый жасмин добавляет сдержанной чувственности '
                                 'этому деревенскому букету — невинному и незабываемому.',
                  'mood': 'Весна в самом нежном проявлении, когда жужжат пчёлы, а утренний свет ещё '
                          'золотой.'}},
  'static_image': 'assets/images/fragrances/fleur-dacacia',
  'position': 10},
 {'slug': 'fleur-doranger',
  'name': "Fleur d'oranger",
  'family': 'Floral · Néroli',
  'family_group': 'floral',
  'notes': ['Néroli absolu', "Fleur d'oranger", 'Bergamote dorée', 'Musc blanc', 'Cèdre'],
  'intensity': 3,
  'seasons': ['printemps', 'ete'],
  'moments': ['Cérémonie', 'Spa', 'Moment de sérénité'],
  'pairs_with': ['Jasmin', 'Mimosa', 'Bergamote'],
  'description': "Le néroli absolu, extrait à la main des fragiles fleurs d'oranger amer de Tunisie, porte "
                 "en lui la quintessence lumineuse de la Méditerranée — solaire, d'une pureté presque "
                 "ineffable, et d'une délicatesse infinie. Cette fragrance évoque les jardins d'Andalousie "
                 'en fleur, entre blancheur éclatante et ivresse sucrée.',
  'mood': "La pureté d'un matin de cérémonie, quand les fleurs d'oranger parfument encore le vent marin et "
          'que tout commence.',
  'i18n': {'en': {'description': 'Neroli absolute, from the fragile bitter-orange blossoms of Tunisia, '
                                 'carries the luminous essence of the Mediterranean: sunny, pure and '
                                 'infinitely delicate. It recalls the flowering gardens of Andalusia.',
                  'mood': 'The purity of a ceremony morning, when orange blossom still scents the sea breeze '
                          'and everything begins.'},
           'ua': {'description': 'Абсолют неролі з тендітних квітів гіркого апельсина Тунісу несе світлу '
                                 'суть Середземномор’я: сонячну, чисту й безмежно ніжну. Він нагадує квітучі '
                                 'сади Андалусії.',
                  'mood': 'Чистота ранку церемонії, коли апельсиновий цвіт ще наповнює морський вітер і все '
                          'тільки починається.'},
           'ru': {'description': 'Абсолют нероли из хрупких цветков горького апельсина Туниса несёт светлую '
                                 'суть Средиземноморья: солнечную, чистую и бесконечно нежную. Он напоминает '
                                 'цветущие сады Андалусии.',
                  'mood': 'Чистота утра церемонии, когда апельсиновый цвет ещё наполняет морской ветер и всё '
                          'только начинается.'}},
  'static_image': 'assets/images/fragrances/fleur-doranger',
  'position': 11},
 {'slug': 'jasmin',
  'name': 'Jasmin',
  'family': 'Floral · Sensuel',
  'family_group': 'floral',
  'notes': ['Jasmin de Grasse', 'Rose absolue', 'Ylang-ylang', 'Musc sensuel', 'Santal doux'],
  'intensity': 4,
  'seasons': ['ete', 'automne'],
  'moments': ['Soirée romantique', 'Bain précieux', 'Coucher de soleil'],
  'pairs_with': ['Rose ancienne', "Fleur d'oranger", 'Musc'],
  'description': 'Le jasmin de Grasse, roi incontesté de la haute parfumerie française depuis des siècles, '
                 'déploie ici ses facettes les plus sensuelles et envoûtantes, magnifiées par la rose '
                 "absolue et l'ylang-ylang tropical. Un floral d'une intensité charnelle et profondément "
                 "raffinée, destiné aux nuits qui méritent d'être mémorables.",
  'mood': 'Les nuits tièdes où la peau garde encore la chaleur du soleil couché, et où chaque heure qui '
          'passe est un cadeau.',
  'i18n': {'en': {'description': 'Jasmine from Grasse, for centuries the king of French perfumery, shows its '
                                 'most sensual side here, heightened by rose absolute and ylang-ylang. A '
                                 'rich, refined floral for nights worth remembering.',
                  'mood': 'Warm nights when the skin still holds the setting sun, and every passing hour is '
                          'a gift.'},
           'ua': {'description': 'Жасмин із Грасу, століттями король французької парфумерії, показує тут '
                                 'свій найчуттєвіший бік, підкреслений абсолютом троянди й іланг-ілангом. '
                                 'Насичений вишуканий квітковий аромат для ночей, які варто запам’ятати.',
                  'mood': 'Теплі ночі, коли шкіра ще зберігає призахідне сонце, а кожна година — подарунок.'},
           'ru': {'description': 'Жасмин из Граса, веками король французской парфюмерии, показывает здесь '
                                 'свою самую чувственную сторону, подчёркнутую абсолютом розы и '
                                 'иланг-илангом. Насыщенный утончённый цветочный аромат для ночей, которые '
                                 'стоит запомнить.',
                  'mood': 'Тёплые ночи, когда кожа ещё хранит закатное солнце, а каждый час — подарок.'}},
  'static_image': 'assets/images/fragrances/jasmin',
  'position': 12},
 {'slug': 'lavande',
  'name': 'Lavande',
  'family': 'Aromatique · Lavande',
  'family_group': 'aromatique',
  'notes': ['Lavande fine de Haute-Provence', 'Romarin sauvage', 'Cèdre', 'Musc frais'],
  'intensity': 3,
  'seasons': ['printemps', 'ete'],
  'moments': ['Coucher', 'Relaxation', 'Bain du soir'],
  'pairs_with': ['Eucalyptus', 'Bergamote', 'Musc'],
  'description': "La lavande fine de Haute-Provence, cueillie sur les plateaux de Valensole au cœur de l'été "
                 'provençal, déploie ses effluves aromatiques avec une authenticité et une sérénité sans '
                 'égales. Le romarin sauvage et le cèdre viennent ancrer cette composition dans une '
                 "profondeur sèche et méditerranéenne d'une beauté toute simple.",
  'mood': 'Le soir tombant sur les champs mauves du Vaucluse, quand la chaleur de la journée cède enfin la '
          'place au silence et à la douceur.',
  'i18n': {'en': {'description': 'Fine lavender from Haute-Provence, picked on the Valensole plateau in high '
                                 'summer, gives off its aromatic scent with calm authenticity. Wild rosemary '
                                 'and cedar anchor it in a dry, Mediterranean depth.',
                  'mood': "Evening falling on the mauve fields of the Vaucluse, when the day's heat finally "
                          'gives way to silence.'},
           'ua': {'description': 'Тонка лаванда Верхнього Провансу, зібрана на плато Валансоль серед літа, '
                                 'дарує свій ароматичний запах зі спокійною автентичністю. Дикий розмарин і '
                                 'кедр додають сухої середземноморської глибини.',
                  'mood': 'Вечір над бузковими полями Воклюзу, коли денна спека нарешті поступається тиші.'},
           'ru': {'description': 'Тонкая лаванда Верхнего Прованса, собранная на плато Валансоль в разгар '
                                 'лета, дарит свой ароматический запах со спокойной подлинностью. Дикий '
                                 'розмарин и кедр добавляют сухой средиземноморской глубины.',
                  'mood': 'Вечер над сиреневыми полями Воклюза, когда дневной зной наконец уступает '
                          'тишине.'}},
  'static_image': 'assets/images/fragrances/lavande',
  'position': 13},
 {'slug': 'mimosa',
  'name': 'Mimosa',
  'family': 'Floral · Solaire',
  'family_group': 'floral',
  'notes': ['Mimosa de Cannes', "Fleur d'acacia", 'Vanille dorée', 'Cèdre léger'],
  'intensity': 3,
  'seasons': ['printemps', 'ete'],
  'moments': ['Réveil lumineux', 'Brunch dominical', 'Escapade en Riviera'],
  'pairs_with': ["Fleur d'acacia", "Fleur d'oranger", 'Bergamote'],
  'description': "Hommage vibrant à la Côte d'Azur en février, quand les mimosas explosent de lumière jaune "
                 "sur fond d'azur, cette fragrance capte l'essence même de la joie méditerranéenne. Dorée, "
                 "légèrement miellée et poudrée comme un rayon de soleil hivernal, elle est l'évocation d'un "
                 'bonheur simple, lumineux et sans calcul.',
  'mood': "L'allégresse d'un matin de février sur la promenade de Cannes, les bras chargés de mimosa et le "
          'cœur entièrement léger.',
  'i18n': {'en': {'description': 'A tribute to the Côte d’Azur in February, when mimosa bursts yellow '
                                 'against the blue, this fragrance holds the essence of Mediterranean joy. '
                                 'Golden, lightly honeyed and powdery like winter sun: a simple, bright '
                                 'happiness.',
                  'mood': 'A February morning on the Cannes promenade, arms full of mimosa and heart '
                          'completely light.'},
           'ua': {'description': 'Присвята Лазуровому берегу в лютому, коли мімоза спалахує жовтим на '
                                 'блакиті, цей аромат зберігає саму суть середземноморської радості. '
                                 'Золотистий, злегка медовий і пудровий, як зимове сонце, — просте світле '
                                 'щастя.',
                  'mood': 'Лютневий ранок на набережній Канн, оберемок мімози в руках і зовсім легке серце.'},
           'ru': {'description': 'Посвящение Лазурному берегу в феврале, когда мимоза вспыхивает жёлтым на '
                                 'голубом, этот аромат хранит саму суть средиземноморской радости. '
                                 'Золотистый, слегка медовый и пудровый, как зимнее солнце, — простое '
                                 'светлое счастье.',
                  'mood': 'Февральское утро на набережной Канн, охапка мимозы в руках и совсем лёгкое '
                          'сердце.'}},
  'static_image': 'assets/images/fragrances/mimosa',
  'position': 14},
 {'slug': 'musc',
  'name': 'Musc',
  'family': 'Musqué · Propre',
  'family_group': 'poudre',
  'notes': ['Musc blanc', 'Iris poudré', 'Cèdre doux', 'Ambre gris'],
  'intensity': 2,
  'seasons': ['printemps', 'ete', 'automne', 'hiver'],
  'moments': ['Quotidien raffiné', 'Télétravail', 'Quiétude'],
  'pairs_with': ['Ambre', 'Cachemire et soie', 'Bois de santal'],
  'description': 'Le musc blanc, intemporel et universel comme la peau propre après le bain, est ici '
                 "distillé dans sa plus grande pureté, rehaussé d'iris poudrée et d'ambre gris pour une "
                 "signature olfactive d'une discrétion absolument sensuelle. Une fragrance de fond que l'on "
                 "ne remarque pas tout de suite, mais dont l'absence se ferait immédiatement ressentir.",
  'mood': "La présence invisible qui embellit l'ordinaire — le parfum de ce qui est simplement et "
          'profondément beau.',
  'i18n': {'en': {'description': 'White musk, timeless like clean skin after a bath, is distilled here at '
                                 'its purest, lifted with powdery iris and ambergris. A background scent you '
                                 'don’t notice at first, but would miss at once.',
                  'mood': 'The invisible presence that makes the ordinary beautiful.'},
           'ua': {'description': 'Білий мускус, позачасовий, як чиста шкіра після ванни, тут у найчистішому '
                                 'вигляді, з пудровим ірисом і сірою амброю. Фоновий аромат, який спершу не '
                                 'помічаєш, але одразу відчуєш, коли його не стане.',
                  'mood': 'Невидима присутність, що робить буденне красивим.'},
           'ru': {'description': 'Белый мускус, вневременной, как чистая кожа после ванны, здесь в чистейшем '
                                 'виде, с пудровым ирисом и серой амброй. Фоновый аромат, который сначала не '
                                 'замечаешь, но сразу почувствуешь, если его не станет.',
                  'mood': 'Незримое присутствие, делающее обыденное красивым.'}},
  'static_image': 'assets/images/fragrances/musc',
  'position': 15},
 {'slug': 'rose-ancienne',
  'name': 'Rose ancienne',
  'family': 'Floral · Rose',
  'family_group': 'floral',
  'notes': ['Rose de Mai', 'Rose de Damas', 'Patchouli terre', 'Musc ambré', 'Oud léger'],
  'intensity': 4,
  'seasons': ['printemps', 'automne'],
  'moments': ['Soirée élégante', 'Cérémonie', 'Après-midi à la française'],
  'pairs_with': ['Jasmin', 'Bois de oud', 'Ambre'],
  'description': 'Évocatrice des roseraies des châteaux de la Loire au tournant du siècle, notre Rose '
                 'ancienne convoque les deux roses les plus précieuses de la haute parfumerie dans un accord '
                 "d'une profondeur et d'une richesse remarquables. Le patchouli et l'oud y ajoutent une "
                 "ombre séduisante qui confère à cette rose toute la noblesse qu'elle mérite.",
  'mood': "La grâce anachronique d'un jardin à la française, où chaque rose ouverte est un sonnet de pétales "
          "que personne n'a encore pensé à écrire.",
  'i18n': {'en': {'description': 'Recalling the rose gardens of the Loire châteaux, our Old Rose brings '
                                 'together the two most precious roses of fine perfumery in a deep, rich '
                                 'accord. Patchouli and oud add a seductive shadow.',
                  'mood': 'The timeless grace of a French garden, where every open rose is a sonnet of '
                          'petals.'},
           'ua': {'description': 'Нагадуючи трояндові сади замків Луари, наша Стара троянда поєднує дві '
                                 'найцінніші троянди парфумерії в глибокому насиченому акорді. Пачулі та уд '
                                 'додають спокусливої тіні.',
                  'mood': 'Позачасова грація французького саду, де кожна розкрита троянда — сонет із '
                          'пелюсток.'},
           'ru': {'description': 'Напоминая розовые сады замков Луары, наша Старинная роза соединяет две '
                                 'самые ценные розы парфюмерии в глубоком насыщенном аккорде. Пачули и уд '
                                 'добавляют соблазнительной тени.',
                  'mood': 'Вневременная грация французского сада, где каждая раскрытая роза — сонет из '
                          'лепестков.'}},
  'static_image': 'assets/images/fragrances/rose-ancienne',
  'position': 16},
 {'slug': 'rosa',
  'name': 'Rosa',
  'family': 'Floral · Frais',
  'family_group': 'floral',
  'notes': ['Rose thé fraîche', "Pétale de rose d'Ispahan", 'Cèdre blanc', 'Musc vert'],
  'intensity': 3,
  'seasons': ['printemps', 'ete'],
  'moments': ['Matin délicat', 'Jardin anglais', 'Pause gourmande'],
  'pairs_with': ['Rose ancienne', 'Coquelicot', "Fleur d'oranger"],
  'description': 'Lumineuse et légèrement aquatique, Rosa saisit la rose dans sa jeunesse la plus fraîche et '
                 "sa beauté la plus cristalline, avant que le soleil n'ait encore eu le temps de sécher la "
                 "rosée sur ses pétales. La rose thé, d'une finesse rare, s'unit au musc vert et au cèdre "
                 'blanc dans une transparence printanière qui émeut par sa simplicité parfaite.',
  'mood': "La grâce des premières roses d'été au petit matin, quand le jardin est encore silencieux et que "
          "tout semble d'une fraîcheur miraculeuse.",
  'i18n': {'en': {'description': 'Bright and slightly watery, Rosa captures the rose at its freshest, before '
                                 'the sun has dried the dew. Fine tea rose joins green musk and white cedar '
                                 'in a spring-like transparency.',
                  'mood': 'The first summer roses early in the morning, when the garden is still silent and '
                          'everything feels fresh.'},
           'ua': {'description': 'Світла й трохи водяниста, Rosa ловить троянду в її найсвіжішій миті, поки '
                                 'сонце ще не висушило росу. Тонка чайна троянда поєднується із зеленим '
                                 'мускусом і білим кедром у весняній прозорості.',
                  'mood': 'Перші літні троянди рано-вранці, коли сад ще мовчить і все здається свіжим.'},
           'ru': {'description': 'Светлая и немного водянистая, Rosa ловит розу в её самый свежий миг, пока '
                                 'солнце ещё не высушило росу. Тонкая чайная роза соединяется с зелёным '
                                 'мускусом и белым кедром в весенней прозрачности.',
                  'mood': 'Первые летние розы ранним утром, когда сад ещё молчит и всё кажется свежим.'}},
  'static_image': 'assets/images/fragrances/rosa',
  'position': 17}]


def load(apps, schema_editor):
    Fragrance = apps.get_model("shop", "Fragrance")
    for row in FRAGRANCES:
        Fragrance.objects.update_or_create(slug=row["slug"], defaults=row)


def unload(apps, schema_editor):
    Fragrance = apps.get_model("shop", "Fragrance")
    Fragrance.objects.filter(slug__in=[r["slug"] for r in FRAGRANCES]).delete()


class Migration(migrations.Migration):
    dependencies = [("shop", "0022_fragrance")]
    operations = [migrations.RunPython(load, unload)]
