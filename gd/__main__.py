"""Somewhat useful 'python -m gd' implementation"""

import argparse
import sys

import gd
import pkg_resources
import aiohttp
import PIL
import platform

con_v = '0.1.1'  # gd_console version

def show_version():
    entries = []

    entries.append('- Python v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'.format(sys.version_info))

    version_info = gd.version_info
    entries.append('- gd.py v{0.major}.{0.minor}.{0.micro}-{0.releaselevel}'.format(version_info))

    entries.append('- [gd_console] v{0}'.format(con_v))

    if version_info.releaselevel != 'final':
        pkg = pkg_resources.get_distribution('gd.py')
        if pkg:
            entries.append('    - gd.py pkg_resources: v{0}'.format(pkg.version))

    entries.append('- aiohttp v{0.__version__}'.format(aiohttp))

    entries.append('- Pillow (PIL) v{0.__version__}'.format(PIL))

    uname = platform.uname()
    entries.append('- System Info: {0.system} {0.release} {0.version}'.format(uname))

    print('\n'.join(entries))


def show_docs():
    _docs = 'https://gdpy.readthedocs.io/en/latest'

    print('- gd.py docs: [{}]'.format(_docs))

def main():
    # make parser
    parser = argparse.ArgumentParser(description='gd.py console commands', prog='gd')
    # add --version
    parser.add_argument('-v', '--version', help='show versions (gd.py, python, etc.)',
        action='store_true', default=False)
    # add --docs
    parser.add_argument('-d', '--docs', help='show links to gd.py docs',
        action='store_true', default=False)
    # parse args
    args = parser.parse_args()
    if args.version:
        show_version()
    if args.docs:
        show_docs()

# run main
main()
