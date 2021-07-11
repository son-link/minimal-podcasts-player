from setuptools import setup

setup(
    name="minimal-podcasts-player",
    version="0.3.1",
    description="Subscribe, listen and (in the future) download your favorite podcasts, quickly and easily.",
    author="Alfonso Saavedra 'Son Link'",
    author_email='sonlink.dourden@gmail.com',
    license="GPL 3.0",
    url="https://github.com/son-link/minimal-podcasts-player",
    scripts=['bin/minimal-podcasts-player'],
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
    },
    download_url='https://github.com/son-link/minimal-podcasts-player/archive/0.3.1.tar.gz',
    keywords=['podcasts', 'audio', 'stream'],
    install_requires=[
        'pyqt5',
        'podcastparser',
    ],
    classifiers=[
        'Development Status :: 4 - Beta',
        'Environment :: X11 Applications :: Qt',
        'Topic :: Multimedia :: Sound/Audio',
        'Topic :: Multimedia :: Sound/Audio :: Players',
        'License :: OSI Approved :: GNU General Public License v3 or later (GPLv3+)',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Intended Audience :: End Users/Desktop',
        'Operating System :: OS Independent'
    ],
)
