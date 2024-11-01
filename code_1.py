from flask import Flask, request, jsonify
from flask_cors import CORS  # Import CORS
import re
import usaddress

app = Flask(__name__)
CORS(app)  # Enable CORS for all routes

@app.route('/parse-address', methods=['POST'])
def parse_address():
    # Get the text from the request
    data = request.get_json()
    text = data.get('text', '')

    # Extract the address using regex
    address_match = re.search(r'[A-Za-z\s]+,\s[A-Z]{2}\s\d{5}', text)
    address_text = address_match.group() if address_match else None

    if address_text:
        try:
            # Parse the address using usaddress
            addresses, address_type = usaddress.tag(address_text)
            return jsonify({
                'status': 'success',
                'addresses': addresses,
                'address_type': address_type
            })
        except usaddress.RepeatedLabelError as e:
            return jsonify({
                'status': 'error',
                'message': 'Error parsing address: {}'.format(e)
            }), 400
    else:
        return jsonify({
            'status': 'error',
            'message': 'No address found.'
        }), 404

if __name__ == '__main__':
    app.run(debug=True)
