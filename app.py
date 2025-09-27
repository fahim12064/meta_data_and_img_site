import os
import io
import datetime
import base64
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PIL import Image

app = Flask(__name__)

# Vercel-এর অস্থায়ী /tmp ফোল্ডার ব্যবহার করা হচ্ছে
UPLOAD_FOLDER = '/tmp'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def generate_meta_tags(phone_model):
    current_year = datetime.datetime.now().year
    country = "Bangladesh"
    country_code = "bd"
    meta_title = f"{phone_model} Price in {country} {current_year}, Full Specs"
    meta_description = f"{phone_model} Full Specifications, Price, Showrooms and Reviews in {country} {current_year}. Compare {phone_model} best prices before buying online."
    meta_keywords = f"{phone_model}, {phone_model} price in {country}, {phone_model} {country_code} prices, {phone_model} full specifications, {phone_model} news reviews"
    return {"title": meta_title, "description": meta_description, "keywords": meta_keywords}

def resize_image(image_path, new_width=300):
    try:
        with Image.open(image_path) as img:
            # মূল ছবির ফরম্যাট সংরক্ষণ করুন
            original_format = img.format
            
            width_percent = new_width / float(img.size[0])
            new_height = int(float(img.size[1]) * width_percent)
            resized_img = img.resize((new_height, new_height), Image.LANCZOS)
            
            img_io = io.BytesIO()
            # রিসাইজ করা ছবিটি মূল ফরম্যাটেই সেভ করুন
            resized_img.save(img_io, format=original_format, quality=95)
            img_io.seek(0)
            return img_io, original_format
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None, None

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        phone_name = request.form.get('phone_name')
        image_file = request.files.get('image_file')
        
        if not phone_name or not image_file or image_file.filename == '':
            return render_template('index.html', error="Please provide both phone name and a valid image file")
        
        filename = secure_filename(image_file.filename)
        filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        image_file.save(filepath)
        
        meta_tags = generate_meta_tags(phone_name)
        
        resized_image_io, image_format = resize_image(filepath)
        
        if resized_image_io:
            # রিসাইজ করা ছবিটি Base64 তে রূপান্তর করুন
            resized_image_base64 = base64.b64encode(resized_image_io.getvalue()).decode('utf-8')
            
            # ছবির ফরম্যাট যদি না পাওয়া যায়, ডিফল্ট হিসেবে 'png' ব্যবহার করুন
            if not image_format:
                image_format = 'png'
            
            # ডাউনলোডের জন্য নতুন ফাইলের নাম তৈরি করুন
            name, ext = os.path.splitext(filename)
            resized_filename = f"{name}_resized.{image_format.lower()}"

            return render_template(
                'index.html',
                phone_name=phone_name,
                meta_tags=meta_tags,
                original_image=filename,
                resized_image_base64=resized_image_base64,
                image_format=image_format.lower(),
                resized_filename=resized_filename
            )
        else:
            return render_template('index.html', error="Error processing image")
    
    return render_template('index.html')

# /tmp ফোল্ডার থেকে মূল ছবিটি দেখানোর জন্য এই রুটটি প্রয়োজন
@app.route('/images/<filename>')
def serve_image(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    try:
        return send_file(filepath)
    except FileNotFoundError:
        return "Image not found. It might have been cleared from the temporary cache. Please upload again.", 404

if __name__ == '__main__':
    app.run(debug=True)
