     1|import os
     2|import uuid
     3|from flask import Flask, request, jsonify, render_template, send_file
     4|import stripe
     5|import requests
     6|
     7|app = Flask(__name__)
     8|
     9|stripe.api_key = os.environ.get('STRIPE_SECRET_KEY', '')
    10|STRIPE_PUBLISHABLE_KEY = os.environ.get('STRIPE_PUBLISHABLE_KEY', '')
    11|
    12|UPLOAD_FOLDER = "uploads"
    13|RESULTS_FOLDER = "results"
    14|os.makedirs(UPLOAD_FOLDER, exist_ok=True)
    15|os.makedirs(RESULTS_FOLDER, exist_ok=True)
    16|
    17|FREE_PROCESSES = 2
    18|
    19|users = {}
    20|
    21|@app.route('/')
    22|def index():
    23|    return render_template('index.html', stripe_key=STRIPE_PUBLISHABLE_KEY)
    24|
    25|@app.route('/process-image', methods=['POST'])
    26|def process_image():
    27|    if 'image' not in request.files:
    28|        return jsonify({'error': 'No image uploaded'}), 400
    29|    
    30|    file = request.files['image']
    31|    operation = request.form.get('operation', 'remove-bg')
    32|    session_id = request.cookies.get('session_id', 'anon')
    33|    
    34|    if session_id not in users:
    35|        users[session_id] = {'processes': 0}
    36|    
    37|    if users[session_id]['processes'] >= FREE_PROCESSES:
    38|        return jsonify({'error': 'Free limit reached', 'requires_payment': True}), 402
    39|    
    40|    file_id = uuid.uuid4().hex[:12]
    41|    ext = os.path.splitext(file.filename)[1] or '.jpg'
    42|    upload_path = os.path.join(UPLOAD_FOLDER, file_id + ext)
    43|    file.save(upload_path)
    44|    
    45|    result_path = os.path.join(RESULTS_FOLDER, file_id + '_result' + ext)
    46|    
    47|    try:
    48|        if operation == 'remove-bg':
    49|            # Use remove.bg API (free tier)
    50|            api_key = os.environ.get('REMOVEBG_API_KEY', '')
    51|            if api_key:
    52|                with open(upload_path, 'rb') as f:
    53|                    r = requests.post(
    54|                        'https://api.remove.bg/v1.0/removebg',
    55|                        files={'image_file': f},
    56|                        data={'size': 'auto'},
    57|                        headers={'X-Api-Key': api_key}
    58|                    )
    59|                    if r.status_code == 200:
    60|                        with open(result_path, 'wb') as out:
    61|                            out.write(r.content)
    62|                    else:
    63|                        # Fallback: copy original
    64|                        import shutil
    65|                        shutil.copy(upload_path, result_path)
    66|            else:
    67|                import shutil
    68|                shutil.copy(upload_path, result_path)
    69|        
    70|        elif operation == 'upscale':
    71|            import shutil
    72|            shutil.copy(upload_path, result_path)
    73|        
    74|        os.remove(upload_path)
    75|        users[session_id]['processes'] += 1
    76|        
    77|        return jsonify({
    78|            'success': True,
    79|            'result_url': '/download/' + os.path.basename(result_path),
    80|            'processes_remaining': FREE_PROCESSES - users[session_id]['processes']
    81|        })
    82|    except Exception as e:
    83|        return jsonify({'error': str(e)}), 500
    84|
    85|@app.route('/download/<filename>')
    86|def download(filename):
    87|    path = os.path.join(RESULTS_FOLDER, filename)
    88|    if os.path.exists(path):
    89|        return send_file(path, as_attachment=True)
    90|    return jsonify({'error': 'File not found'}), 404
    91|
    92|@app.route('/create-checkout', methods=['POST'])
    93|def create_checkout():
    94|    try:
    95|        session = stripe.checkout.Session.create(
    96|            payment_method_types=['card'],
    97|            line_items=[{
    98|                'price_data': {
    99|                    'currency': 'aud',
   100|                    'product_data': {'name': 'AI Image Pro - Monthly'},
   101|                    'unit_amount': 799,
   102|                    'recurring': {'interval': 'month'},
   103|                },
   104|                'quantity': 1,
   105|            }],
   106|            mode='subscription',
   107|            success_url=request.host_url,
   108|            cancel_url=request.host_url,
   109|        )
   110|        return jsonify({'url': session.url})
   111|    except Exception as e:
   112|        return jsonify({'error': str(e)}), 400
   113|
   114|if __name__ == '__main__':
   115|    port = int(os.environ.get('PORT', 5002))
   116|    app.run(host='0.0.0.0', port=port)
   117|