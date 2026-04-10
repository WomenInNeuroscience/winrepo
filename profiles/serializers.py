
from rest_framework import serializers

from .models import Profile, Country


class CountrySerializer(serializers.ModelSerializer):
    profiles_count = serializers.IntegerField(read_only=True)

    class Meta:
        model = Country
        fields = ('id', 'name', 'profiles_count')


class ProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = Profile
        fields = ('id', 'name')


class ProfileSearchSerializer(serializers.ModelSerializer):
    country_name = serializers.CharField(source='country.name', default='')
    country_is_under_represented = serializers.BooleanField(
        source='country.is_under_represented', default=False,
    )
    username = serializers.CharField(source='user.username', default=None)
    recommendation_count = serializers.IntegerField(read_only=True)
    modalities_display = serializers.SerializerMethodField()
    domains_display = serializers.SerializerMethodField()

    class Meta:
        model = Profile
        fields = (
            'id', 'name', 'position', 'institution',
            'country_name', 'country_is_under_represented',
            'modalities_display', 'domains_display', 'keywords',
            'username', 'recommendation_count',
        )

    def get_modalities_display(self, obj):
        return ', '.join(obj.modalities_labels()) if obj.modalities else ''

    def get_domains_display(self, obj):
        return ', '.join(obj.domains_labels()) if obj.domains else ''


class PositionsCountSerializer(serializers.ModelSerializer):
    profiles_count = serializers.IntegerField()

    class Meta:
        model = Profile
        fields = ('position', 'profiles_count')
