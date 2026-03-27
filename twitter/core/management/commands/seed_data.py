"""
Management command: seed_data.py
Place this file at:  yourapp/management/commands/seed_data.py

Make sure management/ and management/commands/ both have an empty __init__.py

Usage:
    python manage.py seed_data
    python manage.py seed_data --users 20 --tweets 200
    python manage.py seed_data --clear
    python manage.py seed_data --no-media
"""

import os
import random
import glob
from django.core.management.base import BaseCommand
from django.utils import timezone
from django.core.files import File
from django.db import transaction

# ── adjust this import path to match your actual app name ─────────────────────
from core.models import User, Tweet, Like, Bookmark, Hashtag, Notification, Message
# ───────────────────────────────────────────────────────────────────────────────

STATIC_MEDIA_DIR = r"D:\static\admin\Backup"
SUPPORTED_EXTENSIONS = (".jpg", ".jpeg", ".png", ".gif", ".webp")


# ══════════════════════════════════════════════════════════════════════════════
#  DATA POOLS
# ══════════════════════════════════════════════════════════════════════════════

USERNAMES = [
    "alex_codes", "priya_writes", "omar_dev", "sara_ux", "luca_ml",
    "nina_data", "ben_crypto", "yui_design", "carlos_ops", "fatima_backend",
    "jake_mobile", "aisha_cloud", "ryan_sec", "zoe_devrel", "mike_sre",
    "msee_wa_tech", "nairobi_ninja", "wakanda_coder", "kenyan_grind", "mama_mboga_254",
    "jua_kali_dev", "nai_vibes", "uhuru_wa_code", "buda_wa_net", "genge_msee",
    "kioo_cha_nai", "shida_solver", "mtaa_mgeni", "digital_omera", "msichana_codes",
    "chef_mwitu", "fitness_tz", "afro_beats_ke", "hustle_daily", "street_art_254",
    "nairobi_foodie", "safari_shots", "eastlands_elite", "CBD_diaries", "thika_road_tales",
]

DISPLAY_NAMES = [
    "Alex Chen", "Priya Patel", "Omar Hassan", "Sara Williams", "Luca Ferrari",
    "Nina Johansson", "Ben Carter", "Yui Tanaka", "Carlos Rivera", "Fatima Al-Amin",
    "Jake Thompson", "Aisha Okafor", "Ryan Murphy", "Zoe Dubois", "Mike Stevens",
    "Msee wa Tech 🇰🇪", "Nairobi Ninja", "Wakanda Coder", "Kenyan Grind 💪", "Mama Mboga 254",
    "Jua Kali Dev", "Nai Vibes ✨", "Uhuru wa Code", "Buda wa Net", "Genge Msee",
    "Kioo cha Nai", "Shida Solver", "Mtaa Mgeni", "Digital Omera", "Msichana Codes 👩‍💻",
    "Chef Mwitu 🍖", "Fitness TZ 💪", "Afro Beats KE 🎵", "Hustle Daily", "Street Art 254 🎨",
    "Nairobi Foodie 🍽️", "Safari Shots 📸", "Eastlands Elite", "CBD Diaries", "Thika Road Tales",
]

BIOS = [
    "Building things on the internet. Coffee addict. ☕",
    "Full-stack dev | Open source | Dog lover 🐶",
    "ML engineer by day, gamer by night 🎮",
    "Nairobi born. Code written. Dreams chased. 🇰🇪",
    "Jua kali developer. Solving shida moja baada ya nyingine.",
    "Msee wa code na chapati. Eastlands represent 💪",
    "Digital nomad | Safari lover | Python enthusiast 🐍",
    "Mama, developer, entrepreneur. Nairobi to the world 🌍",
    "Food blogger based in Westlands. Eating my way through Nairobi 🍽️",
    "Afrobeats fan. Tech bro. Trying to make it in this economy 😅",
    "Street photographer. Capturing Nairobi one frame at a time 📸",
    "Fitness coach | Personal trainer | CBD gym 💪",
    "Cloud architect | AWS & GCP | Kubernetes lover",
    "Security researcher. Ethical hacker. Cat person 🐱.",
    "Making data make sense. One dashboard at a time.",
    "Rust evangelist. Open to work 🚀",
    "Backend dev who accidentally learned CSS.",
    "DevRel @ startup. Speaker. Recovering perfectionist.",
    "Writing code and occasionally coherent sentences.",
    "Distributed systems nerd. Previously @BigTech.",
]

LOCATIONS = [
    "Nairobi, Kenya 🇰🇪", "Eastlands, Nairobi", "Westlands, Nairobi",
    "Mombasa, Kenya", "Kisumu, Kenya", "Nakuru, Kenya", "Thika, Kenya",
    "Kampala, Uganda", "Dar es Salaam, Tanzania", "Kigali, Rwanda",
    "Lagos, Nigeria", "Accra, Ghana", "Johannesburg, SA",
    "San Francisco, CA", "Berlin, Germany", "London, UK",
    "Remote 🌍", "Somewhere on Thika Road 🚗", "CBD, Nairobi",
]

# ─── TWEET POOLS ──────────────────────────────────────────────────────────────

TWEETS_TECH_ENGLISH = [
    "Just shipped a feature I've been working on for 3 weeks. Sleep deprived but happy 🚀",
    "Hot take: code reviews are the most underrated part of engineering culture.",
    "The best documentation is code that doesn't need any.",
    "Spent 2 hours debugging. The bug was a missing semicolon. I'm fine. 🙃",
    "Unpopular opinion: monoliths are underrated. Fight me.",
    "Just discovered a 5-year-old TODO comment in production. Not mine. Not touching it.",
    "The real 10x engineer is the friends we made along the way.",
    "Why do we call it a 'build pipeline' if it barely builds and rarely pipelines?",
    "Started learning Rust. My brain has left the chat.",
    "Reminder: done is better than perfect. Ship it. Iterate. Repeat.",
    "If your API returns a 200 with an error message, we can't be friends.",
    "Dark mode isn't a preference, it's a lifestyle.",
    "My git history is basically a journal of my mental state during each sprint.",
    "I love open source. I hate maintaining open source. Complicated relationship.",
    "Tech debt is just a loan against your future self's happiness.",
    "Finally wrote tests for legacy code. Green across the board. Something is wrong.",
    "Senior dev energy: immediately searching for a library that does this already.",
    "There's no such thing as a temporary hack in production. It lives forever.",
    "Friday afternoon deploys are an extreme sport and I am an athlete.",
    "Reading other people's code is a humbling and educational experience. Mostly humbling.",
    "New blog post: Why I switched from X to Y and back to X — link in bio",
    "Anyone else feel like their imposter syndrome has imposter syndrome?",
    "If you're not breaking things in staging, you're not trying hard enough.",
    "GraphQL is great until you need to explain it to a new hire on a Friday afternoon.",
    "The cloud is just someone else's computer. A very expensive, very reliable one.",
    "Naming things is hard. Caching is hard. Off-by-one errors are embarrassing.",
    "Just automated a task that took 30 mins/day. Took 3 days to automate. Worth it.",
    "My favourite design pattern is delete the code that causes the problem.",
    "Every microservice you add is a new way to wake up at 3am.",
    "There are two hard problems in CS: cache invalidation, naming things, and off-by-one errors.",
]

