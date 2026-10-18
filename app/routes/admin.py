import os
import csv
import io
import time
from datetime import datetime, timezone, timedelta
from werkzeug.utils import secure_filename
from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    flash,
    request,
    Response,
    jsonify,
    current_app
)
from flask_login import login_user, logout_user, login_required, current_user
from app.models import db, User, Lead, Program, TrainingType, HeroContent, SiteSetting
from app.forms import (
    LoginForm,
    ChangePasswordForm,
    HeroForm,
    ProgramForm,
    TrainingTypeForm,
    SiteSettingsForm
)

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


def save_image(file_storage):
    """Save an uploaded image file securely and return its static URL path."""
    if not file_storage or not file_storage.filename:
        return None
    filename = secure_filename(file_storage.filename)
    if not filename:
        return None
    ext = os.path.splitext(filename)[1].lower()
    unique_name = f"upload_{int(time.time())}_{filename}"
    upload_dir = current_app.config['UPLOAD_FOLDER']
    os.makedirs(upload_dir, exist_ok=True)
    full_path = os.path.join(upload_dir, unique_name)
    file_storage.save(full_path)
    return f"/static/uploads/{unique_name}"


# ==========================================
# AUTHENTICATION
# ==========================================

@admin_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))

    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter(
            (User.username == form.username.data.strip()) |
            (User.email == form.username.data.strip().lower())
        ).first()

        if user and user.check_password(form.password.data):
            login_user(user, remember=form.remember.data)
            flash(f"Welcome back, {user.username}!", "success")
            next_page = request.args.get('next')
            if not next_page or not next_page.startswith('/admin'):
                next_page = url_for('admin.dashboard')
            return redirect(next_page)
        else:
            flash("Invalid username or password. Please try again.", "danger")

    return render_template('admin/login.html', form=form)


@admin_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been safely logged out.", "info")
    return redirect(url_for('admin.login'))


@admin_bp.route('/change-password', methods=['GET', 'POST'])
@login_required
def change_password():
    form = ChangePasswordForm()
    if form.validate_on_submit():
        if not current_user.check_password(form.current_password.data):
            flash("Your current password was incorrect.", "danger")
        else:
            current_user.set_password(form.new_password.data)
            db.session.commit()
            flash("Your password has been updated successfully!", "success")
            return redirect(url_for('admin.dashboard'))

    return render_template('admin/change_password.html', form=form)


# ==========================================
# DASHBOARD
# ==========================================

@admin_bp.route('/')
@admin_bp.route('/dashboard')
@login_required
def dashboard():
    now = datetime.utcnow()
    start_of_today = datetime(now.year, now.month, now.day)
    start_of_week = start_of_today - timedelta(days=now.weekday())

    total_leads = Lead.query.count()
    leads_today = Lead.query.filter(Lead.created_at >= start_of_today).count()
    leads_this_week = Lead.query.filter(Lead.created_at >= start_of_week).count()
    latest_leads = Lead.query.order_by(Lead.created_at.desc()).limit(5).all()

    # Status breakdown
    statuses = ['New', 'Contacted', 'Trial Done', 'Converted', 'Not Interested']
    status_counts = {}
    for s in statuses:
        status_counts[s] = Lead.query.filter_by(status=s).count()

    total_programs = Program.query.count()
    total_training_types = TrainingType.query.count()

    return render_template(
        'admin/dashboard.html',
        total_leads=total_leads,
        leads_today=leads_today,
        leads_this_week=leads_this_week,
        latest_leads=latest_leads,
        status_counts=status_counts,
        total_programs=total_programs,
        total_training_types=total_training_types
    )


# ==========================================
# LEADS MANAGEMENT
# ==========================================

