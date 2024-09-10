import base64
from gtts import gTTS
import pandas as pd,numpy as np
import io,os,random,cv2
from PIL import Image, ImageDraw,ImageFilter,ImageEnhance
import smtplib,subprocess,re
from twilio.rest import Client
from geopy.geocoders import Nominatim 
from flask import Flask, request, render_template,send_from_directory, flash,jsonify,send_file
from sklearn.datasets import fetch_california_housing
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression

app = Flask(__name__)
app.secret_key ='231d61aacdc033ea781601c07e4415dd'

# Email configuration
FROM_EMAIL =os.getenv('email')
FROM_PASSWORD = os.getenv('app_pwd')
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587
account_sid = os.getenv('acc_sid')
auth_token = os.getenv('auth_token')
number = '+12563056519'
@app.route('/')
def index():
    return render_template('index.html')
@app.route('/projects')
def projects():
    return render_template('project.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/handle_action', methods=['POST'])
def handle_action():
    action = request.form.get('action')

    if action == 'email':
        return render_template('email.html')
    elif action == 'call':
        return render_template('call.html')
    elif action == 'Sms':
        return render_template('Sms.html')
    elif action == 'docker':
        return render_template('docker.html')
    elif action == 'wth':
        return render_template('wth.html')
    elif action == 'geocord':
        return render_template('geocord.html')
    elif action == 'tta':
        return render_template('texttoaudio.html')
    elif action == 'data':
        return render_template('dataprocess.html')
    elif action == 'random_image':
        return render_template('random_image.html')
    elif action == 'image_filter':
        return render_template('image_filter.html')
    elif action == 'live':
        return render_template('livestream.html')
    elif action == 'clickpic':
        return render_template('clickpic.html')
    elif action == 'special_filters':
        return render_template('special_filter.html')
    elif action == 'ml_model':
        return render_template('ml_model.html')
    elif action == 'docker_metrics':
        return render_template('docker_metrics.html')
    elif action == 'micaccess':
        return render_template('micaccess.html')
    else:
        return render_template('index.html')
# -----------------------------------------------------mail---------------------------------------------------------------
@app.route('/send_email', methods=['POST'])
def send_email():
    to_email = request.form['to']
    subject = request.form['subject']
    body = request.form['body']

    email_text = f"""\
From: {FROM_EMAIL}
To: {to_email}
Subject: {subject}

{body}
"""

    try:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
        server.starttls()  # Secure the connection
        server.login(FROM_EMAIL, FROM_PASSWORD)
        server.sendmail(FROM_EMAIL, to_email, email_text)
        server.quit()
        return('Email sent successfully!')
    except Exception as e:
        flash(f'Failed to send email: {e}')
    
    return render_template('form.html')
# -------------------------------------------------------call-----------------------------------------------------------------
@app.route("/call", methods=['post'])
def call():
    no= '+91'+ request.form['to']
    account_sid = os.getenv('acc_sid')
    auth_token = os.getenv('auth_token')
    client = Client(account_sid, auth_token)
    call = client.calls.create(
            from_=number,

            to=no,

            url="http://demo.twilio.com/docs/voice.xml",

        )

    return(call.sid)
# --------------------------------------------------------sms----------------------------------------------------------------------
@app.route("/Sms", methods=['post'])
def Sms():
    msg=request.form['msg']
    no="+91"+request.form['to']
    client = Client(account_sid, auth_token)
    message = client.messages.create(
    body=msg,

	    from_=number,

	    to=no

	)
    return(f"Message sent with SID: {message.sid}")
# ---------------------------------------------------------whatsapp-------------------------------------------------------------------
@app.route("/wth", methods=['post'])
def wth():
    client = Client(account_sid, auth_token)

    message = client.messages.create(
    from_='whatsapp:+14155238886',
    body=request.form['body'],
    to='whatsapp:+91'+request.form['to']
)
    return (f"Message sent with SID: {message.sid}")
# ----------------------------------------------------------cords--------------------------------------------------------------------
@app.route('/get_geo_coordinates', methods=['POST'])
def get_geo_coordinates():
    address = request.form.get('address')

    geolocator = Nominatim(user_agent="geoapi")
    location = geolocator.geocode(address)

    if location:
        coordinates = {
            'latitude': location.latitude,
            'longitude': location.longitude,
            'address': location.address
        }
    else:
        coordinates = {'error': 'Location not found'}

    return jsonify(coordinates)
# --------------------------------------------------------tts--------------------------------------------------------------------
@app.route('/tts', methods=['POST'])
def string_to_audio():
    data = request.json
    text = data.get('text', '')
    if text:
        audio_buffer = io.BytesIO()
        tts = gTTS(text, lang='en')
        tts.write_to_fp(audio_buffer)
        audio_buffer.seek(0)
        
        return send_file(
            audio_buffer,
            as_attachment=True,
            mimetype='audio/mpeg',
            download_name='output.mp3'
        )
    else:
        return jsonify({'error': 'No text provided'}), 400