TWEETS_TECH_KISWAHILI = [
    "Nimekamilisha feature mpya leo! Wiki tatu za kazi. Nimechoka lakini furaha ni kubwa 🚀",
    "Maoni yangu: code review ndiyo sehemu muhimu zaidi ya engineering. Watu hawajui.",
    "Nimetumia masaa mawili kutafuta hitilafu. Ilikuwa semicolon moja tu. Sawa tu. 😅",
    "Kama API yako inarudisha 200 lakini na ujumbe wa hitilafu, hatuwezi kuwa marafiki.",
    "Dark mode si chaguo tu — ni mtindo wa maisha.",
    "Historia yangu ya git ni jarida la hali yangu ya akili kila sprint.",
    "Napenda open source. Nachukia kudumisha open source. Uhusiano mgumu.",
    "Deni la kiufundi ni mkopo unaochukua dhidi ya furaha ya wewe wa baadaye.",
    "Mwishowe niliandika majaribio kwa ajili ya code ya zamani. Kila kitu kijani. Kuna tatizo.",
    "Mkakati wangu mpendwa wa kubuni: futa code inayosababisha tatizo.",
    "Kuna matatizo mawili magumu katika CS: kutaja vitu, na kuhifadhi data kwenye cache.",
    "Kila microservice unayoongeza ni njia mpya ya kuamshwa saa tisa usiku.",
    "Usambazaji wa Ijumaa mchana ni michezo hatari na mimi ni mwanariadha.",
    "Kusoma code ya watu wengine ni uzoefu wa kujifunza na wa kunyenyekea. Zaidi kunyenyekea.",
    "Kumbuka: kukamilika ni bora kuliko ukamilifu. Tuma, rekebisha, rudia.",
    "Nimeanza kujifunza Rust. Ubongo wangu umeenda likizoni.",
    "Nimegundua maoni ya TODO yenye miaka mitano kwenye production. Si yangu. Sitayagusa.",
    "Kwa nini tunaiita build pipeline kama haijengi vizuri na si pipeline halisi?",
    "Docs bora ni code ambayo haihitaji maelezo yoyote.",
    "Mfumo wa wingu ni kompyuta ya mtu mwingine. Ghali sana, lakini ya kuaminika.",
]

TWEETS_TECH_SHENG = [
    "Nimefika na feature mpya bana! Wiki tatu za hustle, sasa naeza kulala 😴🚀",
    "Si uwongo, code review ndiyo kitu muhimu sana kwa team. Watu hawajua hata.",
    "Nilitumia masaa mawili kudebug. Bug ilikuwa semicolon moja tu. Buda. 😂",
    "Kama API yako inareturn 200 na error message, wewe na mimi hatuwezi kuwa poa.",
    "Dark mode ni lifestyle bana, si option tu. Usiniambie chochote.",
    "Git history yangu ni kama diary ya maisha yangu kila sprint. Emotional sana.",
    "Napenda open source. Lakini kudumisha? Buda, ni stress kubwa sana. 😩",
    "Tech debt ni kama kulipa loan — future self yako ndiyo atalipa bei.",
    "Ukifika senior dev level, unatafuta library tayari. Hiyo ndiyo 10x energy.",
    "Usambazaji saa kumi Ijumaa? Bana hiyo ni extreme sport. Mimi ni athlete wa kweli. 🏆",
    "Nimeanza Rust. Ubongo wangu umekimbia. Umerudi lini? Sijui bana.",
    "Kuna TODO ya miaka tano kwa production. Si yangu. Sitaigusa. Hata kidogo.",
    "Kila microservice mpya ni njia nyingine ya kuamshwa usiku wa manane. Sawa tu.",
    "Kusoma code ya watu wengine — inakufundisha na inakuazesha. Zaidi kuazesha.",
    "Ukifika kufanya tests kwa legacy code, kila kitu kilikuwa green. Sawa, kuna shida.",
    "Favourite design pattern yangu: futa code inayosababisha shida. Simple kama hiyo.",
    "Shida mbili ngumu za CS: kutaja vitu vizuri, na cache invalidation. Na off-by-one ya aibu.",
    "Nimekuwa nafanya kazi kwa wiki tatu bila lunch break. Ni dedication au kujidanganya? 🤔",
    "Docs bora ni code ambayo haihitaji maelezo. Hii ni ukweli wa maisha bana.",
    "Ninafanya kazi usiku wote. Kesho asubuhi deployment. Mungu atusaidie. 🙏",
]

TWEETS_LIFESTYLE_ENGLISH = [
    "Nairobi traffic on a Monday morning is a spiritual experience. An awful one. 😩",
    "Matatu conductors are the original UX designers. They'll fit 20 people in a 14-seater.",
    "Nyama choma plus cold Tusker on a Friday evening. That's the Kenyan dream. 🍖🍺",
    "Sunrise from the Ngong Hills hits different. Nairobi is something else at dawn. 🌅",
    "If you've never argued over the bill at a Nairobi restaurant, are you even Kenyan?",
    "Chapati and beans is the most underrated meal in East Africa. Change my mind.",
    "Nairobi weather reminder: morning jacket, afternoon t-shirt, evening jacket again. Always.",
    "The economy is rough but Nairobians will still find money for the weekend. Resilience.",
    "Westlands on a Saturday night vs Eastlands on a Saturday night — two different Nairobis.",
    "Kenyan parents: Doctor or lawyer? Meanwhile their kid is building startups. 😂",
    "The number of talented Kenyans working for pennies because opportunities aren't equal is wild.",
    "M-Pesa changed everything. Imagine sending rent money in 30 seconds. Africa's gift to the world.",
    "Nairobi is loud, chaotic, beautiful, exhausting, and electric. I wouldn't trade it.",
    "Ugali is not just food. It's culture, it's family, it's home.",
    "Nothing builds character like navigating CBD on a Friday afternoon on foot.",
    "Kenyan humour is unmatched globally. We find a way to laugh at literally everything. 😂",
    "Just had the best pilau of my life at a random kibanda in Eastleigh. Nairobi never disappoints.",
    "The hustle culture here is real. Everyone is working on something on the side.",
    "Wildlife, beaches, mountains, savannah — Kenya has more variety than most continents.",
    "Our music scene is exploding. Afrobeats, gengetone, drill — Nairobi is a vibe factory.",
]

