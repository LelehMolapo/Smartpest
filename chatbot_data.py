import re


CHATBOT_DEFAULT_SUGGESTIONS = [
    "How do I book a service?",
    "How do you treat cockroaches?",
    "Are treatments safe for children and pets?",
    "What is included in weed management?",
    "How much does pest control cost?",
]


PEST_PROFILES = [
    {
        "aliases": ["rat", "rats", "rodent", "rodents", "mouse", "mice"],
        "title": "Rodents (Rats and Mice)",
        "signs": "Droppings, gnaw marks, scratching sounds in ceilings/walls, food packaging damage, and grease marks near walls.",
        "risks": "Disease spread, food contamination, wiring damage, and possible fire risk from damaged cables.",
        "prevention": "Seal entry points, store food in hard containers, fix leaks, remove clutter, and improve waste control.",
        "treatment": "Inspection, bait stations, controlled trapping strategy, proofing recommendations, and follow-up monitoring.",
    },
    {
        "aliases": ["cockroach", "cockroaches", "roach", "roaches"],
        "title": "Cockroaches",
        "signs": "Night activity, pepper-like droppings, egg cases, and musty odor in cupboards or drains.",
        "risks": "Food contamination and asthma/allergy triggers.",
        "prevention": "Keep kitchens dry/clean, repair leaks, close drain gaps, and remove food residue.",
        "treatment": "Targeted baiting, crack-and-crevice treatment, sanitation corrections, and scheduled follow-up.",
    },
    {
        "aliases": ["termite", "termites", "white ant", "white ants"],
        "title": "Termites",
        "signs": "Mud tubes, hollow-sounding wood, blistered paint, discarded wings, and damaged wood frames.",
        "risks": "Serious structural damage if not managed early.",
        "prevention": "Reduce wood-soil contact, fix dampness, and inspect timber and foundations regularly.",
        "treatment": "Inspection, targeted treatment barriers, colony control strategy, and periodic re-inspection.",
    },
    {
        "aliases": ["ant", "ants"],
        "title": "Ants",
        "signs": "Visible trails, colony activity around moisture zones or wall voids.",
        "risks": "Recurring food contamination and persistent re-entry from active colonies.",
        "prevention": "Seal gaps, remove food residue, control moisture, and trim vegetation touching structures.",
        "treatment": "Species-targeted bait program and entry-point treatment.",
    },
    {
        "aliases": ["bedbug", "bedbugs", "bed bug", "bed bugs"],
        "title": "Bed Bugs",
        "signs": "Bites in clusters/lines, blood spots on sheets, and dark spotting near mattress seams.",
        "risks": "Sleep disruption and repeated spread through luggage or furniture.",
        "prevention": "Inspect second-hand furniture, reduce clutter, and check luggage after travel.",
        "treatment": "Detailed room inspection, targeted treatment plan, and staged follow-up visits.",
    },
    {
        "aliases": ["mosquito", "mosquitoes"],
        "title": "Mosquitoes",
        "signs": "High activity near standing water and frequent bites at dusk/night.",
        "risks": "Vector-borne disease risk and high nuisance levels.",
        "prevention": "Remove stagnant water, maintain drainage, and clear overgrown vegetation.",
        "treatment": "Larval source control, adult mosquito reduction, and prevention guidance.",
    },
    {
        "aliases": ["fly", "flies"],
        "title": "Flies",
        "signs": "Persistent indoor/outdoor fly activity near waste, drains, or food handling zones.",
        "risks": "Food hygiene risk and contamination.",
        "prevention": "Strict waste control, drain cleaning, and proofing with screens/door control.",
        "treatment": "Source reduction, targeted treatment, and control devices where needed.",
    },
    {
        "aliases": ["wasp", "wasps", "bee", "bees"],
        "title": "Wasps and Stinging Insects",
        "signs": "Nest activity under roofs, eaves, trees, or cavity spaces.",
        "risks": "Stings and possible allergic reactions.",
        "prevention": "Early nest detection and no disturbance around active nests.",
        "treatment": "Controlled removal by trained technicians using PPE and safe perimeter control.",
    },
    {
        "aliases": ["bird", "birds", "gull", "gulls", "pigeon", "pigeons"],
        "title": "Bird and Gull Control",
        "signs": "Nesting/roosting on roofs, droppings accumulation, blocked gutters, and noise issues.",
        "risks": "Hygiene risk, damage, and business disruption.",
        "prevention": "Proofing, sanitation, and habitat management.",
        "treatment": "Humane exclusion methods, bird-proofing systems, and maintenance plans.",
    },
]


