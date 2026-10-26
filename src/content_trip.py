# Trip-level, ship and line content for the Koningsdam guide.

TRIP = {
    "title": "Mexican Riviera Holiday",
    "ship": "ms Koningsdam",
    "dates": "Dec 26, 2026 – Jan 2, 2027",
    "depart_utc": "2026-12-27T01:00:00Z",   # Dec 26 5:00 pm PST
    "arrive_utc": "2027-01-02T15:00:00Z",   # Jan 2 7:00 am PST
}

# Port calls in UTC (for the route slider and live countdowns)
CALLS = [
    {"id": "sd", "name": "San Diego", "arr": None, "dep": "2026-12-27T01:00:00Z", "utc": -8},
    {"id": "pv", "name": "Puerto Vallarta", "arr": "2026-12-29T14:00:00Z", "dep": "2026-12-29T23:00:00Z", "utc": -6},
    {"id": "mz", "name": "Mazatlán", "arr": "2026-12-30T15:00:00Z", "dep": "2026-12-31T00:00:00Z", "utc": -7},
    {"id": "cb", "name": "Cabo San Lucas", "arr": "2026-12-31T14:00:00Z", "dep": "2026-12-31T21:00:00Z", "utc": -7},
    {"id": "sd2", "name": "San Diego", "arr": "2027-01-02T15:00:00Z", "dep": None, "utc": -8},
]

LEG_NAMES = {
    "sd_pv": ("San Diego", "Puerto Vallarta", 61),
    "pv_mz": ("Puerto Vallarta", "Mazatlán", 16),
    "mz_cb": ("Mazatlán", "Cabo San Lucas", 14),
    "cb_sd": ("Cabo San Lucas", "San Diego", 42),
}

# Things you pass. Along-track distance and timing are computed at build time from the route.
POIS = {
    "coronado": ("Islas Coronado", "Four small Mexican islands just south of the border, home to nesting seabirds. The ship passes within a few miles."),
    "ens": ("Ensenada", "Mexico's busiest cruise port in 2025, with 1.3 million passengers. The lights are off the port side heading south."),
    "cedros": ("Isla Cedros", "A big, mountainous island. Just inside it lies Bahía Sebastián Vizcaíno."),
    "ojo": ("Ojo de Liebre lagoon", "The biggest gray-whale nursery on Earth, beside the Guerrero Negro saltworks. Whales arrive from late December."),
    "sanig": ("San Ignacio lagoon", "Another gray-whale calving lagoon, famous for 'friendly' whales that approach small boats."),
    "mag": ("Magdalena Bay", "The southernmost gray-whale lagoon system, sheltered behind long barrier islands."),
    "cb": ("Land's End", "The granite tip of the Baja peninsula and El Arco, where the Pacific meets the Sea of Cortez."),
    "marias": ("Islas Marías", "A federal prison colony from 1905 until 2019. The islands are now a biosphere reserve."),
    "marietas": ("Islas Marietas", "Guano-white islets at the mouth of Banderas Bay. Blue-footed boobies and humpbacks."),
}

# Climate averages and approximate sun times (local)
WEATHER = [
    {"place": "San Diego", "date": "Dec 26", "hi": 65, "lo": 49, "water": 59, "rise": "6:49 am", "set": "4:49 pm", "port": "sd"},
    {"place": "Puerto Vallarta", "date": "Dec 29", "hi": 84, "lo": 63, "water": 78, "rise": "7:35 am", "set": "6:30 pm", "port": "pv"},
    {"place": "Mazatlán", "date": "Dec 30", "hi": 78, "lo": 60, "water": 73, "rise": "6:48 am", "set": "5:30 pm", "port": "mz"},
    {"place": "Cabo San Lucas", "date": "Dec 31", "hi": 79, "lo": 60, "water": 75, "rise": "7:01 am", "set": "5:45 pm", "port": "cb"},
    {"place": "San Diego", "date": "Jan 2", "hi": 65, "lo": 49, "water": 58, "rise": "6:51 am", "set": "4:54 pm", "port": "sd"},
]