TWEETS_LIFESTYLE_KISWAHILI = [
    "Msongamano wa Nairobi Jumatatu asubuhi ni uzoefu wa kiroho. Mbaya kabisa. 😩",
    "Wakondakta wa matatu ni wabunifu wa kwanza wa UX. Wataingiza watu 20 kwenye gari la 14.",
    "Nyama choma na Tusker baridi Ijumaa jioni. Hiyo ndiyo ndoto ya Mkenya. 🍖🍺",
    "Machweo ya jua kutoka Milima ya Ngong yana ladha tofauti. Nairobi ni kitu kingine kabisa alfajiri. 🌅",
    "Kama hujawahi bishana kuhusu bili kwenye mgahawa wa Nairobi, je, wewe ni Mkenya kweli?",
    "Chapati na maharagwe ni chakula chenye thamani kubwa ambacho hakipewi heshima. Nisemee tofauti.",
    "Hali ya hewa Nairobi: koti asubuhi, fulaha mchana, koti tena jioni. Kila wakati.",
    "Uchumi ni mgumu lakini Wanairobi bado wataona pesa ya wikendi. Ni nguvu ya moyo.",
    "Westlands Jumamosi usiku dhidi ya Eastlands Jumamosi usiku — Nairobi mbili tofauti kabisa.",
    "Wazazi wa Kenya: Daktari au wakili? Huku mtoto wao anajenga startup. 😂",
    "M-Pesa imebadilisha kila kitu. Fikiria kutuma kodi kwa sekunde 30. Zawadi ya Afrika kwa dunia.",
    "Nairobi ni kelele, msongo, nzuri, ya kuchoshea, na yenye nguvu. Sitaibadilisha.",
    "Ugali si chakula tu. Ni utamaduni, ni familia, ni nyumba.",
    "Muziki wetu unakua kwa kasi. Afrobeats, gengetone, drill — Nairobi ni kiwanda cha maono.",
    "Wanyamapori, pwani, milima, savana — Kenya ina aina nyingi zaidi ya mabara mengi.",
    "Mzaha wa Wakenya hauna kifani duniani. Tunacheka kila kitu bila ya kusita. 😂",
    "Nilikuwa na pilau nzuri zaidi maishani mwangu kwenye kibanda kidogo Eastleigh. Nairobi haioni aibu.",
    "Utamaduni wa kufanya kazi kwa bidii hapa ni wa kweli. Kila mtu ana mradi wake.",
    "Hakuna kinachoimarisha tabia kama kupita CBD Ijumaa jioni kwa miguu.",
    "Idadi ya Wakenya wenye vipaji wanaofanya kazi kwa mishahara midogo ni tatizo kubwa la nchi yetu.",
]

TWEETS_LIFESTYLE_SHENG = [
    "Traffic ya Nairobi Jumatatu asubuhi ni kama adhabu ya Mungu. Buda. 😩",
    "Kondakta wa matatu ndio original UX designer. Anaweza piga watu 20 kwa gari la 14. Talent.",
    "Nyama choma na Tusker baridi Ijumaa jioni. Hiyo ndiyo maisha bana. 🍖🍺",
    "Machweo ya jua kutoka Ngong Hills ni different swear. Nairobi mapema asubuhi ni moto. 🌅",
    "Kama hujawahi fight kuhusu bill kwa restaurant, je wewe ni mtu wa Nbi kweli? 😂",
    "Chapati na beans ni underrated sana dunia hii. Niseme tena. Underrated sana.",
    "Weather ya Nbi: koti asubuhi, fulaha mchana, koti tena usiku. Daily routine bana.",
    "Uchumi uko ngumu but Nairobians watapata pesa ya weekend. Hiyo ni resilience ya kweli.",
    "Westlands usiku wa Jumamosi dhidi ya Eastlands usiku wa Jumamosi — Nairobi mbili tofauti. 🌃",
    "Wazazi Kenya: Daktari au wakili? Huku mwanao anajenga app. Hawajui bana. 😂",
    "M-Pesa imefanya kila kitu rahisi. Kutuma rent kwa sekunde 30? Africa ilifanya hiyo.",
    "Nairobi ni loud, chaotic, nzuri, tiring, na electric. Sitaenda mahali pengine.",
    "Ugali si chakula tu — ni utamaduni, ni family, ni home. Usiniambie tena.",
    "Muziki wa Nbi unakua sana. Gengetone, afrobeats, drill — hii city ni vibe factory. 🎵",
    "Kibanda moja Eastleigh — pilau ilikuwa best ya maisha. Nairobi haikudanganya.",
    "Kila mtu ana side hustle hapa. Kila mtu. Hata mkubwa wa ofisi ana kitu chake.",
    "Nai ni msongamano, ni stress, ni beauty, ni exhaustion, ni magic. Naipenda sana. 🫶",
    "Wakenya wenye talent wanafanya kazi kwa pesa kidogo kwa sababu opportunities si equal. Ukweli mzito.",
    "Kufanya kazi kwa bidii ni nzuri lakini bana, rest ni muhimu pia. Balance. Always balance.",
    "Naweza kukimbia CBD Ijumaa mchana kwa miguu bila kutoka pumzi. Hiyo ndiyo mazoezi yangu. 💪",
]

TWEETS_FOOD_SHENG = [
    "Kuku wa kukaanga + ugali + sukuma wiki = Paradise. Mtu yeyote anasema nini? 🍗",
    "Kibanda cha mama pale Gikomba — maharagwe na chapati ni best. Hata nyumbani haifiki.",
    "Nilikula pilau ya mwisho jana. Buda ilikuwa moto wa kweli. 🔥🔥 Nairobi food scene ni fire.",
    "Mutura ni acquired taste lakini once unaipata, huwezi kurudi nyuma. Trust me bana.",
    "Nyama choma usiku wa manane na marafiki — hiyo ndiyo self-care ya kweli. 😂",
    "Ugali na samaki wa kukaanga Kisumu — experience tofauti kabisa. Usiambiwe na mtu.",
    "Mandazi na chai asubuhi ni combo bora duniani. Sitaki kusikia argument nyingine.",
    "Biryani ya Mombasa vs biryani ya Eastleigh — ni debate ya milele. Mimi? Mombasa inashinda.",
    "Kachumbari inafanya kila kitu kuwa bora. Ni science bana, si maoni yangu.",
    "Watu wanaosema hawapendi ugali — mimi sielewi lifestyle yao. Kabisa.",
    "Supu ya ngozi na chapo tatu — breakfast ya malkia. Mtu anajua kibanda pazuri CBD? 🙏",
    "Mchele wa kuchemsha + mchuzi wa nyama + saladi. Hiyo ndiyo lunch ya billionaire bila pesa. 😂",
    "Mtura ya Githurai ni different level bana. Hata ulitoka Westlands, inabidi ufike.",
    "Chai ya tangawizi asubuhi baridi ya Nairobi — hiyo ndiyo therapy ya bei nafuu.",
    "Nikisema napenda pilau ya Eastleigh, si loyalty — ni truth. Ulinisikia vizuri.",
]