@admin_bp.route('/leads')
@login_required
def leads():
    query = Lead.query

    # Search query
    q = request.args.get('q', '').strip()
    if q:
        search_pattern = f"%{q}%"
        query = query.filter(
            (Lead.name.ilike(search_pattern)) |
            (Lead.phone.ilike(search_pattern)) |
            (Lead.email.ilike(search_pattern))
        )

    # Filter: Gender
    gender = request.args.get('gender', '').strip()
    if gender in ['Male', 'Female']:
        query = query.filter_by(gender=gender)

    # Filter: Fitness Goal
    goal = request.args.get('goal', '').strip()
    if goal:
        query = query.filter_by(fitness_goal=goal)

    # Filter: Training Type
    training_type = request.args.get('training_type', '').strip()
    if training_type:
        query = query.filter_by(training_type=training_type)

    # Filter: Status
    status = request.args.get('status', '').strip()
    if status in ['New', 'Contacted', 'Trial Done', 'Converted', 'Not Interested']:
        query = query.filter_by(status=status)

    # Filter: Date range
    date_filter = request.args.get('date', '').strip()
    now = datetime.utcnow()
    if date_filter == 'today':
        start_of_today = datetime(now.year, now.month, now.day)
        query = query.filter(Lead.created_at >= start_of_today)
    elif date_filter == 'this_week':
        start_of_week = datetime(now.year, now.month, now.day) - timedelta(days=now.weekday())
        query = query.filter(Lead.created_at >= start_of_week)
    elif date_filter == 'this_month':
        start_of_month = datetime(now.year, now.month, 1)
        query = query.filter(Lead.created_at >= start_of_month)

    leads_list = query.order_by(Lead.created_at.desc()).all()

    # Dropdown lists for filters
    all_programs = Program.query.order_by(Program.title.asc()).all()
    all_training_types = TrainingType.query.order_by(TrainingType.title.asc()).all()
    statuses = ['New', 'Contacted', 'Trial Done', 'Converted', 'Not Interested']

    return render_template(
        'admin/leads.html',
        leads=leads_list,
        programs=all_programs,
        training_types=all_training_types,
        statuses=statuses,
        current_filters={
            'q': q,
            'gender': gender,
            'goal': goal,
            'training_type': training_type,
            'status': status,
            'date': date_filter
        }
    )


@admin_bp.route('/leads/<int:lead_id>/status', methods=['POST'])
@login_required
def update_lead_status(lead_id):
    lead = db.get_or_404(Lead, lead_id)
    new_status = request.form.get('status', '').strip()
    valid_statuses = ['New', 'Contacted', 'Trial Done', 'Converted', 'Not Interested']

    if new_status in valid_statuses:
        lead.status = new_status
        db.session.commit()
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': True, 'lead_id': lead.id, 'status': lead.status})
        flash(f"Status for {lead.name} updated to '{new_status}'.", "success")
    else:
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return jsonify({'success': False, 'message': 'Invalid status'}), 400
        flash("Invalid status specified.", "danger")

    return redirect(request.referrer or url_for('admin.leads'))


@admin_bp.route('/leads/<int:lead_id>/delete', methods=['POST'])
@login_required
def delete_lead(lead_id):
    lead = db.get_or_404(Lead, lead_id)
    name = lead.name
    db.session.delete(lead)
    db.session.commit()
    flash(f"Lead for '{name}' has been permanently deleted.", "info")
    return redirect(request.referrer or url_for('admin.leads'))