DAYS = [
    {"date": "2026-12-26", "dow": "Sat", "md": "Dec 26", "tag": "Day 1", "title": "San Diego · sail away 5 pm", "port": "sd",
     "zone": "PST · UTC−8", "sun": ("6:49 am", "4:49 pm"),
     "items": [("Midday", "Check in at the cruise terminal during your boarding window"), ("~4 pm", "All aboard (about an hour before sailing; check your boarding pass)"), ("5:00 pm", "Sail past Point Loma at dusk"), ("6–9 pm", "Islas Coronado, then the lights of Ensenada to port (left)")],
     "note": "Sunset is 4:49 pm, so you sail out just after dark. Go aft or to an open deck for the city lights and the Coronado Bridge."},
    {"date": "2026-12-27", "dow": "Sun", "md": "Dec 27", "tag": "Day 2", "title": "At sea off Baja's Pacific coast",
     "zone": "Ship time may move +1 h overnight",
     "items": [("Morning", "Passing Isla Cedros and Bahía Sebastián Vizcaíno"), ("Afternoon", "Abeam of Ojo de Liebre, the biggest gray-whale nursery"), ("All day", "Watch for southbound gray whales: low heart-shaped blows, no dorsal fin")],
     "note": "First full sea day. Claim a table in the Crow's Nest early if you want a puzzle going."},
    {"date": "2026-12-28", "dow": "Mon", "md": "Dec 28", "tag": "Day 3", "title": "At sea · Tropic of Cancer · Land's End",
     "zone": "Ship time should reach UTC−6 by tomorrow",
     "items": [("~Mid-morning", "Cross the Tropic of Cancer (23.44° N) southbound"), ("~Early afternoon", "Pass Land's End and El Arco, then cross the mouth of the Sea of Cortez"), ("All day", "Día de los Santos Inocentes, Mexico's April Fools' Day")],
     "note": "Clocks must gain two hours between San Diego and Puerto Vallarta, usually one hour per night. The daily program has the official change."},
    {"date": "2026-12-29", "dow": "Tue", "md": "Dec 29", "tag": "Day 4", "title": "Puerto Vallarta · 8 am – 5 pm", "port": "pv",
     "zone": "CST · UTC−6", "sun": ("7:35 am", "6:30 pm"),
     "items": [("~7 am", "Enter Banderas Bay past the Marietas at first light"), ("8:00 am", "Docked at Marina Vallarta, 3 miles north of the Malecón"), ("4:30 pm", "Aim to be back aboard (all aboard is normally 30 min before sailing)"), ("5:00 pm", "Sail")],
     "note": "Tuesday: the Marietas Hidden Beach is closed Mondays and Tuesdays, so don't pay extra for it."},
    {"date": "2026-12-30", "dow": "Wed", "md": "Dec 30", "tag": "Day 5", "title": "Mazatlán · 8 am – 5 pm", "port": "mz",
     "zone": "MST · UTC−7 (clocks back 1 h overnight)", "sun": ("6:48 am", "5:30 pm"),
     "items": [("Overnight", "Pass the Islas Marías, a prison colony until 2019"), ("8:00 am", "Docked in the commercial port; free tram to the gate"), ("4:30 pm", "Aim to be back aboard"), ("5:00 pm", "Sail")],
     "note": "Stay inside the U.S. advisory zone: the historic center and the Malecón."},
    {"date": "2026-12-31", "dow": "Thu", "md": "Dec 31", "tag": "Day 6", "title": "Cabo San Lucas · 7 am – 2 pm · New Year's Eve", "port": "cb",
     "zone": "MST · UTC−7", "sun": ("7:01 am", "5:45 pm"),
     "items": [("7:00 am", "Anchor off El Arco; tenders run into the marina"), ("~1:15–1:30 pm", "Last tender (check the daily program)"), ("2:00 pm", "Sail"), ("~6 pm", "Cross the Tropic of Cancer northbound at dusk"), ("Midnight", "Ring in 2027 at sea. Bring 12 grapes aboard")],
     "note": "Tender days run tight. Be in the tender line 45–60 min before the last boat."},
    {"date": "2027-01-01", "dow": "Fri", "md": "Jan 1", "tag": "Day 7", "title": "At sea · New Year's Day",
     "zone": "Clocks back to UTC−8 tonight or tomorrow",
     "items": [("Daytime", "Northbound past the San Ignacio and Ojo de Liebre whale lagoons, then Isla Cedros"), ("Afternoon", "Pack and check your onboard account in the Navigator app"), ("Tonight", "Checked bags go out in the corridor (unless you walk off with them)")],
     "note": "Last whale-watching window. Gray whales are heading the other way to the lagoons you passed on Sunday."},
    {"date": "2027-01-02", "dow": "Sat", "md": "Jan 2", "tag": "Day 8", "title": "San Diego · arrive 7 am", "port": "sd",
     "zone": "PST · UTC−8", "sun": ("6:51 am", "4:54 pm"),
     "items": [("7:00 am", "Arrive San Diego"), ("From ~7:30 am", "Disembarkation; walk-off guests leave first"), ("9:00 am", "San Diego Zoo opens, if you're going"), ("Afternoon", "La Jolla, the USS Midway, or the drive north")],
     "note": "See the San Diego page for a few ways to spend the day."},
]