TWEETS_FOOD_KISWAHILI = [
    "Kuku wa kukaanga, ugali, na sukuma wiki ni mlo bora duniani. 🍗",
    "Kibanda cha mama pale Gikomba — maharagwe na chapati ni bora zaidi. Hata nyumbani haifikii.",
    "Nilipata pilau nzuri sana jana. Nairobi haikuangusha. 🔥",
    "Mutura ni ladha inayohitaji muda wa kuzoea lakini ukiipata, hutarudi nyuma.",
    "Nyama choma usiku wa manane na marafiki — hiyo ndiyo kujitunza kwa kweli. 😂",
    "Ugali na samaki wa kukaanga Kisumu ni uzoefu tofauti kabisa. Lazima ujaribu.",
    "Mandazi na chai asubuhi ni mchanganyiko bora zaidi duniani. Sina ubishi.",
    "Biryani ya Mombasa dhidi ya biryani ya Eastleigh — mdahalo wa milele. Mombasa inashinda.",
    "Kachumbari inaboresha kila chakula. Hiyo ni sayansi, si maoni tu.",
    "Watu wanaosema hawapendi ugali — sijui wanaishi maisha gani. Kabisa.",
    "Supu ya ngozi na mkate wa chapati — kifungua kinywa cha malkia. Mtu anajua kibanda pazuri CBD?",
    "Chai ya tangawizi asubuhi baridi ya Nairobi — hiyo ndiyo tiba ya bei nafuu. ☕",
    "Mlo wa ugali na mchuzi wa maharage ni utajiri wa kweli. Hauhitaji mkahawa wa bei ghali.",
    "Pilau ya Eastleigh ni bora zaidi kuliko mahali popote Nairobi. Hii si maoni, ni ukweli.",
    "Mutura ya Githurai ina harufu ya ushindi. Ukifika, utaelewa maana ya maisha.",
]

TWEETS_HUSTLE_SHENG = [
    "Kuamka saa kumi na mbili usiku kukamilisha project. Hiyo ndiyo entrepreneur life bana. 💪",
    "Client alikupatia pesa baada ya miezi miwili ya kusubiri. Mwisho. Lazima ulipe wakati wako. 😤",
    "Freelancing si rahisi bana. Lakini nobody anakuambia overtime haikusanidi. Freedom ni bora.",
    "Nimezungumza na investors watano wiki hii. Wawili walipenda idea. Hiyo ni progress. 🚀",
    "Siku mbaya za biashara zipo. Inabidi uendelee tu. Kesho ni siku mpya.",
    "Akili yangu inafanya kazi kwa 200% wakati ninajua bili ya mwezi inakuja. 😅",
    "Networking event jana — nilipata contacts tano muhimu. Hiyo ndiyo value ya kweli.",
    "Watu wananiuliza siri ya success. Buda, siri ni persistence tu. Kuendelea hata ukiumia.",
    "Nimekosa chakula cha mchana wiki nzima nikifanya kazi. Lakini order imefika. God is good. 🙏",
    "Startup life: asubuhi una confidence, jioni una doubts, usiku unafanya kazi tu. Cycle.",
    "Nikiwa na pesa kidogo, maumivu mengi. Nikiwa na pesa nyingi, problems nyingine. Life tu.",
    "Watu wanaoniuliza kwa nini siendi office job. Bana, freedom yangu haiuzwi. Simple.",
    "Invoice ilipata viewed — sasa nasubiri payment. Hii sehemu ya biashara ni ngumu sana. 😩",
    "Ukitaka kuanza biashara, anzisha tu. Perfection inakuja baadaye. Just start.",
    "Saa ngapi za siku unafanya kazi? Na ngapi za scroll aimlessly? Swali la kweli. 🤔",
]

TWEETS_HUSTLE_KISWAHILI = [
    "Kuamka saa kumi na mbili usiku kukamilisha mradi. Hii ndiyo maisha ya mjasiriamali. 💪",
    "Mteja alinipa pesa baada ya miezi miwili ya kusubiri. Lazima ulipwe wakati wako. 😤",
    "Kufanya kazi kwa uhuru si rahisi. Lakini hakuna anayekuambia muda wa ziada haukusanidi. Uhuru ni bora.",
    "Nimezungumza na wawekezaji watano wiki hii. Wawili walipenda wazo langu. Maendeleo. 🚀",
    "Siku mbaya za biashara zipo. Inabidi uendelee tu. Kesho ni siku mpya.",
    "Akili yangu inafanya kazi kwa nguvu zaidi ninaporejea kumbuka bili za mwezi. 😅",
    "Tukio la uunganisho la jana — nilipata anwani tano muhimu. Hiyo ndiyo thamani ya kweli.",
    "Watu wananiuliza siri ya mafanikio. Siri ni uvumilivu tu. Kuendelea hata ukiuma.",
    "Nimekosa chakula cha mchana wiki nzima nikifanya kazi. Lakini agizo limefika. Mungu ni mkuu. 🙏",
    "Maisha ya startup: asubuhi una ujasiri, jioni una mashaka, usiku unafanya kazi tu. Mzunguko huu.",
    "Ukitaka kuanzisha biashara, anzisha tu. Ukamilifu unakuja baadaye. Anza kwanza.",
    "Ankara ilipata kutazamwa — sasa nasubiri malipo. Sehemu hii ya biashara ni ngumu. 😩",
    "Nikiwa na pesa kidogo, maumivu mengi. Nikiwa na pesa nyingi, shida nyingine. Maisha haya.",
    "Watu wananiuliza kwa nini siendi kazi ya ofisi. Uhuru wangu hauuzwi. Rahisi.",
    "Saa ngapi za siku unafanya kazi? Na ngapi unazotumia kushuka bila kusudi? Swali zito.",
]

TWEETS_MOTIVATIONAL_SHENG = [
    "Hakuna mtu atakaekuja kukuokoa. Jiokoe mwenyewe. Simama na ufanye kazi. 💪",
    "Watu waliokataa dreams zako ni ushahidi tu kwamba uko njia sahihi. Keep going bana.",
    "Pressure inafanya almasi. Kama una pressure saa hii, jua unaundwa kuwa kitu kikubwa. ✨",
    "Usilinganishe chapter yako ya kwanza na chapter ya mtu mwingine ya ishirini. Patience bana.",
    "Kushindwa si mwisho. Ni feedback tu. Jifunza na uendelee. That's all.",
    "Watu wangu wote wanaofanya kazi kwa bidii bila kutambuliwa — mnaonwa. Keep pushing. 🙏",
    "Ndoto kubwa inahitaji kazi kubwa. Hakuna shortcut. Hata mtu anayeonekana lucky alifanya kazi.",
    "Jiambie ukweli: umefanya nini leo kuelekea goals zako? Honest check-in tu.",
    "Mafanikio yako yatafanya watu wengine believe katika dreams zao. Thamani yako ni kubwa.",
    "Saa ngapi za siku unafanya kazi? Na ngapi za scroll aimlessly? Swali la kweli. 🤔",
    "Rest si uzembe bana. Rest ni investment katika productivity ya kesho. Lala.",
    "Kuamka mapema si faida yenyewe — ni unafanyafanya nini ukiamka mapema ndio kinachohusika.",
    "Ukitaka kubadilisha maisha yako, lazima ubadilishe mazingira yako kwanza. Surround yourself na bora.",
    "Siku ngapi umesema kesho nitaanza? Anza leo. Hata hatua moja ndogo. Just start.",
    "Marafiki wanaokubeba juu — hiyo ndiyo wealth ya kweli. Pesa inakuja na kwenda.",
]

