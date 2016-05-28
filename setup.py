from setuptools import setup

setup(name='girvan_newman_communities',
      version='0.1',
      description='An implementation of the girvan-newman algorithm for detecting communities in graphs',
      url='http://github.com/aled1027/girvan_newman_communities',
      author='Alex Ledger',
      author_email='a.led1027@gmail.com',
      license='MIT',
      packages=['girvan_newman_communities'],
      install_requires=['networkx', 'numpy']
      zip_safe=False)
