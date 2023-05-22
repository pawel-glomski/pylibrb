import sys

try:
  from skbuild import setup
  import nanobind
except ImportError:
  print(
      'The preferred way to invoke "setup.py" is via pip, as in "pip install .".'
      'If you wish to run the setup script directly, you must '
      'first install the build dependencies listed in pyproject.toml!',
      file=sys.stderr)
  raise

setup(
    packages=['pylibrb'],
    package_dir={'': 'src'},
    include_package_data=True,
    cmake_install_dir='src/pylibrb',
)