# ---------------------------------------------process data------------------------------------------------------------------------
@app.route('/process_data', methods=['POST'])
def process_data():
    file = request.files['file']
    if not file:
        return jsonify({'status': 'error', 'message': 'No file uploaded'})

    try:
        # Read the file into a DataFrame
        df = pd.read_csv(file)
        
        # Perform data processing
        summary = {
            'mean': df.mean().to_dict(),
            'median': df.median().to_dict(),
            'std_dev': df.std().to_dict()
        }
        
        return jsonify({'status': 'success', 'summary': summary})
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
# ------------------------------------------------random image---------------------------------------------------------------------
@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        width = int(request.form['width'])
        height = int(request.form['height'])

        # Create an image with random colors
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        for x in range(width):
            for y in range(height):
                draw.point((x, y), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

        # Save the image to a BytesIO object
        img_io = io.BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return f"Error generating image: {str(e)}", 400@app.route('/generate', methods=['POST'])
def generate_image():
    try:
        width = int(request.form['width'])
        height = int(request.form['height'])

        # Create an image with random colors
        image = Image.new('RGB', (width, height), (255, 255, 255))
        draw = ImageDraw.Draw(image)
        
        for x in range(width):
            for y in range(height):
                draw.point((x, y), (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255)))

        # Save the image to a BytesIO object
        img_io = io.BytesIO()
        image.save(img_io, 'PNG')
        img_io.seek(0)

        return send_file(img_io, mimetype='image/png')
    except Exception as e:
        return f"Error generating image: {str(e)}", 400
# -------------------------------------------------------------filter-----------------------------------------------------------
def filters(image, filter_type):
    if filter_type == 'grayscale':
        return cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    elif filter_type == 'blur':
        return cv2.GaussianBlur(image, (15, 15), 0)
    elif filter_type == 'edge':
        return cv2.Canny(image, 100, 200)
    elif filter_type == 'sepia':
        sepia_filter = np.array([[0.272, 0.534, 0.131],
                                 [0.349, 0.686, 0.168],
                                 [0.393, 0.769, 0.189]])
        return cv2.transform(image, sepia_filter)
    elif filter_type == 'sharpen':
        kernel = np.array([[0, -1, 0],
                           [-1, 5, -1],
                           [0, -1, 0]])
        return cv2.filter2D(image, -1, kernel)
    elif filter_type == 'contrast':
        pil_image = Image.fromarray(image)
        enhancer = ImageEnhance.Contrast(pil_image)
        enhanced_image = enhancer.enhance(2)  # Increase contrast
        return np.array(enhanced_image)
    elif filter_type == 'brightness':
        pil_image = Image.fromarray(image)
        enhancer = ImageEnhance.Brightness(pil_image)
        enhanced_image = enhancer.enhance(1.5)  # Increase brightness
        return np.array(enhanced_image)
    elif filter_type == 'edge_enhance':
        pil_image = Image.fromarray(image)
        enhanced_image = pil_image.filter(ImageFilter.EDGE_ENHANCE)
        return np.array(enhanced_image)
    elif filter_type == 'emboss':
        pil_image = Image.fromarray(image)
        enhanced_image = pil_image.filter(ImageFilter.EMBOSS)
        return np.array(enhanced_image)
    elif filter_type == 'posterize':
        pil_image = Image.fromarray(image)
        enhanced_image = pil_image.filter(ImageFilter.POSTERIZE)
        return np.array(enhanced_image)
    elif filter_type == 'invert':
        pil_image = Image.fromarray(image)
        enhanced_image = Image.eval(pil_image, lambda x: 255 - x)
        return np.array(enhanced_image)
    else:
        return image

