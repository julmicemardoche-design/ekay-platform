import os
import sys

# Ajouter le répertoire du projet au chemin Python
project_root = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, project_root)

# Importer l'application
from ekay_platform import create_app

# Créer l'application
app = create_app()

if __name__ == '__main__':
    # Démarrer le serveur de développement
    app.run(debug=True, host='0.0.0.0', port=5000, ssl_context='adhoc')
