import os
from datetime import datetime
from io import BytesIO
from uuid import uuid4

from flask import Flask, flash, jsonify, redirect, render_template, request, send_file, url_for
from flask_login import LoginManager, current_user, login_required, login_user, logout_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename

from config import Config
from models.db_setup import NewsletterSubscriber, Product, QuoteRequest, Service, User, db
from chatbot_data import CHATBOT_DEFAULT_SUGGESTIONS, generate_helpdesk_reply


ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif', 'webp'}
CONTACT_INFO = {
    'phone_display': '+266 6914 1413',
    'phone_tel': '+26669141413',
    'whatsapp_display': '+266 6313 3336',
    'whatsapp_number': '26663133336',
    'email': 'smartpestsolutions1413@gmail.com',
    'facebook': 'Smart Pest Solutions',
    'instagram': 'Smart Pest Solutions',
    'x': 'Smart Pest Solution',
    'facebook_url': '#',
    'instagram_url': '#',
    'x_url': '#',
    'youtube_url': '#',
}

app = Flask(__name__)
app.config.from_object(Config)

try:
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
except OSError:
    app.config['UPLOAD_FOLDER'] = '/tmp/uploads'
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

db.init_app(app)

login_manager = LoginManager(app)
login_manager.login_view = 'admin_login'
login_manager.login_message = 'Please log in to access the admin area.'


@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS


def save_uploaded_image(file_storage):
    if not file_storage or not file_storage.filename:
        return None

    if not allowed_file(file_storage.filename):
        return None

    filename = secure_filename(file_storage.filename)
    extension = filename.rsplit('.', 1)[1].lower()
    unique_name = f"{uuid4().hex}.{extension}"
    destination = os.path.join(app.config['UPLOAD_FOLDER'], unique_name)
    file_storage.save(destination)
    return unique_name


def bootstrap_admin():
    admin_username = os.getenv('ADMIN_USERNAME', 'admin')
    admin_password = os.getenv('ADMIN_PASSWORD', 'admin123')

    existing_admin = User.query.filter_by(username=admin_username).first()
    if not existing_admin:
        admin = User(
            username=admin_username,
            password=generate_password_hash(admin_password)
        )
        db.session.add(admin)
        db.session.commit()


@app.context_processor
def inject_models():
    return {'Product': Product, 'Service': Service, 'contact': CONTACT_INFO, 'chatbot_suggestions': CHATBOT_DEFAULT_SUGGESTIONS}


@app.route('/')
def index():
    recent_products = Product.query.order_by(Product.created_at.desc()).limit(3).all()
    recent_services = Service.query.order_by(Service.created_at.desc()).limit(3).all()
    return render_template(
        'index.html',
        recent_products=recent_products,
        recent_services=recent_services
    )


@app.route('/products')
def products():
    items = Product.query.order_by(Product.created_at.desc()).all()
    return render_template('products.html', products=items)


@app.route('/services')
def services():
    items = Service.query.order_by(Service.created_at.desc()).all()
    return render_template('services.html', services=items)


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/company')
def company():
    return render_template('company.html')


@app.route('/request-quote', methods=['GET', 'POST'])
def request_quote():
    if request.method == 'POST':
        full_name = request.form.get('full_name', '').strip()
        phone = request.form.get('phone', '').strip()
        email = request.form.get('email', '').strip()
        location = request.form.get('location', '').strip()
        property_type = request.form.get('property_type', '').strip()
        service_type = request.form.get('service_type', '').strip()
        message = request.form.get('message', '').strip()

        if not full_name or not phone or not location or not property_type or not service_type:
            flash('Please complete all required quote fields.', 'danger')
            return render_template('request_quote.html')

        quote = QuoteRequest(
            full_name=full_name,
            phone=phone,
            email=email or None,
            location=location,
            property_type=property_type,
            service_type=service_type,
            message=message or None
        )
        db.session.add(quote)
        db.session.commit()
        flash('Quote request sent. We will contact you shortly.', 'success')
        return redirect(url_for('request_quote'))

    return render_template('request_quote.html')