@app.route('/filter', methods=['POST'])
def apply_filter():
    file = request.files['file']
    filter_type = request.form.get('filter')

    if not file:
        return jsonify({'status': 'error', 'message': 'No file uploaded'})

    try:
        # Read the image file
        img = Image.open(file.stream)
        img = np.array(img)

        # Apply the chosen filter
        filtered_img = filters(img, filter_type)

        # Convert back to PIL Image
        filtered_pil = Image.fromarray(filtered_img)
        buffer = io.BytesIO()
        filtered_pil.save(buffer, format="PNG")
        img_data = buffer.getvalue()

        return jsonify({
            'status': 'success',
            'filtered_image': 'data:image/png;base64,' + base64.b64encode(img_data).decode('utf-8')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
# ------------------------------------------------------special filters-------------------------------------------------------------
def overlay_image(background, overlay_path, position):
    overlay = Image.open(overlay_path).convert("RGBA")
    background.paste(overlay, position, overlay)
    return background

def special_filters(image, filter_type):
    image = Image.fromarray(image)
    if filter_type == 'sunglasses':
        # Ensure the path to the sunglasses image is correct
        return np.array(overlay_image(image, 'sunglasses.png', (50, 50)))
    elif filter_type == 'stars':
        img_draw = ImageDraw.Draw(image)
        for _ in range(100):  # Number of stars
            x = np.random.randint(0, image.width)
            y = np.random.randint(0, image.height)
            img_draw.text((x, y), '*', fill=(0,0,0,0))
        return np.array(image)
    else:
        return np.array(image)

@app.route('/apply_special_filter', methods=['POST'])
def apply_special_filter():
    file = request.files['file']
    filter_type = request.form.get('filter')

    if not file:
        return jsonify({'status': 'error', 'message': 'No file uploaded'})

    try:
        # Read the image file
        img = Image.open(file.stream)
        img = np.array(img)

        # Apply the chosen filter
        filtered_img = special_filters(img, filter_type)

        # Convert back to PIL Image
        filtered_pil = Image.fromarray(filtered_img)
        buffer = io.BytesIO()
        filtered_pil.save(buffer, format="PNG")
        img_data = buffer.getvalue()

        return jsonify({
            'status': 'success',
            'filtered_image': 'data:image/png;base64,' + base64.b64encode(img_data).decode('utf-8')
        })
    except Exception as e:
        return jsonify({'status': 'error', 'message': str(e)})
    # ---------------------------------------------------------livestream---------------------------------------------------------
@app.route('/liveStream', methods=['POST'])
def liveStream():
    stream = request.get_json()
    cap = cv2.VideoCapture(stream)
    while True:
        ret, frame = cap.read()
        if not ret:
            break;
        gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        return jsonify({'status': 'frame processed'})
# ----------------------------------------capture and save--------------------------------------------------------------
@app.route('/capture', methods=['POST'])
def capture_photo():
    # Get the image data from the request
    data = request.get_json()
    image_data = data['image'].split(',')[1]  # Remove the data URL prefix

    # Decode the base64 image data
    image_bytes = base64.b64decode(image_data)
    image_array = np.frombuffer(image_bytes, dtype=np.uint8)
    frame = cv2.imdecode(image_array, cv2.IMREAD_COLOR)

    # Set a fixed filename
    filename = "captured_photo.png"
    file_path = os.path.join('images', filename)

    # Save the image to the specified directory
    if not os.path.exists('images'):
        os.makedirs('images')

    if cv2.imwrite(file_path, frame):
        return jsonify({'message': 'Photo captured and saved successfully', 'file_path': f'/images/{filename}'})
    else:
        return jsonify({'error': 'Failed to save image'})

# Serve the image file from the images directory
@app.route('/images/<filename>')
def get_image(filename):
    return send_from_directory('images', filename)
# -------------------------------------------ml model---------------------------------------------------------------------
housing = fetch_california_housing()
X = housing.data[:, [0, 3]]  # Only use 'MedInc' and 'AveRooms'
y = housing.target

# Split dataset into training set and test set
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

# Create a Linear Regression model
model = LinearRegression()
model.fit(X_train, y_train)

@app.route('/predict', methods=['POST'])
def predict():
    data = request.get_json()

    # Convert input data to float (or numeric) values
    median_income = float(data['medianIncome'])
    avg_rooms = float(data['avgRooms'])

    # Combine input features into a numpy array
    input_features = np.array([median_income, avg_rooms]).reshape(1, -1)

    # Make prediction
    prediction = model.predict(input_features)

    # Return the prediction as a JSON response
    return jsonify({'prediction': prediction[0] * 100})
# -------------------------------------docker metrics--------------------------------------------------------------------
@app.route('/docker-metrics', methods=['GET'])
def get_docker_metrics():
    metrics = {
        "memory_used": random.uniform(200, 500),  # In MB
        "status": "running",  # could be "stopped", "paused", etc.
        "storage": random.uniform(20, 100),  # In GB
    }
    return jsonify(metrics)
# ------------------------------------------------------DOCKER----------------------------------------------
@app.route("/pull", methods=['post'])
def pull():
    img=request.form['docker']
    cmd=f'docker pull {img}'
    status,output = subprocess.getstatusoutput(cmd)
    if status == 0:
        image_name = output.split('/')[-1]
        return image_name
    else:
        return("image downloded failed")

@app.route("/images", methods=['post'])
def get_images():
    status,output = subprocess.getstatusoutput('docker images')
    if status == 0:
        img = re.sub(r'(SIZE|MB|kB)', r'\1\n', output)
        return img
    else:
        return("image downloded failed")

if __name__ == '__main__':
    app.run()

                                                                                                       
