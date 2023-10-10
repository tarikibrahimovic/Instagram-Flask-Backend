from flask_jwt_extended import get_jwt_identity

import models
from flask import jsonify, request
from cloudinary.uploader import upload as cloudinary_upload
from os import abort

from db import db


def get_notifications():
    user_id = get_jwt_identity()
    return None