@admin_bp.route('/leads/export-csv')
@login_required
def export_leads_csv():
    # Export filtered or full leads list
    query = Lead.query

    q = request.args.get('q', '').strip()
    if q:
        query = query.filter(
            (Lead.name.ilike(f"%{q}%")) |
            (Lead.phone.ilike(f"%{q}%")) |
            (Lead.email.ilike(f"%{q}%"))
        )
    gender = request.args.get('gender', '').strip()
    if gender in ['Male', 'Female']:
        query = query.filter_by(gender=gender)
    goal = request.args.get('goal', '').strip()
    if goal:
        query = query.filter_by(fitness_goal=goal)
    training_type = request.args.get('training_type', '').strip()
    if training_type:
        query = query.filter_by(training_type=training_type)
    status = request.args.get('status', '').strip()
    if status in ['New', 'Contacted', 'Trial Done', 'Converted', 'Not Interested']:
        query = query.filter_by(status=status)

    leads_list = query.order_by(Lead.created_at.desc()).all()

    output = io.StringIO()
    writer = csv.writer(output)

    # Header
    writer.writerow([
        'Lead ID',
        'Date Received (UTC)',
        'Full Name',
        'Contact Number',
        'Email Address',
        'Gender',
        'Fitness Goal',
        'Training Type',
        'Lead Status',
        'IP Address'
    ])

    for l in leads_list:
        writer.writerow([
            l.id,
            l.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            l.name,
            l.phone,
            l.email,
            l.gender,
            l.fitness_goal,
            l.training_type,
            l.status,
            l.ip_address or ''
        ])

    csv_data = output.getvalue()
    filename = f"leads_export_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}.csv"

    return Response(
        csv_data,
        mimetype="text/csv",
        headers={"Content-Disposition": f"attachment;filename={filename}"}
    )


# ==========================================
# HERO SECTION MANAGEMENT
# ==========================================

@admin_bp.route('/hero', methods=['GET', 'POST'])
@login_required
def hero():
    hero_item = HeroContent.query.first()
    if not hero_item:
        hero_item = HeroContent()
        db.session.add(hero_item)
        db.session.commit()

    form = HeroForm(obj=hero_item)

    if form.validate_on_submit():
        hero_item.headline = form.headline.data.strip()
        hero_item.subheadline = form.subheadline.data.strip()
        hero_item.badge_text = form.badge_text.data.strip()
        hero_item.button_text = form.button_text.data.strip()
        hero_item.button_url = form.button_url.data.strip()
        hero_item.stat_1_val = form.stat_1_val.data.strip()
        hero_item.stat_1_lbl = form.stat_1_lbl.data.strip()
        hero_item.stat_2_val = form.stat_2_val.data.strip()
        hero_item.stat_2_lbl = form.stat_2_lbl.data.strip()
        hero_item.stat_3_val = form.stat_3_val.data.strip()
        hero_item.stat_3_lbl = form.stat_3_lbl.data.strip()

        # Check background image upload
        if form.hero_image.data:
            uploaded_url = save_image(form.hero_image.data)
            if uploaded_url:
                hero_item.image_url = uploaded_url

        db.session.commit()
        flash("Hero section updated successfully!", "success")
        return redirect(url_for('admin.hero'))

    return render_template('admin/hero.html', form=form, hero=hero_item)


# ==========================================
# PROGRAMS MANAGEMENT
# ==========================================

@admin_bp.route('/programs')
@login_required
def programs():
    programs_list = Program.query.order_by(Program.order_num.asc(), Program.id.asc()).all()
    return render_template('admin/programs.html', programs=programs_list)


@admin_bp.route('/programs/new', methods=['GET', 'POST'])
@login_required
def program_new():
    form = ProgramForm()
    if form.validate_on_submit():
        image_url = '/static/images/fat-loss.jpg'  # fallback
        if form.image_file.data:
            uploaded_url = save_image(form.image_file.data)
            if uploaded_url:
                image_url = uploaded_url

        program = Program(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            badge=form.badge.data.strip() if form.badge.data else None,
            icon_name=form.icon_name.data.strip() if form.icon_name.data else 'dumbbell',
            image_url=image_url,
            order_num=form.order_num.data or 0,
            is_active=form.is_active.data
        )
        db.session.add(program)
        db.session.commit()
        flash(f"Program '{program.title}' added successfully!", "success")
        return redirect(url_for('admin.programs'))

    return render_template('admin/program_form.html', form=form, title='Add New Training Program')


