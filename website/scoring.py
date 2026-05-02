from flask import Blueprint, render_template, request, redirect, url_for, jsonify
from flask_login import login_required, current_user
from website.models import ScoringSystem, FeedGroup, ArticleScore
from website import db
from website.llm import improve_scoring_prompt

scoring_bp = Blueprint('scoring', __name__)


@scoring_bp.route('/scoring')
@login_required
def scoring_list():
    default = ScoringSystem.query.filter_by(is_default=True).first()
    user_systems = ScoringSystem.query.filter_by(owner_id=current_user.id).all()
    return render_template('scoring.html', user=current_user, default=default, user_systems=user_systems)


@scoring_bp.route('/scoring/create', methods=['POST'])
@login_required
def create_scoring():
    name = request.form.get('name', '').strip()
    prompt = request.form.get('prompt', '').strip()
    if name and prompt:
        system = ScoringSystem(name=name, prompt=prompt, owner_id=current_user.id, is_default=False)
        db.session.add(system)
        db.session.commit()
    return redirect(url_for('scoring.scoring_list'))


@scoring_bp.route('/scoring/<int:system_id>/update', methods=['POST'])
@login_required
def update_scoring(system_id):
    system = ScoringSystem.query.filter_by(id=system_id, owner_id=current_user.id).first()
    if system:
        name = request.form.get('name', '').strip()
        prompt = request.form.get('prompt', '').strip()
        if name:
            system.name = name
        if prompt:
            system.prompt = prompt
        db.session.commit()
    return redirect(url_for('scoring.scoring_list'))


@scoring_bp.route('/scoring/<int:system_id>/delete', methods=['POST'])
@login_required
def delete_scoring(system_id):
    system = ScoringSystem.query.filter_by(id=system_id, owner_id=current_user.id).first()
    if system:
        # Detach from any feedgroups before deletion
        FeedGroup.query.filter_by(scoring_system_id=system_id).update(
            {'scoring_system_id': None}, synchronize_session='fetch'
        )
        db.session.delete(system)
        db.session.commit()
    return redirect(url_for('scoring.scoring_list'))


@scoring_bp.route('/scoring/improve', methods=['POST'])
@login_required
def improve_prompt():
    data = request.get_json()
    prompt = (data or {}).get('prompt', '').strip()
    if not prompt:
        return jsonify({'error': 'No prompt provided'}), 400
    try:
        improved = improve_scoring_prompt(prompt)
        return jsonify({'improved': improved})
    except Exception as e:
        return jsonify({'error': str(e)}), 500
