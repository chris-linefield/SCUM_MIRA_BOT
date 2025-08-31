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
    "timer": 1407804333281640508,
}

# Canal d'inscription
REGISTRATION_CHANNEL_ID = 1405516212854722691

# Prix des items
ITEM_PRICES = {
    # Garage
    "Car_Repair_Kit": 1,
    "Gasoline_Canister": 1,
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
    "BPC_WolfsWagen": 1,
    "BPC_Cruiser": 1,
    "BPC_Dirtbike": 1,
    # Superette
    "Sewing_kit": 480,
}

# Items par métier
METIER_ITEMS = {
    "garage": {
        "materials": ["Car_Repair_Kit", "Gasoline_Canister"],
        "vehicles": ["BPC_WolfsWagen"]
    },
    "moto": {
        "materials": ["Car_Repair_Kit", "Gasoline_Canister"],
        "vehicles": ["BPC_Cruiser", "BPC_Dirtbike"]
    },
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

# Positions de livraison
DELIVERY_POSITIONS = {
    "A4 - Croisement des pistes": (359517.538, -528322.718, 0),
    "Z0 - Piste devant hangar": (-754535.977, -678349.9049, 0),
    "B2 - Début de piste": (-198424.2325, -31863.4466, 0),
    "Z4 - Piste proche bunker": (437363.6906, 560133.7958, 0)
}

# Positions de livraison par marchand
MERCHANT_DELIVERY_POSITIONS = {
    "garage": (-41297.051, -121472.367, 35180.148),
    "moto": (-41297.051, -121472.367, 35180.148),
    "armurerie": (0, 0, 0),  # À définir
    "quincaillerie": (0, 0, 0),  # À définir
    "restaurateur": (0, 0, 0),  # À définir
    "superette": (0, 0, 0)  # À définir
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

# Position de téléportation pour les véhicules
INSTANT_VEHICLE_POSITION = (-41297.051, -121472.367, 35180.148)

# Délai de livraison (20 minutes)
DELIVERY_TIME = 20 * 60