SHIP_SPECS = [
    ("Gross tonnage", "99,863 GT"),
    ("Length overall", "299.65 m · 983 ft"),
    ("Beam", "35.0 m · 115 ft"),
    ("Draft", "7.95 m · 26 ft"),
    ("Generators", "4 × MaK 12V43C"),
    ("Generating power", "50.4 MW · ~67,600 hp"),
    ("Propulsion", "2 × ABB Azipod, 14 MW each"),
    ("Speed", "18.0 kn service · 22.2 kn max"),
    ("Guests", "2,650 double occ."),
    ("Max aboard", "4,173 persons"),
    ("Guest cabins", "1,331 (68.5% balcony)"),
    ("Crew cabins", "588"),
    ("Builder", "Fincantieri, Marghera (Venice)"),
    ("Delivered", "March 31, 2016"),
    ("Class / flag", "Pinnacle class · Netherlands"),
    ("IMO / call sign", "9692557 · PBGJ"),
]

SHIP_FACTS = [
    "The engines never turn a propeller. Four diesel generators feed one electrical grid that powers both the propulsion motors and the hotel: lights, galleys, air conditioning.",
    "There is no conventional rudder. Each Azipod is an electric motor in a pod under the hull that rotates 360°, so the ship steers by pointing its thrust.",
    "Each MaK 12V43C has 12 cylinders with a 43 cm bore and a 61 cm stroke. One cylinder sweeps about 89 liters, so a single cylinder is about 44 times a typical 2.0-liter car engine.",
    "Total generating power is 50.4 MW, about 67,600 hp, or roughly 66 Tesla Model S Plaids flat out.",
    "Propulsion power rises with the cube of speed. Going from 18 to 22 knots needs about 83% more propulsion power.",
    "Its hull, redesigned bulbous bow and local cooling let it use about 20% less power than Nieuw Amsterdam while carrying about 20% more guests.",
    "Fincantieri built it at Marghera in Venice. It was the yard's 15th ship for Holland America.",
    "Steel was cut on Feb 4, 2014. The keel was laid on Aug 22, 2014 with a 680-ton block. Delivery was March 31, 2016 and the maiden voyage followed on April 8.",
    "For luck, two gold coins showing King Willem-Alexander were welded into the hull at a coin ceremony in February 2015.",
    "Queen Máxima of the Netherlands christened the ship in Rotterdam on May 20, 2016.",
    "Koningsdam means King's dam. The name honors Willem-Alexander, the first Dutch king in more than a century.",
    "At delivery it was the largest ship Holland America had ever commissioned. Royal Caribbean's Icon class is about 2.5 times its gross tonnage.",
    "It is about 30 m longer than Titanic and has more than twice Titanic's enclosed volume.",
    "Six tenders built by Hatecke ferry guests ashore at anchor ports. One of them takes you into Cabo.",
    "The whole design is music-themed, down to the deck names: Beethoven, Gershwin, Schubert.",
    "World Stage is a two-deck theater seating 667, with a 270° wall of LED screens.",
    "Lincoln Center Stage seats 330 for chamber music. Later in the evening the same room becomes B.B. King's Blues Club.",
    "BLEND by Chateau Ste. Michelle was the first wine-blending venue at sea. Ten guests at a time blend their own bottle from barrels.",
    "The Lido pool sits under a magrodome, a retractable glass roof, so it works in any weather.",
    "The ship's IT systems were supplied by Lufthansa Systems.",
    "It was designed to meet Safe Return to Port rules: redundant engine rooms and systems so it can sail home on its own after a fire or flooding in one zone.",
    "The Crow's Nest on Deck 12 forward has about 270° of view. It is the best whale-watching seat on the ship.",
    "Cabins have both U.S. 110 V and European 220 V outlets. Surge protectors are banned, so bring a plain multi-USB charger.",
    "In December 2021, a crew COVID outbreak stopped guests from going ashore in Puerto Vallarta. You'll get the day your predecessors missed.",
]

