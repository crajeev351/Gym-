from datetime import datetime
from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64), unique=True, nullable=False, index=True)
    email = db.Column(db.String(120), unique=True, nullable=False, index=True)
    password_hash = db.Column(db.String(256), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    def __repr__(self):
        return f'<User {self.username}>'


class Lead(db.Model):
    __tablename__ = 'leads'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    phone = db.Column(db.String(20), nullable=False, index=True)
    email = db.Column(db.String(120), nullable=False, index=True)
    gender = db.Column(db.String(10), nullable=False)  # Male / Female
    fitness_goal = db.Column(db.String(120), nullable=False)
    training_type = db.Column(db.String(120), nullable=False)
    status = db.Column(db.String(30), default='New', nullable=False, index=True)
    # Status options: 'New', 'Contacted', 'Trial Done', 'Converted', 'Not Interested'
    ip_address = db.Column(db.String(45), nullable=True)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, index=True)

    @property
    def formatted_phone(self):
        # Format for display: +91 XXXXX XXXXX
        clean = self.phone.replace(' ', '').replace('-', '').replace('+91', '')
        if len(clean) == 10:
            return f"+91 {clean[:5]} {clean[5:]}"
        return self.phone

    @property
    def whatsapp_link(self):
        clean_phone = self.phone.replace(' ', '').replace('-', '').replace('+', '')
        if not clean_phone.startswith('91') and len(clean_phone) == 10:
            clean_phone = '91' + clean_phone
        text = f"Hi {self.name}, thank you for requesting your 2 Days Free Trial for {self.fitness_goal} ({self.training_type}). When would you like to schedule your first session?"
        import urllib.parse
        encoded = urllib.parse.quote(text)
        return f"https://wa.me/{clean_phone}?text={encoded}"

    def __repr__(self):
        return f'<Lead {self.name} - {self.phone}>'


class Program(db.Model):
    __tablename__ = 'programs'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    badge = db.Column(db.String(50), nullable=True)
    icon_name = db.Column(db.String(50), default='flame')
    image_url = db.Column(db.String(255), nullable=False)
    order_num = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<Program {self.title}>'


class TrainingType(db.Model):
    __tablename__ = 'training_types'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=False)
    highlight = db.Column(db.String(50), nullable=True)
    icon_name = db.Column(db.String(50), default='user')
    image_url = db.Column(db.String(255), nullable=False)
    order_num = db.Column(db.Integer, default=0, nullable=False)
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __repr__(self):
        return f'<TrainingType {self.title}>'


class HeroContent(db.Model):
    __tablename__ = 'hero_content'

    id = db.Column(db.Integer, primary_key=True)
    headline = db.Column(db.String(200), default='6+ Years of Transforming Lives', nullable=False)
    subheadline = db.Column(db.String(300), default='Start Your Personal Fitness Journey', nullable=False)
    badge_text = db.Column(db.String(100), default='2 Days Free Trial', nullable=False)
    button_text = db.Column(db.String(80), default='Book Free Trial', nullable=False)
    button_url = db.Column(db.String(100), default='#booking', nullable=False)
    image_url = db.Column(db.String(255), default='/static/images/hero-bg.jpg', nullable=False)
    stat_1_val = db.Column(db.String(50), default='6+')
    stat_1_lbl = db.Column(db.String(80), default='Years Coaching')
    stat_2_val = db.Column(db.String(50), default='500+')
    stat_2_lbl = db.Column(db.String(80), default='Lives Transformed')
    stat_3_val = db.Column(db.String(50), default='98%')
    stat_3_lbl = db.Column(db.String(80), default='Client Goal Success')
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<HeroContent {self.headline}>'


class SiteSetting(db.Model):
    __tablename__ = 'site_settings'

    id = db.Column(db.Integer, primary_key=True)
    business_name = db.Column(db.String(120), default='IronForge Fitness Studio', nullable=False)
    tagline = db.Column(db.String(200), default='Elite Personal Coaching & Functional Body Transformation', nullable=False)
    phone = db.Column(db.String(30), default='+91 98765 43210', nullable=False)
    email = db.Column(db.String(120), default='train@ironforgefitness.in', nullable=False)
    address = db.Column(db.String(255), default='#42, 100 Feet Road, Indiranagar, Bengaluru, Karnataka 560038', nullable=False)
    whatsapp_number = db.Column(db.String(30), default='919876543210', nullable=False)
    whatsapp_message = db.Column(db.Text, default='Hello! I want to claim my 2 Days Free Trial and discuss my fitness goals.', nullable=False)
    accent_color = db.Column(db.String(20), default='#FF4500', nullable=False)
    meta_title = db.Column(db.String(200), default='IronForge Fitness | Personal Fitness Training & 2-Day Free Trial', nullable=False)
    meta_description = db.Column(db.Text, default='Join Bangalore premier personal fitness coaching studio. Specialized Fat Loss, Muscle Gain, Athletic Conditioning & Mobility. Claim your 2 Days Free Trial today!', nullable=False)
    instagram_url = db.Column(db.String(255), default='https://instagram.com/', nullable=False)
    facebook_url = db.Column(db.String(255), default='https://facebook.com/', nullable=False)
    youtube_url = db.Column(db.String(255), default='https://youtube.com/', nullable=False)
    twitter_url = db.Column(db.String(255), default='https://x.com/', nullable=False)
    opening_hours = db.Column(db.String(255), default='Mon - Sat: 6:00 AM - 10:00 PM | Sun: 7:00 AM - 1:00 PM', nullable=False)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def __repr__(self):
        return f'<SiteSetting {self.business_name}>'
