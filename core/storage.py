from django.contrib.staticfiles.storage import StaticFilesStorage

try:
    from whitenoise.storage import CompressedManifestStaticFilesStorage

    class WhiteNoiseStaticFilesStorage(CompressedManifestStaticFilesStorage):
        """
        WhiteNoise storage that compresses static assets and generates a manifest,
        but falls back gracefully to un-hashed URLs instead of raising ValueError
        when a file is not yet compiled in the manifest (e.g. during test runs).
        """
        manifest_strict = False
except ImportError:
    class WhiteNoiseStaticFilesStorage(StaticFilesStorage):
        manifest_strict = False