# Deck plan: venues by deck and section (Fwd / Mid / Aft per Holland America's deck pages)
DECKS = [
    {"n": 12, "name": "Observation", "venues": {"Fwd": ["Crow's Nest", "Explorations Café"], "Mid": ["The Retreat (cabanas, extra cost)"]},
     "tip": "Best seat for whales at first light. Games, puzzles and books live up here."},
    {"n": 11, "name": "Sun", "venues": {"": ["Sun Deck", "Sports court (pickleball)", "Sun Bar"]},
     "tip": "Open-air laps and the widest sky for sunset."},
    {"n": 10, "name": "", "venues": {"Mid": ["New York Deli & Pizza", "Club HAL"], "Aft": ["Tamarind (Pan-Asian, extra cost)", "Tamarind Bar", "Nami Sushi"]},
     "tip": "Late-night pizza is mid-ship on this deck."},
    {"n": 9, "name": "Lido", "venues": {"Fwd": ["Greenhouse Spa & Salon", "Fitness Center", "Hydro Pool"], "Mid": ["Lido Pool under the glass magrodome", "Lido Market (buffet)", "Dive-In (burgers)", "Gelato", "Lido Bar"], "Aft": ["Sea View Pool & Bar"]},
     "tip": "Take breakfast aft at the Sea View Pool and watch the wake."},
    {"n": 8, "name": "Navigation", "venues": {"Fwd": ["The Bridge (crew only)"], "": ["Staterooms"]},
     "tip": "The same deck as the bridge, directly below the Lido."},
    {"n": 7, "name": "Schubert", "venues": {"": ["Staterooms", "Neptune Lounge (suite guests)"]}, "tip": ""},
    {"n": 6, "name": "", "venues": {"": ["Staterooms"]}, "tip": ""},
    {"n": 5, "name": "Gershwin", "venues": {"": ["Staterooms"]}, "tip": ""},
    {"n": 4, "name": "Beethoven", "venues": {"": ["Staterooms"]}, "tip": "One deck above the casino and the top of World Stage."},
    {"n": 3, "name": "Promenade", "venues": {"Fwd": ["World Stage (upper level)", "Casino", "Art Gallery"], "Mid": ["Atrium", "Guest Services", "Grand Dutch Café", "The Shops"], "Aft": ["The Dining Room (upper level)"]},
     "tip": "Grand Dutch Café serves bitterballen and Dutch coffee all day."},
    {"n": 2, "name": "Plaza", "venues": {"Fwd": ["World Stage (lower level)", "Billboard Onboard", "Rolling Stone Rock Room"], "Mid": ["Pinnacle Grill", "Lincoln Center Stage / B.B. King's Blues Club", "Music Walk"], "Aft": ["The Dining Room (lower level)"]},
     "tip": "Music Walk runs mid to fore. Dueling pianos, a rock band and blues all play here on the same evening."},
    {"n": 1, "name": "Main", "venues": {"Mid": ["Meeting rooms"], "": ["Staterooms"]},
     "tip": "Lowest guest deck and the least motion in a swell."},
]
ELSEWHERE = ["Rudi's Sel de Mer (French seafood)", "Canaletto (Italian, on the Lido)", "BLEND wine studio", "Digital Workshop"]

