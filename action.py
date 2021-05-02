#!/usr/bin/python
# encoding: utf-8
import sys

from workflow import Workflow3
import webbrowser

def main(wf):
    args = wf.args[0].split()
    command = args[0]

    if command == 'login':
        token = args[-1]
        wf.store_data('token', token)
        wf.logger.debug('==> Stored token is: %s', token)

    if command == 'config':
        base_url = args[-1]
        wf.store_data('base_url', base_url)
        wf.logger.debug('==> Stored base_url is: %s', base_url)

    if command == 'update':
        wf.start_update()

    if command == 'open':
        webbrowser.open(args[-1])


if __name__ == '__main__':
    update_settings = {
        'github_slug': 'joest67/alfred-yuque-workflow',
        'frequency'  : 1
    }
    wf3 = Workflow3(update_settings=update_settings)
    sys.exit(wf3.run(main))
