import os
import uuid
import urllib.error
import urllib.parse
import urllib.request
from pathlib import PurePosixPath

from django.utils.text import slugify


def _supabase_config():
    supabase_url = os.environ.get("SUPABASE_URL")
    supabase_key = (
        os.environ.get("SUPABASE_SERVICE_ROLE_KEY")
        or os.environ.get("SUPABASE_KEY")
        or os.environ.get("SUPABASE_ANON_KEY")
    )

    if not supabase_url or not supabase_key:
        raise RuntimeError(
            "SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY are required for uploads."
        )

    return supabase_url.rstrip("/"), supabase_key


def upload_public_file(file_obj, folder, title):
    bucket = os.environ.get("SUPABASE_STORAGE_BUCKET", "epaper")
    supabase_url, supabase_key = _supabase_config()
    original_name = getattr(file_obj, "name", "upload")
    extension = PurePosixPath(original_name).suffix.lower()
    safe_title = slugify(title) or "edition"
    path = f"{folder}/{safe_title}-{uuid.uuid4().hex}{extension}"

    content = file_obj.read()
    content_type = getattr(file_obj, "content_type", None) or "application/octet-stream"

    encoded_path = "/".join(urllib.parse.quote(part) for part in path.split("/"))
    upload_url = (
        f"{supabase_url}/storage/v1/object/{urllib.parse.quote(bucket)}/{encoded_path}"
    )
    request = urllib.request.Request(
        upload_url,
        data=content,
        method="POST",
        headers={
            "Authorization": f"Bearer {supabase_key}",
            "apikey": supabase_key,
            "Content-Type": content_type,
            "x-upsert": "false",
        },
    )

    try:
        with urllib.request.urlopen(request, timeout=30):
            pass
    except urllib.error.HTTPError as exc:
        body = exc.read().decode("utf-8", errors="replace")
        raise RuntimeError(f"Supabase upload failed: {exc.code} {body}") from exc

    return (
        f"{supabase_url}/storage/v1/object/public/"
        f"{urllib.parse.quote(bucket)}/{encoded_path}"
    )
