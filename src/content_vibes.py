# Day "vibes": loose options for each port, for anyone in the group. Nothing here is booked.
# Each vibe: name, one-line pitch, effort level, what to bring, and loose blocks (when, idea, detail).

VIBES = {
    "pv": [
        {"name": "Easy & scenic", "effort": "Easy", "pitch": "Old town, the seafront and a long beach lunch.",
         "bring": ["Walking shoes", "Hat", "Pesos for the market"],
         "blocks": [("Morning", "Malecón sculpture walk", "Taxi or Uber 15–20 min to El Centro, then stroll the seafront up to the crowned church."),
                    ("Midday", "Isla Río Cuale market and lunch on the sand", "Crafts and Huichol art on the river island, then pescado embarado at Los Muertos Beach."),
                    ("Afternoon", "Tequila tasting or a whale-watching boat", "Licensed whale boats leave from Los Muertos pier. Back at the terminal by about 4.")]},
        {"name": "Sea life & trails", "effort": "Active", "pitch": "A jungle cliff trail, then snorkeling at Los Arcos.",
         "bring": ["Masks and snorkels", "Trail shoes", "Swimsuit under clothes", "Dry bag"],
         "blocks": [("Morning", "Coast trail from Boca de Tomatlán", "Taxi 40–45 min south, then 1.5–2 h of trail via Colomitos cove to Las Ánimas beach."),
                    ("Midday", "Panga to Los Arcos to snorkel", "Reef fish, morays and sometimes rays in the marine park."),
                    ("Afternoon", "Aguachile in the Zona Romántica", "Then a 25–30 min taxi back to the terminal.")],
         "also": "Or a ship excursion: a dolphin or sea-lion encounter, a canopy zip-line, a countryside horseback ride, or a Marietas snorkel tour (6+ h; pick one with a guaranteed return time)."},
        {"name": "Ship day", "effort": "Chill", "pitch": "Most people go ashore, so the ship is at its quietest.",
         "bring": ["A book", "Sunscreen"],
         "blocks": [("Morning", "Pool, spa or a quiet deck", "The Lido pool and loungers are easy to get on a port day."),
                    ("Midday", "Lunch at Marina Vallarta", "Waterfront restaurants are a short taxi ride from the terminal."),
                    ("Afternoon", "Sail-away from the top deck", "Banderas Bay and the Sierra Madre at 5 pm, with a chance of humpbacks.")]},
    ],
    "mz": [
        {"name": "Old town stroll", "effort": "Easy", "pitch": "Plazas, the cathedral, cliff divers and a pulmonía ride.",
         "bring": ["Walking shoes", "Cash for the pulmonía"],
         "blocks": [("Morning", "Into the Centro Histórico", "Free tram to the gate, then a pulmonía or the 1-mile blue line."),
                    ("Midday", "Cathedral, market and Plazuela Machado", "Mercado Pino Suárez for snacks, then the theater plaza cafés."),
                    ("Afternoon", "Olas Altas and a Malecón ride", "Cliff divers, a seafood lunch and an open-air pulmonía along the seafront.")]},
        {"name": "Climb & explore", "effort": "Active", "pitch": "El Faro's stairs first, then the old town on foot.",
         "bring": ["Water", "Trail or walking shoes", "Sunscreen"],
         "blocks": [("Morning", "Climb El Faro", "A steep 30–45 min stair climb. Go early, before the heat; you look down on the ship."),
                    ("Midday", "Old town and the cliff divers", "Cathedral, market and Plazuela Machado, then Olas Altas."),
                    ("Afternoon", "Walk the Malecón north", "To the Monumento al Pescador, then a pulmonía back. Stay on the Malecón.")]},
        {"name": "Taste of Mazatlán", "effort": "Easy", "pitch": "A food crawl through the city that invented aguachile.",
         "bring": ["Appetite", "Pesos in small bills"],
         "blocks": [("Morning", "Mercado Pino Suárez", "Tamales barbones (shrimp tamales), fresh juice and the shrimp stalls."),
                    ("Midday", "Aguachile and zarandeado", "A seafood lunch at Olas Altas; split a 950 ml Pacífico ballena."),
                    ("Afternoon", "Raspados and a plaza coffee", "Shaved ice from a cart, then back to the ship.")]},
    ],
    "cb": [
        {"name": "Arch & beach", "effort": "Easy", "pitch": "El Arco up close and a calm beach.",
         "bring": ["Swimsuit", "Water shoes", "Cash for the boat"],
         "blocks": [("Morning", "Glass-bottom boat loop", "El Arco, the sea lions and Pelican Rock in 60–75 min."),
                    ("Late morning", "Lover's Beach drop-off", "Arrange the pickup time with the same boat. Swim only on the bay side."),
                    ("Midday", "Marina boardwalk and fish tacos", "Stay close to the tender dock.")]},
        {"name": "Snorkel & whales", "effort": "Active", "pitch": "Pelican Rock's fish, then humpbacks off the arch.",
         "bring": ["Masks and snorkels", "Rash guard", "Dry bag"],
         "blocks": [("Early", "First tenders ashore", "Ship-tour guests board first, then everyone else."),
                    ("Morning", "Snorkel from Lover's Beach toward Pelican Rock", "Water taxi past the arch; bay side only."),
                    ("Late morning", "Small-boat whale watch", "Humpbacks breach off Land's End in December.")],
         "also": "Or the ship's sea kayak & snorkel tour, a beach horseback ride, a dolphin encounter, half-day sportfishing, or a taxi to Santa María or Chileno Bay for clearer water."},
        {"name": "Short & sweet", "effort": "Chill", "pitch": "Skip the early tender rush and save energy for New Year's Eve.",
         "bring": ["A tote for shopping"],
         "blocks": [("Mid-morning", "Tender once the lines ease", "Usually after the first couple of hours."),
                    ("Late morning", "Stroll the marina", "Shops, a margarita and 12 grapes for midnight."),
                    ("Midday", "Back aboard early", "Watch El Arco from the deck as the ship sails at 2.")]},
    ],
    "sd": [
        {"name": "Zoo morning", "effort": "Moderate", "pitch": "Pandas at opening, then lunch in the park.",
         "bring": ["Zoo tickets bought ahead", "Walking shoes"],
         "blocks": [("7–8:30", "Walk off and get to the car", "Self-assist walk-off gets you off first if you carry your own bags."),
                    ("9:00", "San Diego Zoo opens", "Pandas first, then the route on this page. Parking is $16."),
                    ("Afternoon", "Optional: La Jolla Cove", "Sea lions and seals from the seawall, then fish tacos.")]},
        {"name": "Coast & sea lions", "effort": "Easy", "pitch": "The coast north of the city with sea lions and cliffs.",
         "bring": ["Layers (cool morning)", "Binoculars"],
         "blocks": [("Morning", "La Jolla Cove", "Sea lions and harbor seals from the seawall."),
                    ("Midday", "Birch Aquarium or Torrey Pines", "The aquarium takes 1.5–2 h; the clifftop trails are a good gray-whale lookout."),
                    ("Afternoon", "Beach towns heading north", "Encinitas, Carlsbad or the Oceanside pier.")]},
        {"name": "Quick & easy", "effort": "Chill", "pitch": "One good stop near the pier, then on the road.",
         "bring": ["Snacks for the drive"],
         "blocks": [("Morning", "USS Midway Museum", "Beside the cruise terminal; allow 2–3 h. The engineering spaces are the draw."),
                    ("Midday", "Fish tacos or a California burrito", "Oscar's, Mariscos German, Lolita's or Lucha Libre."),
                    ("Afternoon", "On the road", "LA is 2.5–3.5 h on a holiday weekend.")]},
    ],
}

