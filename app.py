import os
from flask import Flask, render_template, request, send_file
from werkzeug.utils import secure_filename
from PIL import Image
import io
import datetime

app = Flask(__name__)

# Vercel-এর অস্থায়ী ফোল্ডার /tmp ব্যবহার করুন
# এই ফোল্ডারটি আগে থেকে থাকে, তাই os.makedirs এর প্রয়োজন নেই
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
            width_percent = new_width / float(img.size[0])
            new_height = int(float(img.size[1]) * width_percent)
            resized_img = img.resize((new_width, new_height), Image.LANCZOS)
            img_io = io.BytesIO()
            # ছবির ফরম্যাট সনাক্ত করার চেষ্টা করুন, না পারলে 'PNG' ব্যবহার করুন
            img_format = img.format if img.format else 'PNG'
            resized_img.save(img_io, format=img_format, quality=95)
            img_io.seek(0)
            return img_io
    except Exception as e:
        print(f"Error resizing image: {e}")
        return None

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
        resized_image_io = resize_image(filepath)
        
        if resized_image_io:
            # ফাইল এক্সটেনশন আলাদা করুন
            name, ext = os.path.splitext(filename)
            resized_filename = f"{name}_resized{ext}"
            resized_filepath = os.path.join(app.config['UPLOAD_FOLDER'], resized_filename)
            
            with open(resized_filepath, 'wb') as f:
                f.write(resized_image_io.getvalue())
            
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

# /tmp ফোল্ডার থেকে ছবি দেখানোর জন্য নতুন রুট
@app.route('/images/<filename>')
def serve_image(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath) # send_file নিজে থেকেই mimetype ঠিক করে নেয়

@app.route('/download/<filename>')
def download_file(filename):
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    return send_file(filepath, as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
