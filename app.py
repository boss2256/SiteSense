from flask import Flask, render_template, request
from pycaret.classification import load_model, predict_model
from utils import clean_url, get_geoip_location
import pandas as pd
from urllib.parse import urlparse

app = Flask(__name__)
model = load_model("models/website_legitimacy_model")

# Label mapping for prediction classes
label_mapping = {
    0: "Benign",
    1: "Phishing",
    2: "Defacement",
    3: "Malware"
}

# List of trusted domains to bypass the model prediction
trusted_domains = ["facebook.com", "youtube.com", "google.com", "kaggle.com"]


@app.route('/')
def home():
    return render_template("home.html")


@app.route('/predict', methods=['POST'])
def predict():
    if request.method == 'POST':
        url = request.form['url']
        cleaned_url = clean_url(url)

        # Extract domain
        domain = urlparse(cleaned_url).netloc.replace("www.", "")

        # Check if the domain is in the trusted domains list
        if domain in trusted_domains:
            predicted_class = "Benign"
            confidence_score = 1.0  # High confidence for trusted domains
        else:
            # Prepare input DataFrame for model prediction
            features = {
                'url_length': len(cleaned_url),
                'special_char_count': sum(1 for c in cleaned_url if not c.isalnum()),
                'is_https': 1 if 'https' in cleaned_url else 0,
                'digit_count': sum(c.isdigit() for c in cleaned_url),
                'letter_count': sum(c.isalpha() for c in cleaned_url),
                'url': cleaned_url,  # Add placeholder for 'url' column
                'domain': domain  # Add placeholder for 'domain' column
            }
            input_df = pd.DataFrame([features])

            # Model prediction
            prediction = predict_model(model, data=input_df)
            predicted_class = label_mapping[prediction['prediction_label'][0]]
            confidence_score = prediction['prediction_score'][0]

        # Perform GeoIP lookup
        geoip_info = get_geoip_location(cleaned_url)

        # Render the result page with prediction and GeoIP information
        return render_template(
            "result.html",
            url=url,
            predicted_class=predicted_class,
            confidence_score=confidence_score,
            geoip_info=geoip_info
        )


if __name__ == '__main__':
    app.run(debug=True)
