# /// script
# requires-python = ">=3.11"
# dependencies = ["keyring>=25,<26"]
# ///
"""Local command-line client for a teacher's own research contributions."""

import argparse
from getpass import GetPassWarning, getpass
from http.client import HTTPException
import json
from pathlib import Path
import re
import sys
from urllib.error import HTTPError
from urllib.parse import urlsplit
from urllib.request import HTTPRedirectHandler, ProxyHandler, Request, build_opener
from uuid import uuid4
import warnings


DEFAULT_BASE = 'https://118.196.149.115:8430'
CONTRIBUTIONS = '/oi/api/me/research-contributions'
KEYRING_SERVICE = 'cn.org.scion.cz-long.research-profile'
KEYRING_ACCOUNT = 'research-api'
TOKEN_PATTERN = re.compile(r'czl_sk_[A-Za-z0-9_-]{43}')
LOOPBACK = {'localhost', '127.0.0.1', '::1'}


class ClientError(Exception):
    pass


class NoRedirect(HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def credential_store():
    try:
        if sys.platform == 'darwin':
            from keyring.backends.macOS import Keyring
            return Keyring()
        if sys.platform == 'win32':
            from keyring.backends.Windows import WinVaultKeyring
            return WinVaultKeyring()
    except ImportError:
        raise ClientError('无法加载系统凭据库，请使用 uv run --script 运行。') from None
    raise ClientError('当前版本支持 macOS 钥匙串和 Windows 凭据管理器。')


def base_url(value):
    url = urlsplit(value)
    local_http = url.scheme == 'http' and url.hostname in LOOPBACK
    if ((url.scheme != 'https' and not local_http) or not url.hostname or url.username is not None
            or url.password is not None or url.query or url.fragment
            or any(char.isspace() or char == '\\' for char in value)):
        raise ClientError('请使用服务的 HTTPS 地址。本机可用 localhost 的 HTTP 地址。')
    return value.rstrip('/')


def request(config, path=CONTRIBUTIONS, body=None):
    headers = {'Accept': 'application/json', 'Authorization': 'Bearer ' + config['token']}
    data = None
    if body is not None:
        headers['Content-Type'] = 'application/json'
        data = json.dumps(body, ensure_ascii=False).encode('utf-8')
    query = Request(config['base_url'] + path, data=data, headers=headers)
    handlers = [NoRedirect()]
    if query.type == 'http':
        handlers.append(ProxyHandler({}))
    try:
        with build_opener(*handlers).open(query, timeout=20) as response:
            result = json.load(response)
    except HTTPError as error:
        with error:
            if error.code == 401:
                raise ClientError('令牌无效或已失效，请在创智龙生成新令牌后重新配置。') from None
            if 300 <= error.code < 400:
                raise ClientError('服务返回重定向，请检查配置的 HTTPS 地址和部署前缀。') from None
            try:
                detail = json.load(error).get('detail')
            except (ValueError, AttributeError):
                detail = None
            message = detail if isinstance(detail, str) else '请求失败，请检查服务状态。'
            raise ClientError(f'HTTP {error.code}，{message.replace(config["token"], "[令牌]")}') from None
    except (OSError, HTTPException):
        raise ClientError('未收到服务响应。若刚保存或送审，请先用 list 核对结果。') from None
    except ValueError:
        raise ClientError('服务未返回预期的 JSON，请检查地址和部署版本。') from None
    if not isinstance(result, dict):
        raise ClientError('服务返回的数据格式有误。')
    return result


def listing(config):
    data = request(config)
    profile = data.get('profile')
    if (not isinstance(profile, dict) or not profile.get('id') or not profile.get('name')
            or type(data.get('binding_revision')) is not int
            or not isinstance(data.get('items'), list) or not isinstance(data.get('archive'), list)):
        raise ClientError('服务未返回完整档案，请确认已部署科研资料 API。')
    if config.get('profile_id', profile['id']) != profile['id']:
        raise ClientError('服务返回的档案与配置不符，请重新配置并核对姓名。')
    return data


def configure(store, url):
    url = base_url(url)
    if not sys.stdin.isatty():
        raise ClientError('请导师在本机终端运行 configure，并按提示粘贴令牌。')
    with warnings.catch_warnings():
        warnings.simplefilter('error', GetPassWarning)
        try:
            token = getpass('粘贴创智龙 API 令牌（输入不显示）：').strip()
        except GetPassWarning:
            raise ClientError('此终端无法隐藏令牌输入。请改用本机终端。') from None
    if not TOKEN_PATTERN.fullmatch(token):
        raise ClientError('令牌格式有误，请复制创智龙生成的完整令牌。')
    config = {'base_url': url, 'token': token}
    data = listing(config)
    config['profile_id'] = data['profile']['id']
    try:
        store.set_password(KEYRING_SERVICE, KEYRING_ACCOUNT, json.dumps(config))
    except Exception:
        raise ClientError('无法写入本机凭据库，请检查系统凭据库权限。') from None
    return connection_summary(data)


def load_config(store):
    try:
        saved = store.get_password(KEYRING_SERVICE, KEYRING_ACCOUNT)
    except Exception:
        raise ClientError('无法读取本机凭据库，请检查系统凭据库权限。') from None
    if not saved:
        raise ClientError('尚未配置令牌，请导师先运行 configure。')
    try:
        config = json.loads(saved)
        config['base_url'] = base_url(config['base_url'])
        if TOKEN_PATTERN.fullmatch(config['token']) and config['profile_id']:
            return config
    except (KeyError, TypeError, ValueError, ClientError):
        pass
    raise ClientError('本机令牌配置有误，请重新运行 configure。')


def connection_summary(data):
    return {'profile': data['profile'], 'binding_revision': data['binding_revision'],
            'archived_count': len(data['archive']), 'record_count': len(data['items'])}


def record_for(data, item_id):
    for item in data['items']:
        if item['id'] == item_id:
            return item
    for item in data['archive']:
        if item['id'] == item_id:
            linked = [row for row in data['items'] if row.get('archive_id') == item['source_id']]
            if len(linked) > 1:
                raise ClientError('该档案成果有多条关联记录，请核对后指定要编辑的记录 ID。')
            return linked[0] if linked else item
    raise ClientError('没有找到该成果 ID，请重新查询。')


def plan_save(config, data, change):
    patch = change.get('fields')
    if not isinstance(patch, dict) or not patch or not all(isinstance(value, str) for value in patch.values()):
        raise ClientError('请提供至少一个要修改的字段，字段值须为字符串。')
    if 'id' in change:
        item = record_for(data, change['id'])
    else:
        item = {'id': str(uuid4()), 'kind': change.get('kind'), 'revision': 0, 'fields': {}}
    if item['kind'] not in {'paper', 'project'} or change.get('kind', item['kind']) != item['kind']:
        raise ClientError('请核对成果类型，kind 须为 paper 或 project。')
    if item.get('status') == 'pending':
        raise ClientError('这条成果正在审核，请等审核结束后再修改。')
    payload = {'id': item['id'], 'kind': item['kind'], 'revision': item['revision'],
               'binding_revision': data['binding_revision'], 'fields': {**item['fields'], **patch}}
    if item.get('source_id'):
        payload['source_id'] = item['source_id']
    return {'action': 'save', 'base_url': config['base_url'], 'profile': data['profile'],
            'changes': {field: {'before': item['fields'].get(field, ''), 'after': value}
                        for field, value in patch.items()}, 'request': payload}


def plan_submit(config, data):
    drafts = [item for item in data['items'] if item['status'] == 'draft']
    if not drafts:
        raise ClientError('没有待提交的成果草稿。')
    items = [{'id': item['id'], 'revision': item['revision']} for item in drafts]
    return {'action': 'submit', 'base_url': config['base_url'], 'profile': data['profile'],
            'drafts': [{**item, 'kind': draft['kind'],
                        'name': draft['fields'].get('title') or draft['fields'].get('name', '')}
                       for item, draft in zip(items, drafts)],
            'request': {'operation_id': str(uuid4()), 'binding_revision': data['binding_revision'], 'items': items}}


def apply_plan(config, action, plan):
    profile = plan.get('profile')
    if (plan.get('action') != action or not isinstance(plan.get('request'), dict)
            or not isinstance(profile, dict)):
        raise ClientError('请传入对应的完整保存或送审计划。')
    if plan.get('base_url') != config['base_url'] or profile.get('id') != config['profile_id']:
        raise ClientError('当前配置与计划的服务或档案不同，请重新生成计划并确认。')
    payload = plan['request']
    if action == 'save':
        return request(config, body=payload)
    result = request(config, CONTRIBUTIONS + '/submit', body=payload)
    submitted_ids = {item['id'] for item in payload['items']}
    return {'items': [item for item in result['items'] if item['id'] in submitted_ids]}


def read_input(path):
    try:
        content = sys.stdin.buffer.read() if path == '-' else Path(path).read_bytes()
        data = json.loads(content)
    except (OSError, ValueError):
        raise ClientError('无法读取 JSON，请提供 UTF-8 JSON 文件或通过标准输入传入。') from None
    if not isinstance(data, dict):
        raise ClientError('请输入 JSON 对象。')
    return data


def main():
    parser = argparse.ArgumentParser(description='维护创智龙本人论文与项目')
    commands = parser.add_subparsers(dest='command', required=True)
    setup = commands.add_parser('configure', help='在终端配置令牌并核对档案')
    setup.add_argument('--base-url', default=DEFAULT_BASE)
    commands.add_parser('check', help='核对令牌关联的档案')
    commands.add_parser('list', help='读取本人档案和成果草稿')
    commands.add_parser('prepare-submit', help='预览全部待提交草稿')
    for command, help_text in (
        ('prepare-save', '合并字段，生成保存计划'),
        ('save', '执行已确认的保存计划'),
        ('submit', '执行已确认的送审计划'),
    ):
        commands.add_parser(command, help=help_text).add_argument('input', nargs='?', default='-')
    args = parser.parse_args()
    try:
        store = credential_store()
        if args.command == 'configure':
            result = configure(store, args.base_url)
        else:
            config = load_config(store)
            if args.command in {'save', 'submit'}:
                result = apply_plan(config, args.command, read_input(args.input))
            else:
                data = listing(config)
                if args.command == 'check':
                    result = connection_summary(data)
                elif args.command == 'prepare-save':
                    result = plan_save(config, data, read_input(args.input))
                elif args.command == 'prepare-submit':
                    result = plan_submit(config, data)
                else:
                    result = data
        print(json.dumps(result, ensure_ascii=False, indent=2))
    except (ClientError, ValueError, EOFError, KeyboardInterrupt) as error:
        print(str(error) if isinstance(error, ClientError) else '配置或操作已取消，或输入格式有误。', file=sys.stderr)
        return 1
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
