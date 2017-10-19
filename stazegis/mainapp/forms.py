import django.forms as forms
from django.forms.widgets import PasswordInput
from django.core.files.uploadedfile import TemporaryUploadedFile
import uuid
import datetime
from .models import Article
from geo.geo import gpx_to_wkt
from django.contrib.gis.geos import GEOSGeometry
from draceditor.fields import DraceditorFormField

class UserRegisterForm(forms.Form):
    email = forms.CharField(label="Email address")
    first_name = forms.CharField(label="Name")
    password = forms.CharField(widget=PasswordInput())
    confirm_password = forms.CharField(widget=PasswordInput())

    def clean(self):
        if self.cleaned_data.get("password") != self.cleaned_data.get("confirm_password"):
            raise forms.ValidationError("Two different passwords were entered")

class ArticleForm(forms.Form):
    title = forms.CharField(label="Title")
    track_type = forms.ChoiceField(choices=(("PED", "Pedestrian"),("CYC","Cycling")))
    markdown_content = DraceditorFormField(label="Description")
    gpx_file = forms.FileField()

    def save(self, commit=True):
        id = uuid.uuid4()
        creation_date = datetime.datetime.now()
        # Non-visible, admin needs to approve
        is_visible = False
        # Content type is Markdown
        markdown_content = self.cleaned_data["markdown_content"]
        # The following assert checks that the TemporaryFileUploadHandler has handled the upload.
        # This needs to be the case for the file to be read by GDAL.
        assert isinstance(self.cleaned_data['gpx_file'], TemporaryUploadedFile)
        uploaded_file_path = self.cleaned_data['gpx_file'].temporary_file_path()

        # Save file to Azure
        # azure_storage = AzureStorage()
        # azure_storage.save(str(id)+'.gpx', open(uploaded_file_path, 'rb'))

        # Convert the GPX TemporaryUploadedFile to WKT
        geom = GEOSGeometry(gpx_to_wkt(uploaded_file_path))

        # Calculate elevation profile with Google Elevation Service
        # elevation_json = gpx_to_elev(open(uploaded_file_path, 'rb'))

        # Save to database
        instance = Article(
            id=id,
            title=title,
            track_type=track_type,
            creation_date=creation_date,
            is_visible=is_visible,
            content_type='md',
            markdown_content=markdown_content,
            geom=geom
        )
        instance.save()

        # Compute bounding box
        instance.compute_bbox()