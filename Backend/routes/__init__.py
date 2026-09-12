from routes.transcription import transcription_bp
from routes.sentences import sentences_bp
from routes.recordings import recordings_bp
from routes.songs import songs_bp
from routes.stutter import stutter_bp
from routes.reports import reports_bp


def register_blueprints(app):
    app.register_blueprint(transcription_bp)
    app.register_blueprint(sentences_bp)
    app.register_blueprint(recordings_bp)
    app.register_blueprint(songs_bp)
    app.register_blueprint(stutter_bp)
    app.register_blueprint(reports_bp)