@app.route('/subscribe', methods=['POST'])
def subscribe():
    email = request.form.get('email', '').strip().lower()
    if not email or '@' not in email:
        flash('Please enter a valid email address.', 'danger')
        return redirect(request.referrer or url_for('index'))

    exists = NewsletterSubscriber.query.filter_by(email=email).first()
    if exists:
        flash('This email is already subscribed.', 'info')
        return redirect(request.referrer or url_for('index'))

    subscriber = NewsletterSubscriber(email=email)
    db.session.add(subscriber)
    db.session.commit()
    flash('Subscribed successfully. Thank you for joining.', 'success')
    return redirect(request.referrer or url_for('index'))


@app.route('/promotions')
def promotions():
    return render_template(
        'info_page.html',
        title='Promotions',
        heading='Current Promotions',
        content='Contact us for seasonal pest control and hygiene offers for homes, businesses, and institutions.'
    )


@app.route('/video-gallery')
def video_gallery():
    return render_template(
        'info_page.html',
        title='Video Gallery',
        heading='Video Gallery',
        content='Our latest service demonstrations and awareness videos will be published here.'
    )


@app.route('/blog')
def blog():
    return render_template(
        'info_page.html',
        title='Blog',
        heading='Pest Advice and Hygiene Tips',
        content='We are preparing practical guides on prevention, treatment timing, and safety for homes and workplaces.'
    )


@app.route('/terms-and-conditions')
def terms_and_conditions():
    return render_template(
        'legal.html',
        title='Terms & Conditions',
        heading='Terms & Conditions',
        points=[
            'Service visits are scheduled based on confirmed bookings and area availability.',
            'Quotes are estimates and may be adjusted after site inspection where necessary.',
            'Clients must follow recommended safety and re-entry guidance after treatment.',
            'Payment terms are agreed in writing for each contract or once-off service.',
        ]
    )


@app.route('/privacy-policy')
def privacy_policy():
    return render_template(
        'legal.html',
        title='Privacy Policy',
        heading='Privacy Policy',
        points=[
            'We collect only information required to deliver services and communicate with clients.',
            'Client information is not sold to third parties.',
            'Data may be used for appointment reminders, service updates, and quality follow-up.',
            'Clients may request updates or deletion of personal data, subject to legal obligations.',
        ]
    )


@app.route('/cookie-policy')
def cookie_policy():
    return render_template(
        'legal.html',
        title='Cookie Policy',
        heading='Cookie Policy',
        points=[
            'This website may use cookies to improve browsing experience and basic analytics.',
            'Cookies help us understand which pages are most useful to visitors.',
            'You can disable cookies in your browser settings if preferred.',
        ]
    )


@app.route('/api/chatbot/message', methods=['POST'])
def chatbot_message():
    payload = request.get_json(silent=True) or {}
    message = (payload.get('message') or '').strip()

    if not message:
        return jsonify({
            'reply': 'Please type your question so I can assist you.',
            'suggestions': CHATBOT_DEFAULT_SUGGESTIONS,
        })

    reply, suggestions = generate_helpdesk_reply(message, CONTACT_INFO)
    return jsonify({'reply': reply, 'suggestions': suggestions})
@app.route('/admin/login', methods=['GET', 'POST'])
def admin_login():
    if current_user.is_authenticated:
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(username=username).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            flash('Welcome back.', 'success')
            return redirect(url_for('admin_dashboard'))

        flash('Invalid username or password.', 'danger')

    return render_template('admin/login.html')


@app.route('/admin/logout')
@login_required
def admin_logout():
    logout_user()
    flash('Logged out successfully.', 'success')
    return redirect(url_for('admin_login'))


