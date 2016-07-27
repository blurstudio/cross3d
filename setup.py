import os
import pypandoc
from setuptools import setup

# See https://packaging.python.org/distributing/#entry-points.
setup(
    name='cross3d',
    description='A unified API allowing to interact with multiple 3D content creation packages.',
    long_description=pypandoc.convert(os.path.join(os.path.abspath(os.path.dirname(__file__)), 'README.md'), 'rst'),
    url='https://github.com/blurstudio/cross3d',
    author='Blur Studio',
    author_email='github@blurstudio.com',
    license='GPL',

    # Versions should comply with PEP440.
    version='0.1.0',

    # See https://pypi.python.org/pypi?%3Aaction=list_classifiers.
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'Topic :: Artistic Software',
        'License :: OSI Approved :: GNU General Public License (GPL)',
        'Programming Language :: Python :: 2.7',
    ],

    keywords='3d autodesk dcc vfx python qt 3dmax softimage xsi maya motionbuilder',
    packages=['cross3d', 'cross3d.abstract', 'cross3d.maya', 'cross3d.studiomax', 'cross3d.softimage', 'cross3d.motionbuilder', 'cross3d.migrate', 'cross3d.classes'],

    # See https://packaging.python.org/en/latest/requirements.html,
    install_requires=[],
)
