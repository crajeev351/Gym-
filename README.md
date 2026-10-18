# IronForge Fitness - Lead Generation & Admin Management Portal

A mobile-first, high-conversion lead generation website and secure admin management portal built exclusively with **Flask**, **Jinja2**, and **Vanilla CSS/JavaScript** (no React, Vue, or Node).

---

## Key Features

### 1. Public Website (Mobile-First Single Page)
- **Cinematic Hero**:
  - Highlighting "6+ Years of Transforming Lives"
  - Dynamic "2 Days Free Trial" animated pulsing badge
  - "Book Free Trial" CTA that smoothly scrolls to `#booking`
  - Editable headline, subheadline, badge text, button text, and background image
  - Key performance metric counters: Years Coaching, Lives Transformed, Goal Success Rate
- **Training Programs Grid**:
  - 4 core programs: **Fat Loss**, **Muscle Gain**, **Cardio & Athletic Training**, **Strength, Mobility, Flexibility**
  - High-definition cards with badges, icons, descriptions, and one-click trial booking
  - Full CRUD, reordering (up/down), and show/hide controls in Admin
- **Training Types Grid**:
  - 4 delivery formats: **One-to-One Training**, **Couples Training**, **Group & Family Training**, **Any Age Process Training**
  - Highlight pills, tailored descriptions, and format inquiry actions
  - Full CRUD, reordering (up/down), and show/hide controls in Admin
- **Free Trial Booking Form (`#booking`)**:
  - Fields: Full Name, 10-Digit Indian Mobile Number, Email Address, Gender (Male/Female custom radio cards), Fitness Goal (dynamic from active Programs), Training Type (dynamic from active Training Types)
  - **Client-Side & Server-Side Validation**:
    - Name required (min 2 characters)
    - 10-digit Indian phone validation (regex `^[6-9]\d{9}$`)
    - Email format verification
    - Gender required
  - **Spam & Abuse Protection**:
    - Flask-WTF CSRF protection
    - Hidden honeypot field (`website` / `honeypot` trap for automated spam bots)
    - IP-based sliding window rate-limiting (max 5 requests per 10 minutes per IP)
  - **Seamless UX**: Asynchronous AJAX submission with loading state, instant inline field feedback, and smooth confirmation message: *"Thank you! We will contact you within 24 hours."*
- **Floating WhatsApp Button**:
  - Fixed bottom-right on all viewports with pulsing animation
  - Opens `https://wa.me/<whatsapp_number>?text=<whatsapp_message>`
  - WhatsApp phone number and prefilled message fully editable from Admin
- **Site Footer**:
  - Business name, tagline, address, phone, email, operating hours, and social media links
- **Dynamic SEO & Branding**:
  - Editable `<title>` tag and `<meta description>`
  - Brand accent color editable from admin with color picker and preset swatches

---

### 2. Admin Panel (`/admin`, Login Required)
- **Secure Authentication**:
  - Powered by `Flask-Login` and hashed passwords (`werkzeug.security`)
  - 60-minute session timeout (`PERMANENT_SESSION_LIFETIME`)
  - CLI command: `flask create-admin` (creates or updates admin user)
  - Change Password screen (`/admin/change-password`)
- **Dashboard (`/admin/dashboard`)**:
  - Total leads counter
  - Leads received today
  - Leads received this week
  - Stage pipeline breakdown (New, Contacted, Trial Done, Converted, Not Interested)
  - Latest 5 leads with quick "Reply on WhatsApp" link and status pill
- **Leads Management (`/admin/leads`)**:
  - Real-time search across Name, Phone, and Email
  - Multi-criteria filtering: Gender, Fitness Goal, Training Type, Lead Status, and Date Range (Today, This Week, This Month, All Time)
  - Status management: Inline status dropdown with instant AJAX updating
  - Direct "Reply on WhatsApp" button with pre-filled lead details
  - Filter-aware CSV export (`/admin/leads/export-csv`)
  - Lead deletion with safety confirmation
- **Edit Hero (`/admin/hero`)**:
  - Headline, subheadline, badge text, button text, link target
  - Upload custom hero background image (with preview)
  - Edit metric values and labels
- **Manage Programs (`/admin/programs`)**:
  - Add, edit, delete, reorder (move up / down), and toggle visibility
- **Manage Training Types (`/admin/training-types`)**:
  - Add, edit, delete, reorder (move up / down), and toggle visibility
- **Site Settings & SEO (`/admin/settings`)**:
  - Business name, tagline, phone, email, physical address, operating hours
  - WhatsApp phone number and prefilled message
  - Brand accent color with live color-picker & preset buttons
  - Social profiles (Instagram, Facebook, YouTube, X/Twitter)
  - SEO Title and Meta Description

---

## Technology Stack

- **Backend**: Python 3.10+, Flask, Jinja2
- **Allowed Extensions**:
  - `Flask-SQLAlchemy` (ORM)
  - `Flask-Migrate` (Database migrations)
  - `Flask-Login` (Session authentication)
  - `Flask-WTF` (Form handling, CSRF protection)
  - `psycopg2-binary` (PostgreSQL / Supabase driver)
  - `python-dotenv` (Environment variable loading)
  - `Pillow` (Image verification and uploads)
- **Frontend**: Plain HTML5, Vanilla CSS3 (Custom design system with CSS custom properties), Vanilla JavaScript (No React, Vue, or Node)
- **Database**: SQLite (default local) or PostgreSQL / Supabase via `DATABASE_URL`

---

## Getting Started

### 1. Install Dependencies
```bash
pip install -r requirements.txt
```

### 2. Environment Configuration
Copy `.env.example` to `.env` (or use the pre-configured `.env`):
```bash
# SQLite (default):
DATABASE_URL=sqlite:///gym.db

# Or for Supabase / PostgreSQL:
# DATABASE_URL=postgresql://postgres:password@db.xxxx.supabase.co:5432/postgres
```

### 3. Create Admin Account via CLI
Run the custom Flask CLI command:
```bash
flask create-admin --username admin --email admin@fitnessjourney.com --password YourSecurePassword123!
```
*(You can also run `flask create-admin` interactively without flags to be prompted securely for password input.)*

### 4. Run the Application
```bash
python wsgi.py
```
Open your browser at:
- **Public Website**: `http://localhost:5000/`
- **Admin Portal**: `http://localhost:5000/admin/login`

---

## Database Schema Summary

- **`users`**: Admin user authentication (`id`, `username`, `email`, `password_hash`, `created_at`)
- **`leads`**: Free trial booking leads (`id`, `name`, `phone`, `email`, `gender`, `fitness_goal`, `training_type`, `status`, `ip_address`, `notes`, `created_at`)
- **`programs`**: Training programs cards (`id`, `title`, `description`, `badge`, `icon_name`, `image_url`, `order_num`, `is_active`, `created_at`)
- **`training_types`**: Training formats cards (`id`, `title`, `description`, `highlight`, `icon_name`, `image_url`, `order_num`, `is_active`, `created_at`)
- **`hero_content`**: Hero section texts, image, and stats (`id`, `headline`, `subheadline`, `badge_text`, `button_text`, `button_url`, `image_url`, `stat_*`)
- **`site_settings`**: Global business details, contact info, WhatsApp configs, accent color, and SEO metadata (`id`, `business_name`, `tagline`, `phone`, `email`, `address`, `whatsapp_*`, `accent_color`, `meta_*`, `social_*`)