INTENT_RULES = [
    {
        "keywords": ["book", "booking", "appointment", "schedule", "visit"],
        "reply": "Booking is simple. Share your location, pest/problem type, and preferred date. You can use our Request Quote page or WhatsApp for faster coordination.",
    },
    {
        "keywords": ["price", "cost", "quote", "how much", "charges"],
        "reply": "Pricing depends on pest type, infestation level, property size, and treatment frequency. We usually confirm cost after inspection to keep pricing fair and accurate.",
    },
    {
        "keywords": ["safe", "safety", "child", "children", "pet", "pets", "toxic"],
        "reply": "Safety is our priority. We use controlled methods, PPE, and clear re-entry guidance. We also provide MSDS where required and avoid risky indoor liquid overuse.",
    },
    {
        "keywords": ["weed", "herbicide", "lawn", "broadleaf", "perennial"],
        "reply": "Our weed management covers lawns, pavements, open grounds, agricultural, and industrial spaces. We target broadleaf, annual, and perennial weeds with planned application cycles.",
    },
    {
        "keywords": ["disinfection", "cleaning", "sanitize", "sanitization", "covid"],
        "reply": "We provide post-construction cleaning, high-touch disinfection, and deep sanitization for schools, clinics, offices, and commercial spaces.",
    },
    {
        "keywords": ["chemical", "rodenticide", "insecticide", "toilet", "odor"],
        "reply": "We supply ready-to-use chemical solutions, including rodenticides, herbicides, insecticides, pit toilet chemicals, and odor-control solutions.",
    },
    {
        "keywords": ["season", "summer", "fall", "winter", "spring"],
        "reply": "We run seasonal programs: Summer (insect/rodent control), Fall (preventive treatment), Winter (indoor monitoring), and Spring (weed control and pest barriers).",
    },
    {
        "keywords": ["response", "urgent", "emergency", "fast"],
        "reply": "Urgent infestations are prioritized. Share your area and issue now, and we will guide the fastest available response window.",
    },
    {
        "keywords": ["preparation", "prepare", "before service", "before treatment"],
        "reply": "Before service: clear food surfaces, secure utensils, reduce clutter around treatment points, and keep children/pets away from active treatment zones.",
    },
    {
        "keywords": ["after treatment", "after service", "follow up", "warranty", "guarantee"],
        "reply": "After treatment, follow re-entry and hygiene guidance. We provide follow-up monitoring and prevention recommendations to reduce re-infestation risk.",
    },
    {
        "keywords": ["school", "clinic", "institution", "government", "commercial"],
        "reply": "Yes, we serve homes, businesses, schools, clinics, and government institutions with tailored treatment and reporting structures.",
    },
]


def _normalize(text):
    cleaned = re.sub(r"\s+", " ", text.strip().lower())
    return cleaned


def _keyword_score(text, keywords):
    score = 0
    for keyword in keywords:
        if keyword in text:
            score += 1
    return score


def _pest_profile_match(text):
    best_profile = None
    best_score = 0
    for profile in PEST_PROFILES:
        score = _keyword_score(text, profile["aliases"])
        if score > best_score:
            best_score = score
            best_profile = profile
    return best_profile if best_score > 0 else None


def _intent_match(text):
    best_reply = None
    best_score = 0
    for rule in INTENT_RULES:
        score = _keyword_score(text, rule["keywords"])
        if score > best_score:
            best_score = score
            best_reply = rule["reply"]
    return best_reply if best_score > 0 else None


def generate_helpdesk_reply(message, contact_info):
    text = _normalize(message)
    if not text:
        return (
            "Please type your question and I will help immediately.",
            CHATBOT_DEFAULT_SUGGESTIONS,
        )

    if any(word in text for word in ["hello", "hi", "hey", "good morning", "good afternoon", "good evening"]):
        return (
            "Hello, welcome to Smart Pest Solutions. How can I help you today with pest control, weed management, cleaning, or chemical products?",
            CHATBOT_DEFAULT_SUGGESTIONS,
        )

    if any(word in text for word in ["thank you", "thanks", "appreciate"]):
        return (
            "You are welcome. If you want, I can also help you prepare for inspection or create a quick service request checklist.",
            ["Inspection checklist", "Service preparation guide", "Request a quote"],
        )

    if any(word in text for word in ["poison", "swallowed", "ingested", "emergency health", "reaction"]):
        return (
            "If there is exposure or a severe reaction, please seek urgent medical help immediately. Then contact us so we can provide product safety details and incident support.",
            ["Call emergency services", "Request MSDS", "Contact Smart Pest now"],
        )

    pest_profile = _pest_profile_match(text)
    if pest_profile:
        reply = (
            f"{pest_profile['title']}: Signs: {pest_profile['signs']} "
            f"Risks: {pest_profile['risks']} Prevention: {pest_profile['prevention']} "
            f"Our approach: {pest_profile['treatment']}"
        )
        return (
            reply,
            ["How much will treatment cost?", "How long does treatment take?", "Book inspection"],
        )

    intent_reply = _intent_match(text)
    if intent_reply:
        return (
            intent_reply,
            ["Request a quote", "Talk on WhatsApp", "View services"],
        )

    fallback = (
        "I can help with pest identification, treatment options, safety, preparation, follow-up, and pricing guidance. "
        f"For direct support, call {contact_info['phone_display']} or WhatsApp {contact_info['whatsapp_display']}."
    )
    return (fallback, CHATBOT_DEFAULT_SUGGESTIONS)
