import os
import io
from datetime import datetime
import mimetypes
from fastapi import File

import settings
from models import FileItem


class ContentBackend:
    def __init__(self):
        self.check_content_backend()
    
    #----
    def check_content_backend(self):
        if not os.path.isdir(settings.CONTENT_PATH):
            os.makedirs(settings.CONTENT_PATH)
    
    #----
    def get_content_list(self) -> list[FileItem]:
        res = []
        for filename in os.listdir(settings.CONTENT_PATH):
            file_path = os.path.join(settings.CONTENT_PATH, filename)
            if os.path.isfile(file_path):
                stats = os.stat(file_path)
                item = FileItem(
                    name=filename,
                    size=stats.st_size,
                    created=datetime.fromtimestamp(stats.st_ctime),
                    modified=datetime.fromtimestamp(stats.st_mtime),
                    type=mimetypes.guess_type(file_path)[0])
                res.append(item)
        return res

    #----
    def save_uploaded_content(self, filename:str, filebytes:bytes) -> FileItem:
        filename = filename
        save_path = os.path.join(settings.CONTENT_PATH, filename)
        with open(save_path, "wb") as f:
            f.write(filebytes)

        stats = os.stat(save_path)
        item = FileItem(
            name=filename,
            size=stats.st_size,
            created=datetime.fromtimestamp(stats.st_ctime),
            modified=datetime.fromtimestamp(stats.st_mtime),
            type=mimetypes.guess_type(save_path)[0]
        )
        return item

    #----
    def get_content_item(self, filename:str) -> FileItem:
        file_path = os.path.join(settings.CONTENT_PATH, filename)
        stats = os.stat(file_path)
        item = FileItem(
            name=filename,
            size=stats.st_size,
            created=datetime.fromtimestamp(stats.st_ctime),
            modified=datetime.fromtimestamp(stats.st_mtime),
            type=mimetypes.guess_type(file_path)[0])
        return item
    #----
    def get_content_bio(self, filename:str) -> io.BytesIO:
        file_path = os.path.join(settings.CONTENT_PATH, filename)
        data = open(file_path, "rb")
        return io.BytesIO(data.read())
    
    #----
    def delete_content_item(self, filename:str):
        save_path = os.path.join(settings.CONTENT_PATH, filename)
        os.unlink(save_path)
        
    #----