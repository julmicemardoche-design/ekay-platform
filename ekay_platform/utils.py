"""
E-KAY Platform - Utilitaires
"""
import os
from PIL import Image, ExifTags
import uuid
from werkzeug.utils import secure_filename
from flask import current_app

def allowed_file(filename, allowed_extensions=None):
    """Vérifie si l'extension du fichier est autorisée"""
    if allowed_extensions is None:
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
    return '.' in filename and \
           filename.rsplit('.', 1)[1].lower() in allowed_extensions

def get_secure_filename(filename):
    """Génère un nom de fichier sécurisé et unique"""
    ext = filename.rsplit('.', 1)[1].lower()
    return f"{uuid.uuid4().hex}.{ext}"

def get_upload_path(subfolder, filename):
    """Génère le chemin de téléchargement pour un fichier"""
    upload_dir = os.path.join(current_app.config['UPLOAD_FOLDER'], subfolder)
    os.makedirs(upload_dir, exist_ok=True)
    return os.path.join(upload_dir, filename)

def process_image(file, max_size=(1200, 1200), quality=85):
    """
    Traite une image : redimensionnement, rotation et optimisation
    Retourne un tuple (image, width, height)
    """
    try:
        img = Image.open(file.stream)
        
        # Vérifier et corriger l'orientation de l'image
        try:
            for orientation in ExifTags.TAGS.keys():
                if ExifTags.TAGS[orientation] == 'Orientation':
                    break
            
            exif = img._getexif()
            if exif is not None:
                exif = dict(exif.items())
                if orientation in exif:
                    if exif[orientation] == 3:
                        img = img.rotate(180, expand=True)
                    elif exif[orientation] == 6:
                        img = img.rotate(270, expand=True)
                    elif exif[orientation] == 8:
                        img = img.rotate(90, expand=True)
        except (AttributeError, KeyError, IndexError):
            # Ne pas s'inquiéter si l'image n'a pas d'EXIF
            pass
        
        # Convertir en RGB si nécessaire (pour les PNG avec transparence)
        if img.mode in ('RGBA', 'LA'):
            background = Image.new('RGB', img.size, (255, 255, 255))
            background.paste(img, mask=img.split()[-1])
            img = background
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        # Redimensionner l'image si elle est trop grande
        img.thumbnail(max_size, Image.Resampling.LANCZOS)
        
        return img, img.size[0], img.size[1]
    except Exception as e:
        current_app.logger.error(f"Erreur lors du traitement de l'image: {e}")
        raise

def save_property_image(file, property_id):
    """
    Enregistre une image pour une propriété et crée des miniatures
    Retourne un dictionnaire avec les informations sur l'image
    """
    if not file or not allowed_file(file.filename):
        return None
    
    try:
        # Créer le répertoire de destination s'il n'existe pas
        upload_dir = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'properties',
            str(property_id)
        )
        os.makedirs(upload_dir, exist_ok=True)
        
        # Générer un nom de fichier unique
        ext = file.filename.rsplit('.', 1)[1].lower()
        filename = f"{uuid.uuid4().hex}.{ext}"
        
        # Traiter et sauvegarder l'image originale
        img, width, height = process_image(file)
        original_path = os.path.join(upload_dir, f"original_{filename}")
        img.save(original_path, 'JPEG', quality=90, optimize=True)
        
        # Créer et sauvegarder la version principale (large)
        main_img = img.copy()
        main_img.thumbnail((1200, 900), Image.Resampling.LANCZOS)
        main_path = os.path.join(upload_dir, filename)
        main_img.save(main_path, 'JPEG', quality=85, optimize=True)
        
        # Créer et sauvegarder la version moyenne
        medium_img = img.copy()
        medium_img.thumbnail((800, 600), Image.Resampling.LANCZOS)
        medium_path = os.path.join(upload_dir, f"medium_{filename}")
        medium_img.save(medium_path, 'JPEG', quality=85, optimize=True)
        
        # Créer et sauvegarder la miniature
        thumb_img = img.copy()
        thumb_img.thumbnail((300, 200), Image.Resampling.LANCZOS)
        thumb_path = os.path.join(upload_dir, f"thumb_{filename}")
        thumb_img.save(thumb_path, 'JPEG', quality=80, optimize=True)
        
        return {
            'filename': filename,
            'original_filename': secure_filename(file.filename),
            'file_size': os.path.getsize(main_path),
            'content_type': file.content_type,
            'width': width,
            'height': height
        }
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de l'enregistrement de l'image: {e}")
        # Nettoyer les fichiers partiellement enregistrés
        if 'upload_dir' in locals() and os.path.exists(upload_dir):
            for f in os.listdir(upload_dir):
                if f.startswith(os.path.splitext(filename)[0]):
                    try:
                        os.remove(os.path.join(upload_dir, f))
                    except:
                        pass
        return None

def delete_property_images(image):
    """Supprime tous les fichiers associés à une image de propriété"""
    try:
        if not image or not image.filename:
            return False
            
        upload_dir = os.path.join(
            current_app.config['UPLOAD_FOLDER'],
            'properties',
            str(image.property_id)
        )
        
        # Supprimer toutes les variantes de l'image
        base_name = os.path.splitext(image.filename)[0]
        for f in os.listdir(upload_dir):
            if f.startswith(base_name):
                try:
                    os.remove(os.path.join(upload_dir, f))
                except Exception as e:
                    current_app.logger.error(f"Erreur lors de la suppression de {f}: {e}")
        
        # Supprimer le répertoire s'il est vide
        try:
            if not os.listdir(upload_dir):
                os.rmdir(upload_dir)
        except Exception as e:
            current_app.logger.error(f"Erreur lors de la suppression du répertoire {upload_dir}: {e}")
        
        return True
        
    except Exception as e:
        current_app.logger.error(f"Erreur lors de la suppression des images: {e}")
        return False
