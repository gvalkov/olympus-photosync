from setuptools import setup, find_packages


classifiers = [
    'Development Status :: 5 - Production/Stable',
    'Programming Language :: Python :: 3',
    'Programming Language :: Python :: 3.3',
    'Programming Language :: Python :: 3.4',
    'Programming Language :: Python :: 3.5',
    'Programming Language :: Python :: 3.6',
    'License :: OSI Approved :: BSD License',
]

requirements = [
    'tqdm'
]

entry_points = {
    'console_scripts': [
        'olympus-photosync = olympusphotosync.cli:main',
        'olympus-photosync-gui = olympusphotosync.gui:main'
    ]
}

extras_require = {
    'test': [
        'tox >= 2.6.0',
        'pytest >= 3.0.3',
        'pytest-cov >= 2.3.1',
    ],
    'devel': [
        'bumpversion >= 0.5.2',
        'check-manifest >= 0.35',
        'readme-renderer >= 16.0',
        'bottle',
    ]
}

kw = {
    'name':                 'olympus-photosync',
    'version':              '1.0.0',

    'description':          'Sync photos from WiFi enabled Olympus cameras',
    'long_description':     open('README.rst').read(),

    'author':               'Georgi Valkov',
    'author_email':         'georgi.t.valkov@gmail.com',
    'license':              'Revised BSD License',
    'keywords':             'olympus camera sync',
    'url':                  'https://github.com/gvalkov/olympus-photosync',
    'classifiers':          classifiers,
    'extras_require':       extras_require,
    'python_requires':      '>=3.3',
    'packages':             find_packages(),
    'entry_points':         entry_points,
    'zip_safe':             True,
}


if __name__ == '__main__':
    setup(**kw)
