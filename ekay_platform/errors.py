from flask import render_template, request, jsonify
from . import db

def page_not_found(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Not found'})
        response.status_code = 404
        return response
    return render_template('errors/404.html'), 404

def internal_server_error(e):
    db.session.rollback()
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Internal server error'})
        response.status_code = 500
        return response
    return render_template('errors/500.html'), 500

def forbidden(e):
    if request.accept_mimetypes.accept_json and not request.accept_mimetypes.accept_html:
        response = jsonify({'error': 'Forbidden'})
        response.status_code = 403
        return response
    return render_template('errors/403.html'), 403

def bad_request(message):
    response = jsonify({'error': 'Bad request', 'message': message})
    response.status_code = 400
    return response

def unauthorized(message):
    response = jsonify({'error': 'Unauthorized', 'message': message})
    response.status_code = 401
    return response

def validation_error(message):
    return bad_request(message)
