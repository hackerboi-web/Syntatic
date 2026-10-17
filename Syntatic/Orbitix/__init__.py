from flask import Blueprint
from groq import Groq
from .config import GROQ_API_KEY

client = Groq(api_key=GROQ_API_KEY)
orbitix_bp = Blueprint("orbitix", __name__, template_folder="../templates", static_folder="../static")

from . import routes  # noqa
""" filePath">
/workspace/app/Syntatic/Orbitix/__init__.py