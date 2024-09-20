''' Custom routes for the application. '''

from flask import Blueprint, render_template

custom_bp = Blueprint('custom', __name__)

@custom_bp.route('/registro_personal', methods=['GET', 'POST'])
def register_personal():
    ''' Renders the personal registration page. '''
    return render_template('')
