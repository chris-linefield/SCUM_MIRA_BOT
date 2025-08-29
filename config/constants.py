import discord

# Rôles Discord
ROLES = {
    "garage": 1405192378066796606,
    "armurerie": 1405501043684545556,
    "moto": 1406507024082276435,
    "quincaillerie": 1405501176786583593,
    "restaurateur": 1405501264187625533,
    "superette": 1405501210110332988,
}

# Rôles administrateurs
ADMIN_ROLES = [
    1391037447470710875,
    1390041557092143114,
    1404135876367355945,
]

# Canaux Discord
CHANNELS = {
    "garage": 1405480822462742549,
    "armurerie": 1405481980761477141,
    "moto": 1405480904893403186,
    "quincaillerie": 1405504539867742208,
    "restaurateur": 1405505475574759534,
    "superette": 1406507683137327224,
    "admin_panel": 1393821678072631346,
    "status": 1407804333281640508,
}

# Canal d'inscription
REGISTRATION_CHANNEL_ID = 1405516212854722691

# Prix des items
ITEM_PRICES = {
    # Garage
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
    # Véhicules
    "BP_Cruiser_B": 20000,
    "BP_Dirtbike_A": 30000,
    # Superette
    "Sewing_kit": 480,
}

# Items par métier
METIER_ITEMS = {
    "garage": ["Car_Repair_Kit", "Gasoline_Canister", "BP_Cruiser_B"],
    "moto": ["Car_Repair_Kit", "Gasoline_Canister", "BP_Dirtbike_A"],
    "armurerie": ["Grinding_Stone_02", "Weapon_Cleaning_Kit"],
    "quincaillerie": ["Tool_Box_Small", "Tool_Box", "Screwdriver", "Lockpick_Item"],
    "restaurateur": ["VegetableOil", "Vinegar"],
    "superette": ["Sewing_kit"]
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

# Délais
DELAY_BETWEEN_ACTIONS = 3  # Secondes entre chaque action pyautogui
MAX_QUANTITY = 20