TWEETS_MOTIVATIONAL_KISWAHILI = [
    "Hakuna mtu atakayekuja kukuokoa. Jiokoe mwenyewe. Simama na ufanye kazi. 💪",
    "Watu waliokataa ndoto zako ni ushahidi tu kwamba uko njia sahihi. Endelea.",
    "Shinikizo linatengeneza almasi. Kama una shinikizo sasa, ujue unatengenezwa kuwa kitu kikubwa. ✨",
    "Usilinganishe sura yako ya kwanza na sura ya ishirini ya mtu mwingine. Subiri.",
    "Kushindwa si mwisho. Ni maoni tu. Jifunza na uendelee. Hiyo tu.",
    "Ndoto kubwa inahitaji kazi kubwa. Hakuna mkato. Hata mtu anayeonekana na bahati alifanya kazi.",
    "Jiambie ukweli: umefanya nini leo kuelekea malengo yako? Ukaguzi wa uaminifu tu.",
    "Mafanikio yako yatafanya watu wengine waamini katika ndoto zao. Thamani yako ni kubwa.",
    "Saa ngapi za siku unafanya kazi? Na ngapi unazotumia kushuka bila kusudi? Swali zito. 🤔",
    "Watu wangu wote wanaofanya kazi kwa bidii bila kutambuliwa — mnaonwa. Endeleeni. 🙏",
    "Pumzika si uvivu. Pumzika ni uwekezaji katika tija ya kesho. Lala vizuri.",
    "Kuamka mapema si kitu — ni unafanyafanya nini ukiamka mapema ndicho kinachohusika.",
    "Ukitaka kubadilisha maisha yako, lazima ubadilishe mazingira yako kwanza.",
    "Siku ngapi umesema kesho nitaanza? Anza leo. Hata hatua moja ndogo. Anza tu.",
    "Marafiki wanaokukweza — hiyo ndiyo utajiri wa kweli. Pesa inakuja na kwenda.",
]

TWEETS_ROMANCE_SHENG = [
    "Alikuwa ananitazama kama mimi ni kitu pekee kinachohusika. Nikiambia — heart ilienda. 😭❤️",
    "Kuhubiwa na mtu anayekupenda kwa kweli ni feeling tofauti kabisa. Hata story ya maisha inabadilika.",
    "Nikiwa na mtu wangu, hata traffic ya Nairobi inaonekana romantic. Mapenzi yana nguvu bana.",
    "Watu wangu wanaofanya long-distance — how do you manage? Asking for a friend. 😅",
    "Red flag: anakuambia nisikie lakini haheshimu muda wako. Run bana. Run.",
    "Love bombing inaonekana vizuri mwanzo — unapata messages zote, attention yote. Lakini baadaye? Ouch.",
    "Kukaa kimya pamoja bila awkwardness ni level ya relationship ambayo haifiki haraka.",
    "Mtu anakupenda kweli? Atakuonyesha kwa matendo. Words ni rahisi sana kuzungumza.",
    "Heartbreak ya kwanza inakufundisha zaidi kuliko darasa lolote. Ni expensive lakini ni lesson ya kweli.",
    "Best feeling: kumpigia mtu simu na anashangilia sauti yako. Hiyo ndiyo connection ya kweli. ❤️",
    "Kudate Nairobi ni adventure yake yenyewe. Unakutana wapi? CBD ni noisy, mall ni pricey. 😂",
    "Mtu anakupenda kweli akikupigia simu saa nne usiku — si drama, ni concern. Tofauti ni muhimu.",
    "Toxic relationship ni kama mtandao wa polepole — unajua ni mbaya lakini unaendelea kutumia. 😩",
    "Ukitaka kujua mtu ni wa kweli, angalia anaakujali vipi ukiwa chini. Wakati wa juu wote wanakaa.",
    "Mtu wako akikusupporti dreams zako ndio yule. Usimwache. Ni rare sana.",
]

TWEETS_ROMANCE_KISWAHILI = [
    "Aliniangalia kama mimi ndiye kitu pekee kinachohusika. Moyo wangu ulikimbia. 😭❤️",
    "Kupendwa na mtu anayekupenda kweli ni hisia tofauti kabisa. Hata hadithi ya maisha inabadilika.",
    "Nikiwa pamoja naye, hata msongamano wa Nairobi unaonekana wa kimapenzi. Mapenzi yana nguvu.",
    "Watu wanaofanya upendo wa umbali — mnawezaje? Ninauliza kwa ajili ya rafiki. 😅",
    "Dalili nyekundu: anakuambia nisikie lakini haheshimu wakati wako. Kimbia.",
    "Kukaa kimya pamoja bila wasiwasi ni kiwango cha uhusiano ambacho hakifiki haraka.",
    "Mtu akikupenda kweli? Ataonyesha kwa matendo. Maneno ni rahisi sana kusema.",
    "Maumivu ya moyo wa kwanza yanakufundisha zaidi kuliko darasa lolote. Ghali lakini ni somo la kweli.",
    "Hisia bora: kumpigia mtu simu na anafurahi kusikia sauti yako. Hiyo ndiyo uhusiano wa kweli. ❤️",
    "Uhusiano wa sumu ni kama mtandao wa polepole — unajua ni mbaya lakini unaendelea kutumia. 😩",
    "Ukitaka kujua mtu ni wa kweli, angalia anakujali vipi ukiwa chini. Wakati wa juu wote wanakaa.",
    "Mpenzi wako akisupporti ndoto zako — hiyo ndiyo mtu wa kweli. Usimwache. Ni nadra sana.",
    "Kudate Nairobi ni safari yake yenyewe. Unakutana wapi? CBD ni na kelele, mall ni ghali. 😂",
    "Mtu anakupenda kweli akikupigia simu usiku — si tatizo, ni wasiwasi. Tofauti ni muhimu.",
    "Upendo wa kweli si hisia tu — ni chaguo unalofanya kila siku. Kila siku unaamua kubaki.",
]

