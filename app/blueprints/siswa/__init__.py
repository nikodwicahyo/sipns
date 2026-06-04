from flask import Blueprint

siswa_bp = Blueprint('siswa', __name__, template_folder='../../templates/siswa')

from app.blueprints.siswa import routes
