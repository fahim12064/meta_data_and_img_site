import os
from flask import Flask, render_template, request, send_file, redirect, url_for
from werkzeug.utils import secure_filename
from PIL import Image
import io
import datetime

app = Flask(__name__)
app.config['UPLOAD_FOLDER'] = 'static/uploads'
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

# আপলোড ফোল্ডার তৈরি করুন
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

def generate_meta_tags(phone_model):
    current_year = datetime.datetime.now().year
    country = "Bangladesh"
    country_code = "bd"

    # Meta Title Generation
    meta_title = f"{phone_model} Price in {country} {current_year}, Full Specs"

    # Meta Description Generation
    meta_description = f"{phone_model} Full Specifications, Price, Showrooms and Reviews in {country} {current_year}. Compare {phone_model} best prices before buying online."

    # Meta Keywords Generation
    meta_keywords = f"{phone_model}, {phone_model} price in {country}, {phone_model} {country_code} prices, {phone_model} full specifications, {phone_model} news reviews"

    return {
        "title": meta_title,
        "description": meta_description,
        "keywords": meta_keywords
    }

def resize_image(image_path, new_width=300):
    try:
        with Image.open(image_path) as img:
            # Calculate new height keeping aspect ratio
            width_percent = new_width / float(img.size[0])
            new_height = int(float(img.size[1]) * width_percent)
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            
            # Save resized image to memory
            img_io = io.BytesIO()
            resized_img.save(img_io, format=img.format, quality=95)
            img_io.seek(0)
            return img_io
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # ফর্ম ডেটা পান
        phone_name = request.form.get('phone_name')
        image_file = request.files.get('image_file')
        
        if not phone_name or not image_file:
            return render_template('index.html', error="Please provide both phone name and image")
        
        # ইমেজ সেভ করুন
        filename = secure_filename(image_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        
        # মেটাডেটা জেনারেট করুন
        meta_tags = generate_meta_tags(phone_name)
        
        # ইমেজ রিসাইজ করুন
        resized_image = resize_image(filepath)
        
        if resized_image:
            # রিসাইজ করা ইমেজ সেভ করুন
            resized_filename = f"resized_{filename}"
            resized_filepath = os.path.join(app.config['UPLOAD_FOLDER'], resized_filename)
            
            with open(resized_filepath, 'wb') as f:
                f.write(resized_image.getvalue())
            
            return render_template(
                'index.html',
                phone_name=phone_name,
                meta_tags=meta_tags,
                original_image=filename,
                resized_image=resized_filename
            )
        else:
            return render_template('index.html', error="Error processing image")
    
    return render_template('index.html')

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)