TWEETS_SPORTS_SHENG = [
    "Arsenal imecheza vibaya tena. Bana sijui naweza kuendelea kuisupport team hii. 😩⚽",
    "Gor Mahia iliochoa Leopards — stadium ilikuwa moto! Hii ndiyo football ya kweli. 🟢⚫",
    "Harambee Stars lazima wapate coach bora. Talents zipo Kenya but system iko broken.",
    "Kipchoge ameshinda tena! Mkenya wa kweli. Pride ya nation. 🏃‍♂️🇰🇪",
    "NBA finals saa hizi — ni kati ya drama na talent. Mimi? Natazama tu bila kusupport mtu.",
    "Mtu wangu anasema Chelsea itashinda EPL. Niambie jinsi ya kumsaidia. 😂",
    "Kenya sevens team ni pride ya nation. Wanafanya kazi bila resources nyingi. Salute. 🏉",
    "Boxing ya usiku wa jana ilikuwa fire. Mtu yeyote alitazama? KO round ya tatu — bana!",
    "Ukiwa supporter wa Tottenham, unastahili vacation. Watu hao wanateseka. 😂",
    "Kenya marathon runners ni wa kutisha. Tunashinda dunia bila hata kujua tuna nguvu kiasi gani.",
    "Gor Mahia vs AFC Leopards Derby ni mchezo wa moyo. Hata watu wasiopenda soka wanafuatilia.",
    "Kama unatazama match bila kula nyama choma, unafanya kosa kubwa sana. Hakika. 🍖⚽",
    "Tuambie sports betting imebeba au imechukua pesa yako leo. Honest answers only. 😂",
    "Kenyans tunaweza run marathon lakini hatuwezi uendesha timu ya soka. Paradox ya kweli.",
    "Kuona Kipchoge akifika finish line — hiyo ni proof kwamba binadamu ana nguvu isiyo na mipaka. 🏆",
]

TWEETS_SPORTS_KISWAHILI = [
    "Arsenal imecheza vibaya tena. Sijui ninaweza kuendelea kuisupport timu hii. 😩⚽",
    "Gor Mahia imechomea AFC Leopards — uwanja ulikuwa wa moto! Hii ndiyo soka ya kweli. 🟢⚫",
    "Harambee Stars lazima wapate kocha bora. Vipaji vipo Kenya lakini mfumo umevunjika.",
    "Kipchoge ameshinda tena! Mkenya wa kweli. Fahari ya taifa. 🏃‍♂️🇰🇪",
    "Kenya sevens team ni fahari ya taifa. Wanafanya kazi bila rasilimali nyingi. Heshima. 🏉",
    "Mchezo wa ngumi wa usiku wa jana ulikuwa mzuri. KO raundi ya tatu — ya kushangaza!",
    "Wakimbiaji wa marathon wa Kenya wana nguvu ya kutisha. Tunashinda dunia bila hata kujua.",
    "Ukiwa mshabiki wa Tottenham, unastahili likizo. Watu hao wanateseka. 😂",
    "NBA finals sasa hivi — ni mchezo kati ya drama na ujuzi. Ninatazama tu.",
    "Timu yetu ya soka lazima iwekeze katika vijana. Ndio mustakabali wa mchezo wetu.",
    "Derby ya Gor Mahia na AFC Leopards ni mchezo wa moyo. Hata wasiopenda soka wanafuatilia.",
    "Kutazama mechi bila kula nyama choma ni kosa kubwa. Hakika kabisa. 🍖⚽",
    "Kuona Kipchoge akifika mstari wa mwisho — ni ushahidi kwamba binadamu ana nguvu isiyo na mipaka.",
    "Wakenya tunaweza kukimbia marathon lakini hatuwezi kuendesha timu ya soka. Paradox ya kweli.",
    "Natumai Kenya itaingia Kombe la Dunia siku moja. Ndoto inawezekana kama tukifanya kazi.",
]

TWEETS_GENERAL_SHENG = [
    "Serikali ikiomba raia wafanye X, lakini wao wenyewe wanafanya Y. Classic. 😤",
    "Nairobi imebadilika sana. Miaka kumi ijayo itaonekana different kabisa. Interesting times.",
    "Uchumi wa Kenya uko na potential kubwa. Kama tu watu wa juu wangeacha kuiba. Sad.",
    "Kama umewahi kulipa kodi kwa wakati na landlord hanaweza kufix chochote — karibu Kenya. 😂",
    "Watoto wa siku hizi ni wasomi zaidi ya generation yoyote. Mzigo lazima uwe heavy sana.",
    "Naomba tu power isirudi saa nne usiku. Ninafanya kazi. Saa nne usiku pia. 🙏",
    "Mpango wa maisha: kazi, kulala, kuamka, kulalamika kuhusu traffic, kazi tena. Repeat.",
    "Watu wanaolalamika kuhusu kila kitu lakini hawafanyi chochote — hiyo ni frustrating sana.",
    "Wakati wa recession, Nairobians bado wanaenda out. Hiyo ndiyo optimism ya kweli. 😂",
    "Ndoa si destination — ni journey ya kila siku. Kila siku unaamua kubaki. Think about it.",
    "Mtoto wa Nairobi akiambia niko sawa — hiyo inaweza maanisha kitu chochote. Be careful.",
    "Hizi social media apps zinatumia data nyingi sana. Lakini bado tunazitumia. Logic? Zero.",
    "Rais mpya, matatizo yale yale. Nairobi inaendelea. Watu wanaendelea. Life goes on.",
    "Sisi Nairobians tunaweza cheka kitu chochote. Hata mambo magumu — tunayafanya meme. Therapy yetu.",
    "KPLC ikikata stima bila notice — bana hiyo ni cyber attack ya serikali dhidi ya wananchi. 😂",
    "Nbi rent inakua ghali kila mwaka. Watu wa middle class wanakimbia outskirts. Story ya dunia.",
    "Unapopewa change kwa duka na unaambiwa nikuletee kidogo — hawaleti. Hiyo ni theft halali. 😩",
    "Una majukumu ya adult lakini budget ya teenager. Welcome to Kenya economy bana. 😭",
    "Si watoto wote wa rich wanafanikiwa, wala watoto wa maskini wote hawafanikiwa. Effort + luck = life.",
    "Nairobi baridi ya Julai ikiua polepole — na watu wanasema Kenya si na majira. 🥶",
]

