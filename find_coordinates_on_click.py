from pynput import mouse
import sys

def on_click(x, y, button, pressed):
    if button == mouse.Button.left and pressed:
        print(f"Clique gauche : X={x}, Y={y}")
    elif button == mouse.Button.right and pressed:
        print("\nArrêt du script (clic droit).")
        return False  # Arrête l'écoute

# Configuration du listener
with mouse.Listener(on_click=on_click) as listener:
    print("Déplace ta souris et CLIQUE GAUCHE pour afficher les coordonnées.")
    print("CLIQUE DROIT pour arrêter le script.\n")
    listener.join()
