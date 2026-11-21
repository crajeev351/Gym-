import re
from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for, session
from app.models import db, HeroContent, Program, TrainingType, SiteSetting, Lead
from app.forms import BookingForm
from app.rate_limiter import is_rate_limited

public_bp = Blueprint('public', __name__)


def clean_indian_phone(phone_str):
    """Normalize Indian phone number to 10 digits."""
    if not phone_str:
        return ''
    cleaned = re.sub(r'[\s\-\+]', '', phone_str)
    if cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
    return cleaned


@public_bp.route('/', methods=['GET'])
def index():
    hero = HeroContent.query.first()
    programs = Program.query.filter_by(is_active=True).order_by(Program.order_num.asc(), Program.id.asc()).all()
    training_types = TrainingType.query.filter_by(is_active=True).order_by(TrainingType.order_num.asc(), TrainingType.id.asc()).all()
    settings = SiteSetting.query.first()

    form = BookingForm()
    # Populate dropdown choices dynamically from database
    form.fitness_goal.choices = [('', 'Select your fitness goal...')] + [(p.title, p.title) for p in programs]
    form.training_type.choices = [('', 'Select training type...')] + [(t.title, t.title) for t in training_types]

    return render_template(
        'index.html',
        hero=hero,
        programs=programs,
        training_types=training_types,
        settings=settings,
        form=form,
        booking_confirmed=session.pop('booking_confirmed', False)
    )


@public_bp.route('/book', methods=['POST'])
def book():
    is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or \
              'application/json' in request.headers.get('Accept', '')

    # 1. IP Rate Limiting check
    limited, wait_seconds = is_rate_limited(max_requests=5, window_seconds=600)
    if limited:
        err_msg = f"Too many requests from your IP. Please try again in {wait_seconds} seconds."
        if is_ajax:
            return jsonify({'success': False, 'message': err_msg}), 429
        flash(err_msg, 'danger')
        return redirect(url_for('public.index') + '#booking')

    # 2. Hidden Honeypot spam trap
    honeypot_val = request.form.get('honeypot', '').strip()
    if honeypot_val:
        # Silently respond with success to fool bot, without inserting spam lead
        if is_ajax:
            return jsonify({
                'success': True,
                'message': 'Thank you! We will contact you within 24 hours.'
            })
        flash('Thank you! We will contact you within 24 hours.', 'success')
        return redirect(url_for('public.index') + '#booking')

    programs = Program.query.filter_by(is_active=True).order_by(Program.order_num.asc()).all()
    training_types = TrainingType.query.filter_by(is_active=True).order_by(TrainingType.order_num.asc()).all()

    form = BookingForm()
    form.fitness_goal.choices = [('', 'Select your fitness goal...')] + [(p.title, p.title) for p in programs]
    form.training_type.choices = [('', 'Select training type...')] + [(t.title, t.title) for t in training_types]

    if form.validate_on_submit():
        cleaned_phone = clean_indian_phone(form.phone.data)
        ip = request.headers.get('X-Forwarded-For', request.remote_addr or '127.0.0.1')
        if ',' in ip:
            ip = ip.split(',')[0].strip()

        lead = Lead(
            name=form.name.data.strip(),
            phone=cleaned_phone,
            email=form.email.data.strip().lower(),
            gender=form.gender.data,
            fitness_goal=form.fitness_goal.data,
            training_type=form.training_type.data,
            status='New',
            ip_address=ip
        )
        db.session.add(lead)
        db.session.commit()

        success_msg = "Thank you! We will contact you within 24 hours."

        if is_ajax:
            return jsonify({
                'success': True,
                'message': success_msg,
                'lead_id': lead.id
            })

        session['booking_confirmed'] = True
        return redirect(url_for('public.index') + '#booking-success')

    # Validation errors
    if is_ajax:
        return jsonify({
            'success': False,
            'message': 'Please fix the errors in the form.',
            'errors': form.errors
        }), 400

    hero = HeroContent.query.first()
    settings = SiteSetting.query.first()
    flash('Please fill all required fields correctly.', 'danger')
    return render_template(
        'index.html',
        hero=hero,
        programs=programs,
        training_types=training_types,
        settings=settings,
        form=form
    ), 400
