from rest_framework import serializers
from draceditor.utils import markdownify
from .models import Article

class ArticleSerializer(serializers.ModelSerializer):
    html_content = serializers.SerializerMethodField()
    class Meta:
        model = Article
        fields = ('id', 'title', 'creation_date', 'html_content', 'track_type', 'bbox')

    def get_html_content(self, obj):
        if obj.content_type == "html":
            return obj.html_content
        elif obj.content_type == "md":
            return markdownify(obj.markdown_content)
        else:
            raise ValueError("Unknown content type: '{0}'".format(obj.content_type))