@admin_bp.route('/programs/<int:program_id>/edit', methods=['GET', 'POST'])
@login_required
def program_edit(program_id):
    program = db.get_or_404(Program, program_id)
    form = ProgramForm(obj=program)

    if form.validate_on_submit():
        program.title = form.title.data.strip()
        program.description = form.description.data.strip()
        program.badge = form.badge.data.strip() if form.badge.data else None
        program.icon_name = form.icon_name.data.strip() if form.icon_name.data else 'dumbbell'
        program.order_num = form.order_num.data or 0
        program.is_active = form.is_active.data

        if form.image_file.data:
            uploaded = save_image(form.image_file.data)
            if uploaded:
                program.image_url = uploaded

        db.session.commit()
        flash(f"Program '{program.title}' updated successfully!", "success")
        return redirect(url_for('admin.programs'))

    return render_template('admin/program_form.html', form=form, program=program, title=f"Edit '{program.title}'")


@admin_bp.route('/programs/<int:program_id>/toggle', methods=['POST'])
@login_required
def program_toggle(program_id):
    program = db.get_or_404(Program, program_id)
    program.is_active = not program.is_active
    db.session.commit()
    status_str = "visible" if program.is_active else "hidden"
    flash(f"Program '{program.title}' is now {status_str}.", "info")
    return redirect(url_for('admin.programs'))


@admin_bp.route('/programs/<int:program_id>/move/<string:direction>', methods=['POST'])
@login_required
def program_move(program_id, direction):
    program = db.get_or_404(Program, program_id)
    programs = Program.query.order_by(Program.order_num.asc(), Program.id.asc()).all()
    idx = programs.index(program)

    if direction == 'up' and idx > 0:
        other = programs[idx - 1]
        program.order_num, other.order_num = other.order_num, program.order_num
        if program.order_num == other.order_num:
            program.order_num -= 1
        db.session.commit()
    elif direction == 'down' and idx < len(programs) - 1:
        other = programs[idx + 1]
        program.order_num, other.order_num = other.order_num, program.order_num
        if program.order_num == other.order_num:
            program.order_num += 1
        db.session.commit()

    return redirect(url_for('admin.programs'))


@admin_bp.route('/programs/<int:program_id>/delete', methods=['POST'])
@login_required
def program_delete(program_id):
    program = db.get_or_404(Program, program_id)
    title = program.title
    db.session.delete(program)
    db.session.commit()
    flash(f"Program '{title}' deleted.", "info")
    return redirect(url_for('admin.programs'))


# ==========================================
# TRAINING TYPES MANAGEMENT
# ==========================================

@admin_bp.route('/training-types')
@login_required
def training_types():
    types_list = TrainingType.query.order_by(TrainingType.order_num.asc(), TrainingType.id.asc()).all()
    return render_template('admin/training_types.html', training_types=types_list)


@admin_bp.route('/training-types/new', methods=['GET', 'POST'])
@login_required
def training_type_new():
    form = TrainingTypeForm()
    if form.validate_on_submit():
        image_url = '/static/images/one-on-one.jpg'
        if form.image_file.data:
            uploaded = save_image(form.image_file.data)
            if uploaded:
                image_url = uploaded

        training_type = TrainingType(
            title=form.title.data.strip(),
            description=form.description.data.strip(),
            highlight=form.highlight.data.strip() if form.highlight.data else None,
            icon_name=form.icon_name.data.strip() if form.icon_name.data else 'user',
            image_url=image_url,
            order_num=form.order_num.data or 0,
            is_active=form.is_active.data
        )
        db.session.add(training_type)
        db.session.commit()
        flash(f"Training Type '{training_type.title}' added successfully!", "success")
        return redirect(url_for('admin.training_types'))

    return render_template('admin/training_type_form.html', form=form, title='Add New Training Type')


@admin_bp.route('/training-types/<int:type_id>/edit', methods=['GET', 'POST'])
@login_required
def training_type_edit(type_id):
    training_type = db.get_or_404(TrainingType, type_id)
    form = TrainingTypeForm(obj=training_type)

    if form.validate_on_submit():
        training_type.title = form.title.data.strip()
        training_type.description = form.description.data.strip()
        training_type.highlight = form.highlight.data.strip() if form.highlight.data else None
        training_type.icon_name = form.icon_name.data.strip() if form.icon_name.data else 'user'
        training_type.order_num = form.order_num.data or 0
        training_type.is_active = form.is_active.data

        if form.image_file.data:
            uploaded = save_image(form.image_file.data)
            if uploaded:
                training_type.image_url = uploaded

        db.session.commit()
        flash(f"Training Type '{training_type.title}' updated successfully!", "success")
        return redirect(url_for('admin.training_types'))

    return render_template('admin/training_type_form.html', form=form, training_type=training_type, title=f"Edit '{training_type.title}'")


