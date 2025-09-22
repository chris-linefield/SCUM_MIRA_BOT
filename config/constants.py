# Rôles Discord
import discord

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
    "Car_Repair_Kit": 2500,
    "Gasoline_Canister": 2500,
    "Big_Vehicle_StorageRack": 7600,
    "Medium_Vehicle_StorageRack": 4400,
    "Small_Vehicle_StorageRack": 2640,
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
    "BPC_WolfsWagen": 4800,
    "BPC_Laika": 4400,
    "BPC_Rager": 7200,
    "BPC_RIS": 2800,
    "BPC_Tractor": 2800,
    "BPC_Cruiser": 2560,
    "BPC_Dirtbike": 2000,
    # Superette
    "Sewing_kit": 480,
    # Packs
    "pack_blindage_leger_rager": 25000,
    "pack_blindage_leger_volkswagen": 15000,
    "pack_blindage_leger_laika": 15000,
    "pack_quad_basic": 5000,
    "pack_blindage_lourd_rager": 50000,
    "pack_blindage_lourd_volkswagen": 35000,
    "pack_blindage_lourd_laika": 35000,
    "pack_blindage_lourd_tracteur": 25000,
    "pack_quad_militaire": 15000,
}

# Items par métier
METIER_ITEMS = {
    "garage": {
        "materials": ["Car_Repair_Kit", "Gasoline_Canister", "Big_Vehicle_StorageRack", "Medium_Vehicle_StorageRack", "Small_Vehicle_StorageRack"],
        "vehicles": ["BPC_WolfsWagen", "BPC_Laika", "BPC_Rager", "BPC_RIS", "BPC_Tractor"],
        "packs": [
            "pack_blindage_leger_rager",
            "pack_blindage_leger_volkswagen",
            "pack_blindage_leger_laika",
            "pack_quad_basic",
            "pack_blindage_lourd_rager",
            "pack_blindage_lourd_volkswagen",
            "pack_blindage_lourd_laika",
            "pack_blindage_lourd_tracteur",
            "pack_quad_militaire"
        ],
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

# Positions de livraison par marchand (À REMPLACER PAR LES TUES)
MERCHANT_DELIVERY_POSITIONS = {
    "garage": (-41297.051, -121472.367, 35180.148),
    "moto": (-41297.051, -121472.367, 35180.148),
    "armurerie": (123456.789, -654321.0, 0),  # Remplace par les vraies coordonnées
    "quincaillerie": (123456.789, -654321.0, 0),  # Remplace par les vraies coordonnées
    "restaurateur": (123456.789, -654321.0, 0),  # Remplace par les vraies coordonnées
    "superette": (123456.789, -654321.0, 0)  # Remplace par les vraies coordonnées
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
INSTANT_VEHICLE_POSITION = (-46050.273, -119181.414, 32178.090)

# Délai de livraison (20 minutes)
DELIVERY_TIME = 20 * 60

# Liste des items par pack
PACK_ITEMS = {
    "pack_blindage_leger_rager": [
        "Rager_Body_ArmorLight_Back_Item", "Rager_Body_ArmorLight_Left_Item", "Rager_Body_ArmorLight_Right_Item",
        "Rager_Body_ArmorLight_Top_Item", "Rager_Door_ArmorLight_BackLeft_Item", "Rager_Door_ArmorLight_BackRight_Item",
        "Rager_Door_ArmorLight_FrontLeft_Item", "Rager_Door_ArmorLight_FrontRight_Item", "Rager_DoorTrunk_ArmorLight_Item",
        "Rager_Wheel_ArmorLight_FrontLeft_Item", "Rager_Wheel_ArmorLight_FrontRight_Item"
    ],
    "pack_blindage_leger_volkswagen": [
        "WW_Bumper_Armor_Back_Item", "WW_Door_ArmorLight_BackLeft_Item", "WW_Door_ArmorLight_BackRight_Item",
        "WW_Door_ArmorLight_FrontLeft_Item", "WW_Door_ArmorLight_FrontRight_Item", "WW_DoorTrunk_ArmorLight_Item"
    ],
    "pack_blindage_leger_laika": [
        "Laika_Bumper_Armor_Back_Item", "Laika_Door_ArmorLight_FrontLeft_Item", "Laika_Door_ArmorLight_FrontRight_Item",
        "Laika_Body_ArmorLight_Top", "Laika_Body_ArmorLight_Left", "Laika_Body_ArmorLight_Right", "Laika_DoorTrunk_ArmorLight_Item"
    ],
    "pack_quad_basic": [
        "RIS_Bars_Civilian_Back_Item", "RIS_Bars_Civilian_Front_Item", "RIS_Hand_Guards_Civilian_Item", "RIS_Plow_Civilian"
    ],
    "pack_blindage_lourd_rager": [
        "Rager_Body_ArmorHeavy_Back_Item", "Rager_Body_ArmorHeavy_Left_Item", "Rager_Body_ArmorHeavy_Right_Item",
        "Rager_Body_ArmorHeavy_Top_Item", "Rager_Door_ArmorHeavy_BackLeft_Item", "Rager_Door_ArmorHeavy_BackRight_Item",
        "Rager_Door_ArmorHeavy_FrontLeft_Item", "Rager_Door_ArmorHeavy_FrontRight_Item", "Rager_DoorTrunk_ArmorHeavy_Item",
        "Rager_Wheel_ArmorLight_FrontLeft_Item", "Rager_Wheel_ArmorLight_FrontRight_Item"
    ],
    "pack_blindage_lourd_volkswagen": [
        "WW_Bumper_Armor_Back_Item", "WW_Door_ArmorHeavy_BackLeft_Item", "WW_Door_ArmorHeavy_BackRight_Item",
        "WW_Door_ArmorHeavy_FrontLeft_Item", "WW_Door_ArmorHeavy_FrontRight_Item", "WW_Body_ArmorHeavy_Top_Item",
        "WW_DoorTrunk_ArmorHeavy_Item", "WW_Wheel_ArmorLight_FrontLeft_Item", "WW_Wheel_ArmorLight_FrontRight_Item"
    ],
    "pack_blindage_lourd_laika": [
        "Laika_Bumper_Armor_Back_Item", "Laika_Door_ArmorHeavy_FrontLeft_Item", "Laika_Door_ArmorHeavy_FrontRight_Item",
        "Laika_Body_ArmorHeavy_Top_Item", "Laika_Body_ArmorHeavy_Left", "Laika_Body_ArmorHeavy_Right", "Laika_DoorTrunk_ArmorHeavy_Item"
    ],
    "pack_blindage_lourd_tracteur": [
        "Tractor_Body_Left_ArmorHeavy_Item", "Tractor_Body_Right_ArmorHeavy_Item", "Tractor_Body_Top_ArmorHeavy_Back_Item",
        "Tractor_Body_Top_ArmorHeavy_Front_Item", "Tractor_Body_Top_ArmorHeavy_Left_Item", "Tractor_Body_Top_ArmorHeavy_Right_Item",
        "Tractor_Door_Left_ArmorHeavy_Item", "Tractor_Door_Right_ArmorHeavy_Item", "Tractor_WheelArmorHeavy_Front_Item", "Tractor_WheelArmorHeavy_Front_Item"
    ],
    "pack_quad_militaire": [
        "RIS_Armor_Military_Front_Item", "RIS_Body_Military_Item", "RIS_Hand_Guards_Civilian_Item", "RIS_Spikes_Military", "RIS_Wheel_Armor_Item"
    ],
}