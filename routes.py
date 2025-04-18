import os
import shutil

from uuid import uuid4
from flask import request, render_template, session, redirect, url_for, flash, send_file, jsonify

from utils import is_valid_url, download_youtube, add_album_art

# Stockage temporaire des statuts de tâches
tasks_status = {}

def register_routes(app, download_folder):
    @app.route('/', methods=['GET', 'POST'])
    def index():
        if request.method == 'POST':
            task_id = str(uuid4())
            tasks_status[task_id] = {'status': 'processing', 'message': 'Téléchargement en cours...'}

            url = request.form.get('url')
            format_choice = request.form.get('format')

            if not url or not is_valid_url(url):
                tasks_status[task_id] = {'status': 'error', 'message': "URL YouTube invalide."}
                return jsonify({'task_id': task_id})

            downloaded_file = download_youtube(url, format_choice, download_folder)
            if downloaded_file and os.path.isfile(downloaded_file):
                if format_choice == "mp3":
                    add_album_art(downloaded_file, downloaded_file.replace(".mp3", ".jpg"))
                session['download_file'] = downloaded_file
                tasks_status[task_id] = {'status': 'success', 'message': "Fichier généré avec succès !"}
            else:
                tasks_status[task_id] = {'status': 'error', 'message': "Le fichier n'a pas pu être généré."}

            return jsonify({'task_id': task_id})

        return render_template('index.html', download_file=session.get('download_file'))

    @app.route('/status/<task_id>')
    def task_status(task_id):
        return jsonify(tasks_status.get(task_id, {'status': 'unknown', 'message': 'Tâche introuvable'}))

    @app.route('/download')
    def download():
        file_path = session.get('download_file')
        if file_path and os.path.isfile(file_path):
            session.pop('download_file', None)
            return send_file(file_path, as_attachment=True)

        flash("Erreur : Le fichier n'est plus disponible.", "error")
        return redirect(url_for('index'))

    @app.route('/clear')
    def clear():
        try:
            shutil.rmtree(download_folder)
            os.makedirs(download_folder, exist_ok=True)
            session.pop('download_file', None)
            flash("Tous les fichiers temporaires ont été supprimés.", "success")
        except Exception as e:
            flash(f"Erreur lors du nettoyage : {str(e)}", "error")
        return redirect(url_for('index'))
