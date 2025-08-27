import discord

DELIVERY_POSITIONS = {
    "A4 - Croisement des pistes": (359517.538, -528322.718, 0),
    "Z0 - Piste devant hangar": (-754535.977, -678349.9049, 0),
    "B2 - Début de piste": (-198424.2325, -31863.4466, 0),
    "Z4 - Piste proche bunker": (437363.6906, 560133.7958, 0)
}

# Prix des items
ITEM_PRICES = {
    # Garage auto/moto
    "Car_Repair_Kit": 2000,
    "Gasoline_Canister": 1500,

    # Armurerie
    "Grinding_Stone_02": 3000,
    "Weapon_Cleaning_Kit": 5200,

    # Quincaillerie
    "Tool_Box_Small": 1000,
    "Tool_Box": 2500,
    "Screwdriver": 5000,
    "Lockpick_Item": 5000,

    # Restaurateur
    "VegetableOil": 800,
    "Vinegar": 500,

    # Superette
    "Sewing_kit": 480
}

# Items par métier
METIER_ITEMS = {
    "garage": ["Car_Repair_Kit", "Gasoline_Canister"],
    "moto": ["Car_Repair_Kit", "Gasoline_Canister"],
    "armurerie": ["Grinding_Stone_02", "Weapon_Cleaning_Kit"],
    "quincaillerie": ["Tool_Box_Small", "Tool_Box", "Screwdriver", "Lockpick_Item"],
    "restaurateur": ["VegetableOil", "Vinegar"],
    "superette": ["Sewing_kit"]
}

# Rôles
ROLES = {
    "garage": 1405192378066796606,
    "armurerie": 1405501043684545556,
    "moto": 1406507024082276435,
    "quincaillerie": 1405501176786583593,
    "restaurateur": 1405501264187625533,
    "superette": 1405501210110332988
}

# Canaux
CHANNELS = {
    "garage": 1405480822462742549,
    "armurerie": 1405481980761477141,
    "moto": 1405480904893403186,
    "quincaillerie": 1405504539867742208,
    "restaurateur": 1405505475574759534,
    "superette": 1406507683137327224
}

# Messages d'annonce
ANNOUNCE_MESSAGES = {
    "garage": {
        "open": "Ouverture du Garage, venez nombreux !",
        "close": "Le Garage ferme ses portes, à bientôt !"
    },
    "armurerie": {
        "open": "Ouverture de l'Armurerie, venez vous équiper !",
        "close": "L'Armurerie ferme ses portes, à bientôt !"
    },
    "moto": {
        "open": "Ouverture du Magasin de Motos, venez faire un tour !",
        "close": "Le Magasin de Motos ferme, à demain !"
    },
    "quincaillerie": {
        "open": "Ouverture de la Quincaillerie, outils et matériaux disponibles !",
        "close": "La Quincaillerie ferme, bon bricolage !"
    },
    "restaurateur": {
        "open": "Ouverture du Restaurant, venez vous restaurer !",
        "close": "Le Restaurant ferme, bon appétit !"
    },
    "superette": {
        "open": "Ouverture de la Superette, faites vos courses !",
        "close": "La Superette ferme, à demain !"
    }
}

# Noms des métiers
METIER_NAMES = {
    "garage": "Garage",
    "armurerie": "Armurerie",
    "moto": "Magasin de Motos",
    "quincaillerie": "Quincaillerie",
    "restaurateur": "Restaurant",
    "superette": "Superette"
}

# Couleurs pour les embeds
METIER_COLORS = {
    "garage": discord.Color.dark_gold(),
    "armurerie": discord.Color.dark_red(),
    "moto": discord.Color.dark_blue(),
    "quincaillerie": discord.Color.dark_orange(),
    "restaurateur": discord.Color.green(),
    "superette": discord.Color.purple()
}

# Constantes supplémentaires
MAX_QUANTITY = 20
DELIVERY_TIME = 20 * 60
ANNOUNCE_DELAY = 5 * 60

STORM_TIMES = ["00:55", "06:55", "12:55", "18:55"]
STORM_ANNOUNCE_MESSAGE = "Réinitialisation BCU dans 5 minutes."
STATUS_CHANNEL_ID = 1407804333281640508