@app.route('/admin/dashboard')
@login_required
def admin_dashboard():
    product_count = Product.query.count()
    service_count = Service.query.count()
    quote_count = QuoteRequest.query.count()
    subscriber_count = NewsletterSubscriber.query.count()
    recent_quotes = QuoteRequest.query.order_by(QuoteRequest.created_at.desc()).limit(8).all()
    return render_template(
        'admin/dashboard.html',
        product_count=product_count,
        service_count=service_count,
        quote_count=quote_count,
        subscriber_count=subscriber_count,
        recent_quotes=recent_quotes
    )


@app.route('/admin/leads')
@login_required
def admin_leads():
    quotes = QuoteRequest.query.order_by(QuoteRequest.created_at.desc()).all()
    subscribers = NewsletterSubscriber.query.order_by(NewsletterSubscriber.created_at.desc()).all()
    return render_template('admin/leads.html', quotes=quotes, subscribers=subscribers)


@app.route('/admin/leads/export/pdf')
@login_required
def export_leads_pdf():
    try:
        from reportlab.lib.pagesizes import A4
        from reportlab.pdfgen import canvas
    except ImportError:
        flash('PDF export requires reportlab. Run: pip install reportlab', 'danger')
        return redirect(url_for('admin_leads'))

    quotes = QuoteRequest.query.order_by(QuoteRequest.created_at.desc()).all()
    subscribers = NewsletterSubscriber.query.order_by(NewsletterSubscriber.created_at.desc()).all()

    buffer = BytesIO()
    pdf = canvas.Canvas(buffer, pagesize=A4)
    width, height = A4
    left = 40
    y = height - 40

    def new_page():
        nonlocal y
        pdf.showPage()
        y = height - 40
        pdf.setFont('Helvetica-Bold', 14)
        pdf.drawString(left, y, 'Smart Pest Solutions - Leads Report (continued)')
        y -= 24
        pdf.setFont('Helvetica', 9)

    def ensure_space(min_space=60):
        nonlocal y
        if y < min_space:
            new_page()

    pdf.setFont('Helvetica-Bold', 16)
    pdf.drawString(left, y, 'Smart Pest Solutions - Leads Report')
    y -= 18
    pdf.setFont('Helvetica', 9)
    pdf.drawString(left, y, f'Generated: {datetime.now().strftime("%Y-%m-%d %H:%M")}')
    y -= 22

    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(left, y, f'Quote Requests ({len(quotes)})')
    y -= 16
    pdf.setFont('Helvetica', 9)
    pdf.drawString(left, y, 'Date | Name | Phone | Location | Service')
    y -= 12
    pdf.line(left, y, width - left, y)
    y -= 10

    for quote in quotes:
        ensure_space()
        date_txt = quote.created_at.strftime('%Y-%m-%d')
        line = f"{date_txt} | {quote.full_name[:20]} | {quote.phone[:16]} | {quote.location[:18]} | {quote.service_type[:22]}"
        pdf.drawString(left, y, line)
        y -= 12
        if quote.email:
            ensure_space()
            pdf.drawString(left + 14, y, f'Email: {quote.email[:55]}')
            y -= 12
        if quote.message:
            ensure_space()
            msg = quote.message.replace('\n', ' ')[:90]
            pdf.drawString(left + 14, y, f'Note: {msg}')
            y -= 12
        y -= 4

    ensure_space(90)
    y -= 8
    pdf.setFont('Helvetica-Bold', 12)
    pdf.drawString(left, y, f'Newsletter Subscribers ({len(subscribers)})')
    y -= 16
    pdf.setFont('Helvetica', 9)
    pdf.drawString(left, y, 'Date | Email')
    y -= 12
    pdf.line(left, y, width - left, y)
    y -= 10

    for subscriber in subscribers:
        ensure_space()
        date_txt = subscriber.created_at.strftime('%Y-%m-%d')
        pdf.drawString(left, y, f'{date_txt} | {subscriber.email[:70]}')
        y -= 12

    pdf.save()
    buffer.seek(0)

    filename = f"smartpest-leads-{datetime.now().strftime('%Y%m%d-%H%M')}.pdf"
    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')