HAL_FACTS = [
    "Founded April 18, 1873 in Rotterdam as the Nederlandsch-Amerikaansche Stoomvaart Maatschappij, the Netherlands-America Steamship Company. The line still marks April 18.",
    "The first Rotterdam sailed from the Netherlands to New York in 1872 under the predecessor firm Plate, Reuchlin & Co.",
    "The public called it Holland America Line for years before the name became official in 1896.",
    "Its ships carried hundreds of thousands of European emigrants to America: people westbound, cargo eastbound.",
    "Regular Rotterdam–North America passenger service ended in 1971. The line ran its first standalone Atlantic crossing in 40 years in 2011.",
    "When Germany invaded in 1940, the company moved its seat to Curaçao. Nieuw Amsterdam (1938) then carried hundreds of thousands of Allied troops.",
    "Since the 1890s nearly every ship name ends in -dam, after Dutch places built around dams: Rotterdam, Amsterdam, Edam, Schiedam.",
    "The four Vista-class ships are named for the compass: Oosterdam, Westerdam, Noordam and Zuiderdam.",
    "The 2021 flagship is the seventh ship named Rotterdam. Rotterdam V (1959) is now a hotel in Rotterdam harbor.",
    "Part of Carnival Corporation since 1989, with headquarters in Seattle.",
    "The fleet is 11 mid-size ships of about 61,000–100,000 GT. P&O's Arcadia joins in 2029.",
    "In April 2026 the line announced Holland America Evolution: more than $500 million to refit six ships, starting with Oosterdam in fall 2027.",
    "It sails to nearly 400 ports in 114 countries.",
    "It has sailed Alaska for more than 75 years, longer than any other line.",
    "Its private island in the Bahamas, Half Moon Cay, is now RelaxAway, Half Moon Cay, shared with Carnival.",
    "The line turned 150 in 2023.",
    "Members of the Dutch royal family have christened its ships many times.",
    "Much of the crew is Indonesian and Filipino. The crew show, if your sailing has one, is often the best night of the week.",
    "In 1912, ice warnings from its ship Noordam were relayed to Titanic.",
    "Music partners aboard include B.B. King's, Billboard, Lincoln Center and Rolling Stone.",
    "It has no new ships on order. It is refitting its fleet and taking over Arcadia instead.",
]

WIFI = [
    ("Surf", "Web, email, messaging. No calls or video."),
    ("Premium", "Adds audio and video messaging. About US$26/day on a 7-day plan."),
    ("Stream", "Adds Netflix, Disney+ and Wi-Fi calling. About US$38/day on a 7-day plan."),
]


SITE_URL = "daniel-beachy.github.io/cruise-guide-v1"

# Group cabins. Put the number in "cabin" (e.g. 6123) once Holland America assigns it; the deck is derived from it.
CABINS = [
    {"who": "Daniel & Taylor", "cabin": None, "tbd": "Not assigned yet", "type": "Inside", "note": "Guarantee booking. Holland America assigns the cabin closer to sailing."},
    {"who": "Parents", "cabin": None, "type": "", "note": ""},
    {"who": "Tyson & Malea", "cabin": None, "type": "", "note": ""},
]
