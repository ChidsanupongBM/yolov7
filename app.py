from flask import Flask, request, jsonify
import os
import subprocess
import shutil

app = Flask(__name__)

UPLOAD_FOLDER = 'test'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}

@app.route('/upload', methods=['POST'])
def upload_image():
    if 'file' not in request.files:
        return jsonify({'error': 'No file part'})

    file = request.files['file']

    if file.filename == '':
        return jsonify({'error': 'No selected file'})

    if file and allowed_file(file.filename):
        filename = file.filename
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

        # ลบโฟลเดอร์ "exp" ใน "runs/detect"
        exp_folder = 'runs/detect/exp'
        if os.path.exists(exp_folder):
            shutil.rmtree(exp_folder)

        weights_path = 'runs/train/exp/weights/best.pt'
        conf = 0.25
        source = 'test/' + filename
        detect_command = f'python detect.py --weights {weights_path} --conf {conf} --source {source}'
        
        try:
            subprocess.run(detect_command, shell=True, check=True)
        except subprocess.CalledProcessError:
            return jsonify({'error': 'Error while running detect.py'})

        return jsonify({'message': 'File uploaded and processed successfully'})

if __name__ == '__main__':
    app.run(debug=True)