@app.route('/admin/products/add', methods=['GET', 'POST'])
@login_required
def add_product():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price_raw = request.form.get('price', '').strip()
        image_file = request.files.get('image')

        if not name:
            flash('Product name is required.', 'danger')
            return render_template('admin/add_product.html')

        price = None
        if price_raw:
            try:
                price = float(price_raw)
            except ValueError:
                flash('Price must be a valid number.', 'danger')
                return render_template('admin/add_product.html')

        image_name = save_uploaded_image(image_file)
        if image_file and image_file.filename and image_name is None:
            flash('Image must be png, jpg, jpeg, gif, or webp.', 'danger')
            return render_template('admin/add_product.html')

        product = Product(
            name=name,
            description=description,
            price=price,
            image=image_name
        )
        db.session.add(product)
        db.session.commit()

        flash('Product created successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/add_product.html')


@app.route('/admin/products/<int:product_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        price_raw = request.form.get('price', '').strip()
        image_file = request.files.get('image')

        if not name:
            flash('Product name is required.', 'danger')
            return render_template('admin/edit_product.html', product=product)

        price = None
        if price_raw:
            try:
                price = float(price_raw)
            except ValueError:
                flash('Price must be a valid number.', 'danger')
                return render_template('admin/edit_product.html', product=product)

        image_name = save_uploaded_image(image_file)
        if image_file and image_file.filename and image_name is None:
            flash('Image must be png, jpg, jpeg, gif, or webp.', 'danger')
            return render_template('admin/edit_product.html', product=product)

        product.name = name
        product.description = description
        product.price = price
        if image_name:
            product.image = image_name

        db.session.commit()
        flash('Product updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/edit_product.html', product=product)


@app.route('/admin/products/<int:product_id>/delete', methods=['POST'])
@login_required
def delete_product(product_id):
    product = db.session.get(Product, product_id)
    if not product:
        flash('Product not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(product)
    db.session.commit()
    flash('Product deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


@app.route('/admin/services/add', methods=['GET', 'POST'])
@login_required
def add_service():
    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        image_file = request.files.get('image')

        if not name:
            flash('Service name is required.', 'danger')
            return render_template('admin/add_service.html')

        image_name = save_uploaded_image(image_file)
        if image_file and image_file.filename and image_name is None:
            flash('Image must be png, jpg, jpeg, gif, or webp.', 'danger')
            return render_template('admin/add_service.html')

        service = Service(name=name, description=description, image=image_name)
        db.session.add(service)
        db.session.commit()

        flash('Service created successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/add_service.html')


@app.route('/admin/services/<int:service_id>/edit', methods=['GET', 'POST'])
@login_required
def edit_service(service_id):
    service = db.session.get(Service, service_id)
    if not service:
        flash('Service not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        description = request.form.get('description', '').strip()
        image_file = request.files.get('image')

        if not name:
            flash('Service name is required.', 'danger')
            return render_template('admin/edit_service.html', service=service)

        image_name = save_uploaded_image(image_file)
        if image_file and image_file.filename and image_name is None:
            flash('Image must be png, jpg, jpeg, gif, or webp.', 'danger')
            return render_template('admin/edit_service.html', service=service)

        service.name = name
        service.description = description
        if image_name:
            service.image = image_name

        db.session.commit()
        flash('Service updated successfully.', 'success')
        return redirect(url_for('admin_dashboard'))

    return render_template('admin/edit_service.html', service=service)


@app.route('/admin/services/<int:service_id>/delete', methods=['POST'])
@login_required
def delete_service(service_id):
    service = db.session.get(Service, service_id)
    if not service:
        flash('Service not found.', 'danger')
        return redirect(url_for('admin_dashboard'))

    db.session.delete(service)
    db.session.commit()
    flash('Service deleted successfully.', 'success')
    return redirect(url_for('admin_dashboard'))


with app.app_context():
    try:
        db.create_all()
        bootstrap_admin()
    except Exception as exc:
        # Avoid crashing serverless cold start; check logs and DATABASE_URL config.
        print(f'Database initialization warning: {exc}')


if __name__ == '__main__':
    app.run(debug=True)



