import os
import shutil

from uuid import uuid4
from threading import Thread
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
        Met à jour le dictionnaire global de suivi des tâches avec un log complet.
        """
        if task_id not in tasks_status:
            tasks_status[task_id] = {'status': 'processing', 'log': []}

        tasks_status[task_id]['status'] = status
        tasks_status[task_id]['log'].append(message)

    def handle_download(task_id, url, format_choice):
        """
        Fonction de traitement du téléchargement à exécuter dans un thread séparé.
        """
        def callback(status, message):
            update_status(task_id, status, message)

        downloaded_file = download_youtube(url, format_choice, download_folder, callback)

        if downloaded_file and os.path.isfile(downloaded_file):
            if format_choice == "mp3":
                callback("processing", "🖼 Ajout de la miniature MP3...")
                add_album_art(downloaded_file, downloaded_file.replace(".mp3", ".jpg"), callback)

            tasks_status[task_id]['file_path'] = downloaded_file
            update_status(task_id, 'success', "✅ Fichier prêt au téléchargement !")
        else:
            update_status(task_id, 'error', "❌ Le fichier n'a pas pu être généré.")

    @app.route('/', methods=['GET', 'POST'])
    def index():
        """
        Gère la page d'accueil avec le formulaire.
        En POST, déclenche le thread de téléchargement et retourne un task_id.
        """
        if request.method == 'POST':
            task_id = str(uuid4())
            update_status(task_id, 'processing', '🛠 Préparation du téléchargement...')

            url = request.form.get('url')
            format_choice = request.form.get('format')

            if not url or not is_valid_url(url):
                update_status(task_id, 'error', "❌ URL YouTube invalide.")
                return jsonify({'task_id': task_id})

            # Lancer le traitement dans un thread
            thread = Thread(target=handle_download, args=(task_id, url, format_choice))
            thread.start()

            return jsonify({'task_id': task_id})

        return render_template('index.html', download_file=session.get('download_file'))

    @app.route('/status/<task_id>')
    def task_status(task_id):
        """
        Fournit à l'AJAX le statut d'une tâche en cours avec l'historique complet.
        """
        task = tasks_status.get(task_id)
        if task:
            return jsonify({
                'status': task['status'],
                'log': task['log']
            })
        else:
            return jsonify({
                'status': 'unknown',
                'log': ['❓ Tâche introuvable']
            })

    @app.route('/download', endpoint='download')
    def download():
        """
        Envoie le fichier généré à l'utilisateur et nettoie la session.
        """
        task_id = request.args.get("task_id")
        file_path = tasks_status.get(task_id, {}).get('file_path')

        if file_path and os.path.isfile(file_path):
            session.pop('download_file', None)
            return send_file(file_path, as_attachment=True)

        flash("❌ Erreur : Le fichier n'est plus disponible.", "error")
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
            flash("✅ Tous les fichiers temporaires ont été supprimés.", "success")
        except Exception as e:
            flash(f"❌ Erreur lors du nettoyage : {str(e)}", "error")
        return redirect(url_for('index'))