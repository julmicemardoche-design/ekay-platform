import os
from flask import Flask, render_template

# Création de l'application
app = Flask(__name__)

# Configuration de base
app.config['SECRET_KEY'] = 'votre-cle-secrete-tres-longue'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ekay.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Configuration des dossiers
template_dir = os.path.abspath('ekay_platform/templates')
static_dir = os.path.abspath('ekay_platform/static')
app.template_folder = template_dir
app.static_folder = static_dir

# Vérification des dossiers
print("\n[INFO] Dossier des templates:", template_dir)
print("[INFO] Dossier des fichiers statiques:", static_dir)
print("[INFO] Contenu du dossier templates:", os.listdir(template_dir) if os.path.exists(template_dir) else "Dossier non trouvé")

# Route de test
@app.route('/')
def index():
    try:
        # Essayer d'abord avec le template de test
        return render_template('test.html')
    except Exception as e:
        return f"Erreur lors du rendu du template: {str(e)}"

if __name__ == '__main__':
    print("\n" + "="*50)
    print("  DÉMARRAGE DE L'APPLICATION E-KAY")
    print("="*50 + "\n")
    print("Accédez à l'application sur: http://127.0.0.1:5000")
    print("Appuyez sur Ctrl+C pour arrêter le serveur\n")
    
    # Démarrer le serveur
    app.run(host='127.0.0.1', port=5000, debug=True)
