from flask_jwt_extended import get_jwt_identity

import models
from flask import jsonify, request
from cloudinary.uploader import upload as cloudinary_upload
from db import db
from os import abort
from sqlalchemy import and_


def post():
    user_id = get_jwt_identity()['user_id']
    title = request.form.get('caption')
    file = request.files['file']
    if file:
        result = cloudinary_upload(file)
        image_url = result['secure_url']
    try:
        post = models.PostModel(user_id=user_id, title=title, image_url=image_url)
        post.save_to_db()
    except Exception as e:
        abort(500, message=str(e))
    return jsonify({"message": "Post created."}), 201
