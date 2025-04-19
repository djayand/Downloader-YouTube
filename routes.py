import os
import shutil
from uuid import uuid4
from flask import request, render_template, session, redirect, url_for, flash, send_file, jsonify

from utils import is_valid_url, download_youtube, add_album_art

# Stockage temporaire des statuts de tâches
tasks_status = {}

def register_routes(app, download_folder):
    """
    Fonction à appeler dans main.py pour enregistrer toutes les routes Flask.
    """

    def update_status(task_id, status, message):
        """
        Met à jour le dictionnaire global de suivi des tâches.
        """
        tasks_status[task_id] = {'status': status, 'message': message}

    @app.route('/', methods=['GET', 'POST'])
    def index():
        """
        Gère la page d'accueil avec le formulaire.
        En POST, traite le téléchargement et retourne un task_id.
        """
        if request.method == 'POST':
            task_id = str(uuid4())
            update_status(task_id, 'processing', 'Préparation du téléchargement...')

            url = request.form.get('url')
            format_choice = request.form.get('format')

            if not url or not is_valid_url(url):
                update_status(task_id, 'error', "URL YouTube invalide.")
                return jsonify({'task_id': task_id})

            def callback(status, message):
                update_status(task_id, status, message)

            downloaded_file = download_youtube(url, format_choice, download_folder, callback)
            if downloaded_file and os.path.isfile(downloaded_file):
                if format_choice == "mp3":
                    add_album_art(downloaded_file, downloaded_file.replace(".mp3", ".jpg"), callback)

                session['download_file'] = downloaded_file
                update_status(task_id, 'success', "Fichier généré avec succès !")
            else:
                update_status(task_id, 'error', "Le fichier n'a pas pu être généré.")

            return jsonify({'task_id': task_id})

        return render_template('index.html', download_file=session.get('download_file'))

    @app.route('/status/<task_id>')
    def task_status(task_id):
        """
        Fournit à l'AJAX le statut d'une tâche en cours (succès, erreur, en cours...).
        """
        return jsonify(tasks_status.get(task_id, {'status': 'unknown', 'message': 'Tâche introuvable'}))

    @app.route('/download')
    def download():
        """
        Envoie le fichier généré à l'utilisateur et nettoie la session.
        """
        file_path = session.get('download_file')
        if file_path and os.path.isfile(file_path):
            session.pop('download_file', None)
            return send_file(file_path, as_attachment=True)

        flash("Erreur : Le fichier n'est plus disponible.", "error")
        return redirect(url_for('index'))

    @app.route('/clear')
    def clear():
        """
        Supprime tous les fichiers temporaires générés par le serveur.
        """
        try:
            shutil.rmtree(download_folder)
            os.makedirs(download_folder, exist_ok=True)
            session.pop('download_file', None)
            flash("Tous les fichiers temporaires ont été supprimés.", "success")
        except Exception as e:
            flash(f"Erreur lors du nettoyage : {str(e)}", "error")
        return redirect(url_for('index'))
import os
import shutil
from uuid import uuid4
from flask import request, render_template, session, redirect, url_for, flash, send_file, jsonify

from utils import is_valid_url, download_youtube, add_album_art

# Stockage temporaire des statuts de tâches
tasks_status = {}

def register_routes(app, download_folder):
    """
    Fonction à appeler dans main.py pour enregistrer toutes les routes Flask.
    """

    def update_status(task_id, status, message):
        """
        Met à jour le dictionnaire global de suivi des tâches.
        """
        tasks_status[task_id] = {'status': status, 'message': message}

    @app.route('/', methods=['GET', 'POST'])
    def index():
        """
        Gère la page d'accueil avec le formulaire.
        En POST, traite le téléchargement et retourne un task_id.
        """
        if request.method == 'POST':
            task_id = str(uuid4())
            update_status(task_id, 'processing', 'Préparation du téléchargement...')

            url = request.form.get('url')
            format_choice = request.form.get('format')

            if not url or not is_valid_url(url):
                update_status(task_id, 'error', "URL YouTube invalide.")
                return jsonify({'task_id': task_id})

            def callback(status, message):
                update_status(task_id, status, message)

            downloaded_file = download_youtube(url, format_choice, download_folder, callback)
            if downloaded_file and os.path.isfile(downloaded_file):
                if format_choice == "mp3":
                    add_album_art(downloaded_file, downloaded_file.replace(".mp3", ".jpg"), callback)

                session['download_file'] = downloaded_file
                update_status(task_id, 'success', "Fichier généré avec succès !")
            else:
                update_status(task_id, 'error', "Le fichier n'a pas pu être généré.")

            return jsonify({'task_id': task_id})

        return render_template('index.html', download_file=session.get('download_file'))

    @app.route('/status/<task_id>')
    def task_status(task_id):
        """
        Fournit à l'AJAX le statut d'une tâche en cours (succès, erreur, en cours...).
        """
        return jsonify(tasks_status.get(task_id, {'status': 'unknown', 'message': 'Tâche introuvable'}))

    @app.route('/download')
    def download():
        """
        Envoie le fichier généré à l'utilisateur et nettoie la session.
        """
        file_path = session.get('download_file')
        if file_path and os.path.isfile(file_path):
            session.pop('download_file', None)
            return send_file(file_path, as_attachment=True)

        flash("Erreur : Le fichier n'est plus disponible.", "error")
        return redirect(url_for('index'))

    @app.route('/clear')
    def clear():
        """
        Supprime tous les fichiers temporaires générés par le serveur.
        """
        try:
            shutil.rmtree(download_folder)
            os.makedirs(download_folder, exist_ok=True)
            session.pop('download_file', None)
            flash("Tous les fichiers temporaires ont été supprimés.", "success")
        except Exception as e:
            flash(f"Erreur lors du nettoyage : {str(e)}", "error")
        return redirect(url_for('index'))