@admin_bp.route('/training-types/<int:type_id>/toggle', methods=['POST'])
@login_required
def training_type_toggle(type_id):
    training_type = db.get_or_404(TrainingType, type_id)
    training_type.is_active = not training_type.is_active
    db.session.commit()
    status_str = "visible" if training_type.is_active else "hidden"
    flash(f"Training Type '{training_type.title}' is now {status_str}.", "info")
    return redirect(url_for('admin.training_types'))


@admin_bp.route('/training-types/<int:type_id>/move/<string:direction>', methods=['POST'])
@login_required
def training_type_move(type_id, direction):
    training_type = db.get_or_404(TrainingType, type_id)
    types_list = TrainingType.query.order_by(TrainingType.order_num.asc(), TrainingType.id.asc()).all()
    idx = types_list.index(training_type)

    if direction == 'up' and idx > 0:
        other = types_list[idx - 1]
        training_type.order_num, other.order_num = other.order_num, training_type.order_num
        if training_type.order_num == other.order_num:
            training_type.order_num -= 1
        db.session.commit()
    elif direction == 'down' and idx < len(types_list) - 1:
        other = types_list[idx + 1]
        training_type.order_num, other.order_num = other.order_num, training_type.order_num
        if training_type.order_num == other.order_num:
            training_type.order_num += 1
        db.session.commit()

    return redirect(url_for('admin.training_types'))


@admin_bp.route('/training-types/<int:type_id>/delete', methods=['POST'])
@login_required
def training_type_delete(type_id):
    training_type = db.get_or_404(TrainingType, type_id)
    title = training_type.title
    db.session.delete(training_type)
    db.session.commit()
    flash(f"Training Type '{title}' deleted.", "info")
    return redirect(url_for('admin.training_types'))


# ==========================================
# SITE SETTINGS
# ==========================================

@admin_bp.route('/settings', methods=['GET', 'POST'])
@login_required
def settings():
    site_settings = SiteSetting.query.first()
    if not site_settings:
        site_settings = SiteSetting()
        db.session.add(site_settings)
        db.session.commit()

    form = SiteSettingsForm(obj=site_settings)

    if form.validate_on_submit():
        site_settings.business_name = form.business_name.data.strip()
        site_settings.tagline = form.tagline.data.strip() if form.tagline.data else ''
        site_settings.phone = form.phone.data.strip()
        site_settings.email = form.email.data.strip().lower()
        site_settings.address = form.address.data.strip()
        # Clean whatsapp number: strip spaces, +, etc.
        raw_wa = form.whatsapp_number.data.strip().replace('+', '').replace(' ', '').replace('-', '')
        site_settings.whatsapp_number = raw_wa
        site_settings.whatsapp_message = form.whatsapp_message.data.strip()
        site_settings.accent_color = form.accent_color.data.strip()
        site_settings.meta_title = form.meta_title.data.strip()
        site_settings.meta_description = form.meta_description.data.strip()
        site_settings.instagram_url = form.instagram_url.data.strip() if form.instagram_url.data else ''
        site_settings.facebook_url = form.facebook_url.data.strip() if form.facebook_url.data else ''
        site_settings.youtube_url = form.youtube_url.data.strip() if form.youtube_url.data else ''
        site_settings.twitter_url = form.twitter_url.data.strip() if form.twitter_url.data else ''
        site_settings.opening_hours = form.opening_hours.data.strip() if form.opening_hours.data else ''

        db.session.commit()
        flash("Site settings updated successfully!", "success")
        return redirect(url_for('admin.settings'))

    return render_template('admin/settings.html', form=form, settings=site_settings)