SD_EMBARK = [
    "Terminal: B Street Pier (1140 N. Harbor Dr.) or the neighboring Broadway Pier. Your Holland America documents say which.",
    "From LA it's about 120 miles, 2–2.5 hours. Aim to arrive within your check-in window; all aboard is about an hour before the 5 pm sailing.",
    "Port-run parking lots sit beside the terminal. Reserve ahead if you can and check current rates.",
    "Drop people and bags at the curb first, then park. Porters take checked bags; about $2 a bag is customary.",
    "Keep passports, medications, swimsuits and chargers in your carry-on. Checked bags may not reach the cabin until evening.",
]

SD_DISEMBARK = [
    "Self-assist walk-off: carry all your own bags and leave first, usually from about 7:30 am.",
    "Tagged luggage: put bags out the night before, leave later in the morning by your assigned group, and collect them in the terminal.",
    "Customs (CBP) is quick for U.S. citizens. Have passports ready.",
    "The Zoo is about 2.5 miles from the pier, roughly 10 minutes by car. Keep luggage out of sight in the trunk anywhere you park.",
]

SKY_TARGETS = [
    ("Saturn", "Evening, high in the south", "A steady, pale-gold point high in the south after sunset. It sets around 1 am. You need a telescope to see the rings."),
    ("Jupiter and Regulus", "Rises about 10 pm in the east", "The brightest thing in the late-night sky, sitting about 3.5° (two finger-widths) from Regulus, the heart of Leo. Brace binoculars on the rail and look for up to four moons in a line."),
    ("Mars", "Rises about 11 pm", "Orange-red, about 10° from Jupiter. It's brightening toward opposition in February 2027."),
    ("Venus", "Before dawn, low in the southeast", "The 'morning star', far brighter than anything else in the sky. It rises around 4 am."),
    ("Canopus", "Around midnight, low in the south", "The second-brightest star in the night sky. It never rises in Portland and barely clears San Diego's horizon, but off Mexico it climbs to about 15°."),
    ("Orion and Sirius", "Evening onward, east to south", "Orion is high by midnight; follow his belt down-left to Sirius, the brightest star."),
    ("Polaris drops", "Due north, all night", "Polaris sits at an altitude equal to your latitude: about 32° in San Diego and about 23° off Mazatlán. A fist at arm's length is roughly 10°."),
    ("Southern Cross (long shot)", "Just before dawn, due south", "On Dec 29–30 its top star, Gacrux, reaches about 10° in twilight. The rest of the cross stays too low to see."),
    ("Green flash", "The moment the sun sets", "A clear sea horizon is the best place to catch a brief green flash on the sun's last sliver. Look right at the last moment, not before."),
    ("Glowing wake", "On a dark night, looking down", "Bioluminescent plankton can sparkle blue-green in the ship's wake. Look straight down from an open deck aft or along the side."),
]

SKY_TIPS = [
    "Find the darkest open deck you can, often forward or aft on the upper decks, away from pool lights.",
    "Give your eyes 15–20 minutes. Turn your phone to red night mode (Sky Guide has one) and dim the screen.",
    "Your phone's GPS works with no signal, so Sky Guide places the stars correctly at sea. Its support pages say it needs no internet.",
    "At 12× magnification the view shakes on a moving ship. Brace your elbows on the rail, or lean against a wall.",
]

SKY_APPS = [
    ("Sky Guide", "Works fully offline. Point it at the sky to name stars and planets; it also shows stars below the horizon."),
    ("Stellarium Mobile", "Free, with a deeper catalog. Good as a backup and for planning by setting any date and place."),
    ("SkyView Lite", "Free and the simplest point-and-identify app."),
]
