import os
from flask import flash
from PIL import Image

from flask import current_app

def add_profile_pic(pic_upload,username):

    filename = pic_upload.filename
    # Erfassen Sie die Erweiterungsart .jpg oder .png
    ext_type = filename.split('.')[-1]
    storage_filename = str(username) + '.' +ext_type
    filepath = os.path.join(current_app.root_path, 'static\profile_pics', storage_filename)

    # Größe
    output_size = (200, 200)

    # Bild öffnen und speichern
    pic = Image.open(pic_upload)
    pic.thumbnail(output_size)
    pic.save(filepath)
    flash('Bild geändert!', 'success')


    return storage_filename
