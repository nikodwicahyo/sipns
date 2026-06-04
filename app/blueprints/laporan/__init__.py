from flask import Blueprint

laporan_bp = Blueprint('laporan', __name__, template_folder='../../templates/laporan')

from app.blueprints.laporan import routes