TWEETS_GENERAL_KISWAHILI = [
    "Serikali inaomba raia wafanye X, lakini wao wenyewe wanafanya Y. Classic. 😤",
    "Nairobi imebadilika sana. Miaka kumi ijayo itaonekana tofauti kabisa. Nyakati za kuvutia.",
    "Uchumi wa Kenya una uwezo mkubwa. Kama tu viongozi wangeacha kuiba. Huzuni.",
    "Kama umewahi kulipa kodi kwa wakati lakini landlord hawezi kurekebisha chochote — karibu Kenya. 😂",
    "Watoto wa leo ni wasomi zaidi ya kizazi chochote. Mzigo lazima uwe mzito sana.",
    "Naomba tu umeme usifuke saa kumi usiku. Ninafanya kazi. Saa kumi usiku pia. 🙏",
    "Mpango wa maisha: kazi, kulala, kuamka, kulalamika kuhusu msongamano, kazi tena. Rudia.",
    "Wakati wa msongo wa kiuchumi, Wanairobi bado wanaenda nje. Hiyo ndiyo matumaini ya kweli. 😂",
    "Ndoa si mwisho wa safari — ni safari yenyewe ya kila siku. Kila siku unaamua kubaki.",
    "Mitandao ya kijamii inatumia data nyingi sana. Lakini bado tunaitumia. Mantiki? Hakuna.",
    "Rais mpya, matatizo yale yale. Nairobi inaendelea. Watu wanaendelea. Maisha yanaendelea.",
    "Sisi Wanairobi tunaweza kucheka kitu chochote. Hata mambo magumu — tunayafanya meme. Tiba yetu.",
    "Kodi ya nyumba inakua ghali kila mwaka. Watu wa darasa la kati wanakimbia maeneo ya nje. Hadithi ya ulimwengu.",
    "Una majukumu ya mtu mzima lakini bajeti ya kijana. Karibu Kenya ya leo. 😭",
    "Si watoto wote wa matajiri wanafaulu, wala watoto wote wa maskini hawafaulu. Juhudi pamoja na bahati.",
]

# ── Combine ALL tweet pools ────────────────────────────────────────────────────
ALL_TWEETS = (
    TWEETS_TECH_ENGLISH
    + TWEETS_TECH_KISWAHILI
    + TWEETS_TECH_SHENG
    + TWEETS_LIFESTYLE_ENGLISH
    + TWEETS_LIFESTYLE_KISWAHILI
    + TWEETS_LIFESTYLE_SHENG
    + TWEETS_FOOD_SHENG
    + TWEETS_FOOD_KISWAHILI
    + TWEETS_HUSTLE_SHENG
    + TWEETS_HUSTLE_KISWAHILI
    + TWEETS_MOTIVATIONAL_SHENG
    + TWEETS_MOTIVATIONAL_KISWAHILI
    + TWEETS_ROMANCE_SHENG
    + TWEETS_ROMANCE_KISWAHILI
    + TWEETS_SPORTS_SHENG
    + TWEETS_SPORTS_KISWAHILI
    + TWEETS_GENERAL_SHENG
    + TWEETS_GENERAL_KISWAHILI
)

HASHTAG_NAMES = [
    # Tech
    "buildinpublic", "100daysofcode", "opensource", "webdev", "devlife",
    "javascript", "python", "rust", "golang", "typescript",
    "machinelearning", "cloudnative", "kubernetes", "devops", "uxdesign",
    "startup", "indiehacker", "coding", "tech", "softwareengineering",
    # Kenyan / Swahili
    "nairobi", "kenya", "nairobidiaries", "kenyantwitter", "eastafrica",
    "254", "kenyanfood", "nairobifood", "mamamboga", "hustlehard",
    "gengetone", "afrobeats", "kenyamusic", "kenyasports", "gormahia",
    "harambee", "kipchoge", "kenyamarathon", "nairobisunset", "eastlands",
    "westlands", "cbd", "thikaroad", "mombasa", "kisumu",
    # Lifestyle / general
    "hustle", "motivation", "mentalhealth", "selfcare", "relationships",
    "food", "nyamachoma", "ugali", "chapati", "pilau",
    "football", "soccer", "epl", "arsenal", "chelsea",
    "fitness", "workout", "running", "marathon", "health",
    # Sheng vibes
    "nairobibana", "kenyabana", "eastlandselite", "nairobisquad", "vibanda",
]

MESSAGE_CONTENTS = [
    "Sema bana! Umebuy laptop ile ya second hand? 😂",
    "Hey! Loved your latest post. Keep it up 🙌",
    "Unaweza nishare hii link ya course uliyosema? Asante.",
    "Would you be open to a quick collab on this project?",
    "Niambie siri ya kupata clients wa freelance bana 🙏",
    "Umesoma article ile ya tech yesterday? Interesting sana.",
    "Karibu kwa team — tunaanza Jumatatu! 🚀",
    "Buda, pilau ile ulisema iko wapi exactly? GPS please 😂",
    "Just followed you! Your content is top tier 🔥",
    "Any chance you're hiring? Asking for a friend 😅",
    "Saw your portfolio — impressive work honestly.",
    "Do you have resources on learning Django you'd recommend?",
    "Thanks for the review feedback last week. Really helped!",
    "Happy to collaborate on that side project still?",
    "Habari yako rafiki? Tuonane CBD lunch? 🍽️",
    "Nikusend designs za hii feature — tell me what you think.",
    "Ulifika event jana? Ilikuwa poa sana bana.",
    "Si uwongo, code uliyoandika ni clean sana. Respect.",
]


# ══════════════════════════════════════════════════════════════════════════════
#  HELPERS
# ══════════════════════════════════════════════════════════════════════════════

def collect_media_files(directory):
    if not os.path.isdir(directory):
        return []
    paths = []
    for ext in SUPPORTED_EXTENSIONS:
        paths.extend(glob.glob(os.path.join(directory, "**", f"*{ext}"), recursive=True))
        paths.extend(glob.glob(os.path.join(directory, "**", f"*{ext.upper()}"), recursive=True))
    return list(set(paths))


def attach_random_image(field, media_pool):
    """Attach a randomly chosen image from media_pool to a Django ImageField."""
    if not media_pool:
        return
    path = random.choice(media_pool)
    try:
        with open(path, "rb") as f:
            field.save(os.path.basename(path), File(f), save=False)
    except OSError:
        pass


# ══════════════════════════════════════════════════════════════════════════════
#  MANAGEMENT COMMAND
# ══════════════════════════════════════════════════════════════════════════════

