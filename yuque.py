#!/usr/bin/python
# encoding: utf-8
import re
import sys
import urllib

from workflow import Workflow3, web

YUQUE_BASE_URL = 'https://yuque.com'
PAGE_SIZE = 20


def query_doc(wf, query):
    wf.logger.debug('==> query: %s', query)
    if len(query) <= 0 or query.strip() <= 0:
        wf.add_item(u'输入无效')
        return

    match = re.match(r'(!?)(\S+) ?(\+)?(?(2)([0-9]*)$|$)', query)
    if match is None:
        wf.add_item(u'输入无效', subtitle=query)
        return

    related, content, _, page = map(lambda x: x.strip() if x is not None else x, match.groups())

    wf.logger.debug('==> params: %s, %s, %s', related, content, page)

    token = wf.stored_data('token')
    base_url = wf.stored_data('base_url') or YUQUE_BASE_URL
    headers = {
        'X-Auth-Token': token
    }
    offset = 1 if (page is None or len(page) <= 0) else int(page)
    params = {
        "type": 'doc',
        "q": urllib.quote(content.encode('utf-8')),
        "offset": str(offset)
    }
    if related == '!':
        params['related'] = 'true'
    url = '%s/api/v2/search' % base_url.strip("/")
    wf.logger.debug('==> url: %s, param: %s', url, params)

    resp = web.get(url, params=params, headers=headers)
    if resp.status_code == 200:
        total = resp.json()['meta']['total']
        # 查询结果为空
        if total == 0:
            wf.add_item(u'没有符合条件的查询结果')

        data = resp.json()['data']
        wf.logger.debug('==> query = %s, page size: %s, got result: %s', query, len(data), total)

        # 构建查询结果选择列表
        eof = True if len(data) < 20 else False
        autocomplete = '' if eof else u'%s +%s' % (content, offset + 1)
        for doc in data:
            book_name = doc['target']['book']['name']
            title = clean_hilight(doc['title'])
            title = '%s - %s' % (book_name, title)
            subtitle = clean_hilight(doc['summary'])
            wf.add_item(title,
                        subtitle=subtitle,
                        arg='open %s%s' % (base_url, doc['url']),
                        autocomplete=autocomplete,
                        valid=True)
        setattr(wf, "offset", offset + 1)
    # 未授权
    elif resp.status_code == 401:
        wf.add_item('Error: Unauthorized', autocomplete='> login ')

    else:
        wf.add_item('Error: Unknow', subtitle=url)


def action_list(wf, query):
    args = query.split()
    command = args[1] if len(args[0]) == 1 and len(args) > 1 else args[0][1:]

    if command in 'login':
        valid = bool(re.match(r'^>\s*login\s+\w+$', query))
        wf.add_item('> login <Access token>',
                    subtitle=u'设置语雀 AccessToken',
                    arg='login %s' % args[-1],
                    autocomplete='> login ',
                    valid=valid)

    if command in 'config':
        valid = bool(re.match(r'^>\s*config\s+\w+$', query))
        wf.add_item('> config <Base URL>',
                    subtitle=u'配置',
                    arg='config %s' % args[-1],
                    autocomplete='> config ',
                    valid=valid)

    if command in 'update':
        wf.add_item('> update',
                    subtitle=u'检查更新',
                    arg='update',
                    autocomplete='> update ',
                    valid=True)


def clean_hilight(text):
    text = re.sub(r'<em>', '', text)
    text = re.sub(r'</em>', '', text)
    return text


def main(wf):
    query = wf.args[0]
    if query.startswith('>'):
        action_list(wf, query)
    else:
        query_doc(wf, query)

    wf.send_feedback()


if __name__ == '__main__':
    update_settings = {
        'github_slug': 'joest67/alfred-yuque-workflow',
        'frequency': 1,
    }
    wf3 = Workflow3(update_settings=update_settings)
    # 更新
    if wf3.update_available:
        wf3.start_update()
    sys.exit(wf3.run(main))
