from setuptools import setup

setup(name='blondel_communities',
      version='0.1',
      description='An implementation of the Blondel et al. algorithm for detecting communities in graphs',
      url='http://github.com/aled1027/communities',
      author='Alex Ledger',
      author_email='a.led1027@gmail.com',
      license='MIT',
      packages=['blondel_communities'],
      install_requires=['networkx', 'numpy']
      zip_safe=False)
