from flask import Blueprint

guru_bp = Blueprint('guru', __name__, template_folder='../../templates/guru')

from app.blueprints.guru import routes