class Command(BaseCommand):
    help = (
        "Seed the database with diverse fake data in English, Kiswahili and Sheng. "
        "Tweet images are pulled randomly from D:\\static\\admin\\Backup."
    )

    def add_arguments(self, parser):
        parser.add_argument("--users",    type=int, default=15,  help="Number of users to create (default 15)")
        parser.add_argument("--tweets",   type=int, default=120, help="Number of tweets to create (default 120)")
        parser.add_argument("--clear",    action="store_true",   help="Delete existing seeded data first")
        parser.add_argument("--no-media", action="store_true",   help="Skip attaching images to records")

    @transaction.atomic
    def handle(self, *args, **options):
        n_users  = options["users"]
        n_tweets = options["tweets"]
        clear    = options["clear"]
        no_media = options["no_media"]

        self.stdout.write(self.style.MIGRATE_HEADING("\n🌱  Starting seed_data command\n"))

        # ── Optional clear ─────────────────────────────────────────────────
        if clear:
            self.stdout.write("  Clearing existing data...")
            Message.objects.all().delete()
            Notification.objects.all().delete()
            Bookmark.objects.all().delete()
            Like.objects.all().delete()
            Hashtag.objects.all().delete()
            Tweet.objects.all().delete()
            User.objects.filter(is_superuser=False).delete()
            self.stdout.write(self.style.WARNING("  Cleared.\n"))

        # ── Collect media ──────────────────────────────────────────────────
        media_pool = []
        if not no_media:
            media_pool = collect_media_files(STATIC_MEDIA_DIR)
            if media_pool:
                self.stdout.write(f"  Media pool: {len(media_pool)} images found in {STATIC_MEDIA_DIR}")
            else:
                self.stdout.write(
                    self.style.WARNING(
                        f"  No images found at {STATIC_MEDIA_DIR} — running without media."
                    )
                )

        # ── Create Users ───────────────────────────────────────────────────
        self.stdout.write(f"\n  Creating {n_users} users...")
        sample_size = min(n_users, len(USERNAMES))
        usernames = random.sample(USERNAMES, sample_size)
        while len(usernames) < n_users:
            usernames.append(f"user_{len(usernames):03d}")

        users = []
        for i, uname in enumerate(usernames):
            if User.objects.filter(username=uname).exists():
                users.append(User.objects.get(username=uname))
                self.stdout.write(f"    (exists) @{uname}")
                continue

            display = DISPLAY_NAMES[i] if i < len(DISPLAY_NAMES) else uname.replace("_", " ").title()
            u = User(
                username=uname,
                email=f"{uname}@example.com",
                display_name=display,
                bio=random.choice(BIOS),
                location=random.choice(LOCATIONS),
                website=f"https://{uname}.dev",
                is_verified=random.random() < 0.15,
                is_private=random.random() < 0.10,
            )
            u.set_password("password123")
            if media_pool:
                attach_random_image(u.avatar, media_pool)
                if random.random() < 0.5:
                    attach_random_image(u.banner, media_pool)
            u.save()
            users.append(u)
            self.stdout.write(f"    Created @{uname}")

        # ── Follow relationships ───────────────────────────────────────────
        self.stdout.write("\n  Building follow graph...")
        for u in users:
            others = [x for x in users if x != u]
            targets = random.sample(others, k=random.randint(1, min(8, len(others))))
            for t in targets:
                u.followers.add(t)

        # ── Create Hashtags ────────────────────────────────────────────────
        self.stdout.write("\n  Creating hashtags...")
        hashtags = []
        for name in HASHTAG_NAMES:
            h, _ = Hashtag.objects.get_or_create(name=name)
            hashtags.append(h)

        # ── Create Tweets ──────────────────────────────────────────────────
        self.stdout.write(f"\n  Creating {n_tweets} tweets from a pool of {len(ALL_TWEETS)} unique posts...")
        tweets = []
        for _ in range(n_tweets):
            author  = random.choice(users)
            content = random.choice(ALL_TWEETS)
            t = Tweet(
                user=author,
                content=content,
                views_count=random.randint(0, 50000),
                created_at=timezone.now() - timezone.timedelta(
                    days=random.randint(0, 180),
                    hours=random.randint(0, 23),
                    minutes=random.randint(0, 59),
                ),
            )
            if media_pool and random.random() < 0.25:
                attach_random_image(t.media, media_pool)
            t.save()
            t.hashtags.set(random.sample(hashtags, k=random.randint(1, 4)))
            tweets.append(t)

        # ── Replies ────────────────────────────────────────────────────────
        self.stdout.write("  Adding replies...")
        reply_sample = random.sample(tweets, k=min(40, len(tweets)))
        for parent in reply_sample:
            r = Tweet(
                user=random.choice(users),
                content=random.choice(ALL_TWEETS),
                reply_to=parent,
                views_count=random.randint(0, 5000),
            )
            r.save()
            tweets.append(r)

        # ── Retweets ───────────────────────────────────────────────────────
        self.stdout.write("  Adding retweets...")
        rt_sample = random.sample(tweets, k=min(25, len(tweets)))
        for original in rt_sample:
            rt = Tweet(
                user=random.choice(users),
                content=original.content,
                retweet_of=original,
                views_count=random.randint(0, 10000),
            )
            rt.save()
            tweets.append(rt)

        # ── Likes ──────────────────────────────────────────────────────────
        self.stdout.write("  Adding likes...")
        like_pairs = set()
        for _ in range(min(n_tweets * 5, 3000)):
            u = random.choice(users)
            t = random.choice(tweets)
            if (u.id, t.id) not in like_pairs:
                Like.objects.get_or_create(user=u, tweet=t)
                like_pairs.add((u.id, t.id))

        # ── Bookmarks ─────────────────────────────────────────────────────
        self.stdout.write("  Adding bookmarks...")
        bm_pairs = set()
        for _ in range(min(n_tweets * 2, 600)):
            u = random.choice(users)
            t = random.choice(tweets)
            if (u.id, t.id) not in bm_pairs:
                Bookmark.objects.get_or_create(user=u, tweet=t)
                bm_pairs.add((u.id, t.id))

        # ── Notifications ─────────────────────────────────────────────────
        self.stdout.write("  Adding notifications...")
        notif_types = ["like", "retweet", "reply", "follow", "mention"]
        for _ in range(min(n_tweets * 3, 800)):
            sender    = random.choice(users)
            recipient = random.choice([u for u in users if u != sender])
            ntype     = random.choice(notif_types)
            Notification.objects.create(
                sender=sender,
                recipient=recipient,
                notification_type=ntype,
                tweet=random.choice(tweets) if ntype != "follow" else None,
                is_read=random.random() < 0.4,
                created_at=timezone.now() - timezone.timedelta(days=random.randint(0, 60)),
            )

        # ── Messages ──────────────────────────────────────────────────────
        self.stdout.write("  Adding messages...")
        for _ in range(min(n_users * 10, 400)):
            sender    = random.choice(users)
            recipient = random.choice([u for u in users if u != sender])
            Message.objects.create(
                sender=sender,
                recipient=recipient,
                content=random.choice(MESSAGE_CONTENTS),
                is_read=random.random() < 0.6,
                created_at=timezone.now() - timezone.timedelta(
                    days=random.randint(0, 30),
                    hours=random.randint(0, 23),
                ),
            )

        # ── Summary ───────────────────────────────────────────────────────
        self.stdout.write(self.style.SUCCESS(f"""
╔══════════════════════════════════════════╗
║          Seed complete!                  ║
╠══════════════════════════════════════════╣
║  Users          : {User.objects.count():<5}                  ║
║  Tweets         : {Tweet.objects.count():<5}                  ║
║  Likes          : {Like.objects.count():<5}                  ║
║  Bookmarks      : {Bookmark.objects.count():<5}                  ║
║  Hashtags       : {Hashtag.objects.count():<5}                  ║
║  Notifications  : {Notification.objects.count():<5}                  ║
║  Messages       : {Message.objects.count():<5}                  ║
╚══════════════════════════════════════════╝

  Default password for all seeded users: password123
"""))