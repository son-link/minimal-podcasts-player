from setuptools import setup

setup(
    name="minimal-podcast-player",
    version="0.5.0",
    description="Play your favorite YouTube's music videos and playlist",
    author="Alfonso Saavedra 'Son Link'",
    author_email='sonlink.dourden@gmail.com',
    license="GPL 3.0",
    url="https://son-link.github.io",
    scripts=['bin/minimal-podcast-player'],
    packages=['mpp'],
    package_dir={'mpp': 'mpp'},
    package_data={'mpp': ['*', 'locales/*.qm', 'ui/*.py']},
    exclude_package_data={
        'mpp': [
            'icon.svg',
            'podcast-2665175.ai',
            'no-cover.svg',
            '*.json',
            '*.ts',
            'images.qrc',
            'icons',
            'mpp.db',
            'mpp.ini',
            'mpp.pro',
            'search.py'
        ]
    }
)
