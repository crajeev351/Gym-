import re
from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    RadioField,
    SelectField,
    TextAreaField,
    IntegerField,
    SubmitField
)
from wtforms.validators import (
    DataRequired,
    Length,
    EqualTo,
    Optional,
    Regexp,
    ValidationError
)


EMAIL_REGEX = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'


def validate_indian_phone(form, field):
    """Custom validator for 10-digit Indian phone numbers."""
    cleaned = re.sub(r'[\s\-\+]', '', field.data or '')
    if cleaned.startswith('91') and len(cleaned) == 12:
        cleaned = cleaned[2:]
    if not re.match(r'^[6-9]\d{9}$', cleaned):
        raise ValidationError('Please enter a valid 10-digit Indian mobile number (e.g. 9876543210).')


class BookingForm(FlaskForm):
    name = StringField('Full Name', validators=[
        DataRequired(message='Please enter your full name.'),
        Length(min=2, max=100, message='Name must be between 2 and 100 characters.')
    ])
    phone = StringField('Contact Number', validators=[
        DataRequired(message='Please enter your 10-digit mobile number.'),
        validate_indian_phone
    ])
    email = StringField('Email Address', validators=[
        DataRequired(message='Please enter your email address.'),
        Regexp(EMAIL_REGEX, message='Please provide a valid email address.')
    ])
    gender = RadioField('Gender', choices=[('Male', 'Male'), ('Female', 'Female')], validators=[
        DataRequired(message='Please select your gender.')
    ])
    fitness_goal = SelectField('Fitness Goal', validators=[
        DataRequired(message='Please select a fitness goal.')
    ])
    training_type = SelectField('Training Type', validators=[
        DataRequired(message='Please select a training type.')
    ])
    # Honeypot spam defense field (must remain empty)
    honeypot = StringField('Website', validators=[Optional()])
    submit = SubmitField('Claim 2 Days Free Trial')


class LoginForm(FlaskForm):
    username = StringField('Username or Email', validators=[
        DataRequired(message='Username or email is required.')
    ])
    password = PasswordField('Password', validators=[
        DataRequired(message='Password is required.')
    ])
    remember = BooleanField('Keep me logged in')
    submit = SubmitField('Sign In')


class ChangePasswordForm(FlaskForm):
    current_password = PasswordField('Current Password', validators=[
        DataRequired(message='Current password is required.')
    ])
    new_password = PasswordField('New Password', validators=[
        DataRequired(message='New password is required.'),
        Length(min=6, message='New password must be at least 6 characters long.')
    ])
    confirm_password = PasswordField('Confirm New Password', validators=[
        DataRequired(message='Please confirm your new password.'),
        EqualTo('new_password', message='New passwords must match.')
    ])
    submit = SubmitField('Update Password')


class HeroForm(FlaskForm):
    headline = StringField('Hero Headline', validators=[
        DataRequired(message='Headline is required.')
    ])
    subheadline = TextAreaField('Hero Subheadline', validators=[
        DataRequired(message='Subheadline is required.')
    ])
    badge_text = StringField('Highlighted Badge Text', validators=[
        DataRequired(message='Badge text is required.')
    ])
    button_text = StringField('CTA Button Text', validators=[
        DataRequired(message='Button text is required.')
    ])
    button_url = StringField('Button Link Target', validators=[
        DataRequired(message='Button link target is required.')
    ])
    hero_image = FileField('Upload Background Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp'], 'Images only (jpg, jpeg, png, webp)!')
    ])
    stat_1_val = StringField('Metric 1 Value', validators=[Optional()])
    stat_1_lbl = StringField('Metric 1 Label', validators=[Optional()])
    stat_2_val = StringField('Metric 2 Value', validators=[Optional()])
    stat_2_lbl = StringField('Metric 2 Label', validators=[Optional()])
    stat_3_val = StringField('Metric 3 Value', validators=[Optional()])
    stat_3_lbl = StringField('Metric 3 Label', validators=[Optional()])
    submit = SubmitField('Save Hero Changes')


class ProgramForm(FlaskForm):
    title = StringField('Program Title', validators=[
        DataRequired(message='Title is required.')
    ])
    description = TextAreaField('Short Description', validators=[
        DataRequired(message='Description is required.')
    ])
    badge = StringField('Badge / Tag (e.g. Popular, High Energy)', validators=[Optional()])
    icon_name = StringField('Icon Keyword (flame, dumbbell, activity, shield, zap, heart)', validators=[Optional()])
    image_file = FileField('Card Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'svg'], 'Images only!')
    ])
    order_num = IntegerField('Display Order (Lower comes first)', default=0, validators=[Optional()])
    is_active = BooleanField('Visible on Website', default=True)
    submit = SubmitField('Save Program')


class TrainingTypeForm(FlaskForm):
    title = StringField('Training Type Title', validators=[
        DataRequired(message='Title is required.')
    ])
    description = TextAreaField('Short Description', validators=[
        DataRequired(message='Description is required.')
    ])
    highlight = StringField('Highlight Tag (e.g. 1-on-1 Focus, Couples)', validators=[Optional()])
    icon_name = StringField('Icon Keyword (user, users, heart-handshake, calendar)', validators=[Optional()])
    image_file = FileField('Card Image', validators=[
        Optional(),
        FileAllowed(['jpg', 'jpeg', 'png', 'webp', 'svg'], 'Images only!')
    ])
    order_num = IntegerField('Display Order (Lower comes first)', default=0, validators=[Optional()])
    is_active = BooleanField('Visible on Website', default=True)
    submit = SubmitField('Save Training Type')


class SiteSettingsForm(FlaskForm):
    business_name = StringField('Business Name', validators=[
        DataRequired(message='Business name is required.')
    ])
    tagline = StringField('Tagline', validators=[Optional()])
    phone = StringField('Display Phone Number', validators=[
        DataRequired(message='Phone number is required.')
    ])
    email = StringField('Contact Email', validators=[
        DataRequired(message='Email is required.'),
        Regexp(EMAIL_REGEX, message='Please provide a valid email address.')
    ])
    address = TextAreaField('Physical Address', validators=[
        DataRequired(message='Address is required.')
    ])
    whatsapp_number = StringField('WhatsApp Number (with country code, no + or spaces, e.g. 919876543210)', validators=[
        DataRequired(message='WhatsApp number is required.')
    ])
    whatsapp_message = TextAreaField('WhatsApp Prefilled Message', validators=[
        DataRequired(message='Prefilled message is required.')
    ])
    accent_color = StringField('Brand Accent Color (Hex Code, e.g. #FF4500)', validators=[
        DataRequired(message='Accent color is required.')
    ])
    meta_title = StringField('SEO Title Tag', validators=[
        DataRequired(message='SEO Title is required.')
    ])
    meta_description = TextAreaField('SEO Meta Description', validators=[
        DataRequired(message='SEO Meta description is required.')
    ])
    instagram_url = StringField('Instagram URL', validators=[Optional()])
    facebook_url = StringField('Facebook URL', validators=[Optional()])
    youtube_url = StringField('YouTube URL', validators=[Optional()])
    twitter_url = StringField('Twitter / X URL', validators=[Optional()])
    opening_hours = StringField('Operating Hours', validators=[Optional()])
    submit = SubmitField('Update Site Settings')
