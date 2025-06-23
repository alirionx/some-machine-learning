import mimetypes
import io
from fastapi import File
from minio import Minio

import settings
from models import FileItem


class ContentBackend:
    def __init__(self):
        self.client = None
        self.create_minio_client()
        self.check_content_backend()
    
    #----
    def create_minio_client(self):
        client = Minio(
            endpoint=settings.CONTENT_MINIO_ENDPOINT, 
            access_key=settings.CONTENT_MINIO_ACCESSKEY, 
            secret_key=settings.CONTENT_MINIO_SECRETKEY, 
            secure=settings.CONTENT_MINIO_SECURE,
            cert_check=False)
        self.client = client
    
    #----
    def check_content_backend(self):
        if not self.client.bucket_exists(settings.CONTENT_MINIO_BUCKET):
            self.client.make_bucket(settings.CONTENT_MINIO_BUCKET)
    
    #----
    def get_content_list(self) -> list[FileItem]:
        res = []
        object_list = self.client.list_objects(settings.CONTENT_MINIO_BUCKET)

        for obj in object_list:
            if not obj.is_dir:
                stats = self.client.stat_object(settings.CONTENT_MINIO_BUCKET, obj.object_name)
                item = FileItem(
                    name=obj.object_name,
                    size=obj.size,
                    created=obj.last_modified,
                    modified=obj.last_modified,
                    type=stats.content_type )
                res.append(item)
        return res

    #----
    def save_uploaded_content(self, filename:str, filebytes:bytes) -> FileItem:
        content_type = mimetypes.guess_type(filename)[0] or "application/octet-stream"
        self.client.put_object(
            bucket_name=settings.CONTENT_MINIO_BUCKET,
            object_name=filename,
            data=io.BytesIO(filebytes),
            length=len(filebytes),
            content_type=content_type
        )
        stats = self.client.stat_object(settings.CONTENT_MINIO_BUCKET, filename)
        item = FileItem(
            name=filename,
            size=stats.size,
            created=stats.last_modified,
            modified=stats.last_modified,
            type=stats.content_type
        )
        return item

    #----
    def get_content_item(self, filename:str) -> io.BytesIO:
        response = self.client.get_object(
            bucket_name=settings.CONTENT_MINIO_BUCKET, object_name=filename)
        data = response.read()
        response.close()
        response.release_conn()
        return io.BytesIO(data)
    
    #----
    def delete_content_item(self, filename:str):
        self.client.stat_object(
            bucket_name=settings.CONTENT_MINIO_BUCKET, object_name=filename)
        self.client.remove_object(
            bucket_name=settings.CONTENT_MINIO_BUCKET, object_name=filename)
        
    #----