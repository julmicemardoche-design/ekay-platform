"""
E-KAY Platform - User Blueprint
Copyright (c) 2025 Walny Mardoché JULMICE. All Rights Reserved.

This software is proprietary and confidential.
Unauthorized copying, distribution, or use is strictly prohibited.
Contact: julmicemardoche@gmail.com
"""

from flask import Blueprint

bp = Blueprint('user', __name__)

from . import routes
