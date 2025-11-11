from flask import Flask, render_template, request, redirect, url_for, send_file
from pymongo import MongoClient
import gridfs
import io

app = Flask(__name__)

client = MongoClient("mongodb://localhost:27017/")
db = client["file_storage"]
fs = gridfs.GridFS(db)

@app.route('/')
def index():
    files = []
    for file in db.fs.files.find():
        chunks_count = db.fs.chunks.count_documents({"files_id": file["_id"]})
        files.append({
            "id": str(file["_id"]),
            "name": file["filename"],
            "size": round(file["length"] / 1024, 2),  # в КБ
            "chunks": chunks_count
        })
    return render_template("index.html", files=files)

@app.route('/upload', methods=['POST'])
def upload_file():
    uploaded_file = request.files['file']
    if uploaded_file:
        fs.put(uploaded_file, filename=uploaded_file.filename)
    return redirect(url_for('index'))

@app.route('/download/<file_id>')
def download_file(file_id):
    from bson import ObjectId
    file = fs.get(ObjectId(file_id))
    return send_file(
        io.BytesIO(file.read()),
        as_attachment=True,
        download_name=file.filename
    )

@app.route('/delete/<file_id>')
def delete_file(file_id):
    from bson import ObjectId
    fs.delete(ObjectId(file_id))
    return redirect(url_for('index'))


if __name__ == '__main__':
    app.run(debug=True)
