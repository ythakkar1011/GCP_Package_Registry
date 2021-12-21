import os
import uuid

import flask
import flask.testing
from google.cloud import storage
import pytest
import requests
from six import BytesIO

import main


@pytest.fixture
def client() -> flask.testing.FlaskClient:
    main.app.testing = True
    return main.app.test_client()


def test_index(client: flask.testing.FlaskClient) -> None:
    r = client.get('/')
    assert r.status_code == 200


@pytest.fixture(scope="module")
def blob_name() -> str:
    name = f"gae-flex-storage-{uuid.uuid4()}"
    yield name

    bucket = storage.Client().bucket(os.environ["CLOUD_STORAGE_BUCKET"])
    blob = bucket.blob(name)
    blob.delete()


def test_upload(client: flask.testing.FlaskClient, blob_name: str) -> None:
    # Upload a simple file
    file_content = b"This is some test content."

    r = client.post(
        '/upload',
        data={
            'file': (BytesIO(file_content), blob_name)
        }
    )

    assert r.status_code == 200

    # The app should return the public cloud storage URL for the uploaded
    # file. Download and verify it.
    cloud_storage_url = r.data.decode('utf-8')
    r = requests.get(cloud_storage_url)
    assert r.text.encode('utf-8') == file_content
