from app.models import db, HeroContent, Program, TrainingType, SiteSetting


def seed_default_data():
    """Seed default database records if they do not exist."""
    # 1. Hero Content
    if not HeroContent.query.first():
        hero = HeroContent(
            headline="6+ Years of Transforming Lives",
            subheadline="Start Your Personal Fitness Journey",
            badge_text="2 Days Free Trial",
            button_text="Book Now",
            button_url="#booking",
            image_url="/static/images/hero-bg.jpg",
            stat_1_val="6+",
            stat_1_lbl="Years Coaching",
            stat_2_val="500+",
            stat_2_lbl="Clients Transformed",
            stat_3_val="98%",
            stat_3_lbl="Goal Success Rate"
        )
        db.session.add(hero)

    # 2. Training Programs
    if Program.query.count() == 0:
        programs_data = [
            {
                "title": "Fat Loss",
                "description": "Target stubborn fat and torch calories with science-backed metabolic conditioning and high-intensity interval programming tailored to your body type.",
                "badge": "Most Popular",
                "icon_name": "flame",
                "image_url": "/static/images/fat-loss.jpg",
                "order_num": 1,
                "is_active": True
            },
            {
                "title": "Muscle Gain",
                "description": "Build lean, sculpted muscle and develop serious functional strength through progressive resistance training, hypertrophic splits, and tailored nutrition guidance.",
                "badge": "Hypertrophy",
                "icon_name": "dumbbell",
                "image_url": "/static/images/muscle-gain.jpg",
                "order_num": 2,
                "is_active": True
            },
            {
                "title": "Cardio & Athletic Training",
                "description": "Explode your stamina, speed, and overall athletic performance with high-energy agility drills, plyometrics, and heart-pounding cardio circuits.",
                "badge": "High Energy",
                "icon_name": "activity",
                "image_url": "/static/images/cardio-athletic.jpg",
                "order_num": 3,
                "is_active": True
            },
            {
                "title": "Strength, Mobility, Flexibility",
                "description": "Unlock pain-free movement, bulletproof your joints, correct posture, and enhance total body flexibility with functional kettlebell and mobility training.",
                "badge": "Longevity",
                "icon_name": "shield",
                "image_url": "/static/images/strength-mobility.jpg",
                "order_num": 4,
                "is_active": True
            }
        ]
        for p in programs_data:
            db.session.add(Program(**p))

    # 3. Training Types
    if TrainingType.query.count() == 0:
        types_data = [
            {
                "title": "One-to-One Training",
                "description": "100% dedicated personal coaching with real-time biometric tracking, strict form correction, and custom daily workouts built around your lifestyle.",
                "highlight": "100% Dedicated",
                "icon_name": "user",
                "image_url": "/static/images/one-on-one.jpg",
                "order_num": 1,
                "is_active": True
            },
            {
                "title": "Couples Training",
                "description": "Stay accountable, push each other, and enjoy dynamic partner workouts. Tailored to suit individual fitness levels while working out together.",
                "highlight": "Train Together",
                "icon_name": "users",
                "image_url": "/static/images/couples-training.jpg",
                "order_num": 2,
                "is_active": True
            },
            {
                "title": "Group & Family Training",
                "description": "Energetic small-group workouts that build collective fitness habits, friendly motivation, and positive team energy for friends or whole families.",
                "highlight": "Community Spirit",
                "icon_name": "users-round",
                "image_url": "/static/images/group-family.jpg",
                "order_num": 3,
                "is_active": True
            },
            {
                "title": "Any Age Process Training",
                "description": "Safe, progressive exercise programs tailored for any life stage—from teenagers developing athletic agility to seniors maintaining bone density and vitality.",
                "highlight": "All Generations",
                "icon_name": "heart-pulse",
                "image_url": "/static/images/any-age.jpg",
                "order_num": 4,
                "is_active": True
            }
        ]
        for t in types_data:
            db.session.add(TrainingType(**t))

    # 4. Site Settings
    if not SiteSetting.query.first():
        settings = SiteSetting(
            business_name="IronForge Fitness Studio",
            tagline="Transform Your Body & Elevate Your Life",
            phone="+91 98765 43210",
            email="coach@ironforgefitness.in",
            address="#42, 100 Feet Road, Indiranagar, Bengaluru, Karnataka 560038",
            whatsapp_number="919876543210",
            whatsapp_message="Hi Coach! I'm interested in the 2 Days Free Trial. Could you share more details about your training sessions?",
            accent_color="#FF4500",
            meta_title="IronForge Fitness | Personal Fitness Training & 2-Day Free Trial",
            meta_description="Premier personal fitness training studio in Bangalore. Expert coaching for Fat Loss, Muscle Gain, Mobility, and Athletic Conditioning. Claim your 2 Days Free Trial now!",
            instagram_url="https://instagram.com/",
            facebook_url="https://facebook.com/",
            youtube_url="https://youtube.com/",
            twitter_url="https://x.com/",
            opening_hours="Mon - Sat: 6:00 AM - 10:00 PM | Sun: 7:00 AM - 1:00 PM"
        )
        db.session.add(settings)

    db.session.commit()
