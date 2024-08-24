from ansible.plugins.lookup import LookupBase
import os
import hashlib
import pwd
import grp
import time
from typing import List, Dict, Any, Optional

DOCUMENTATION = '''
---
name: stat
author: "LE MEUR Ghislain"
version_added: "1.0.0"
short_description: Retrieves file or directory status and attributes.
description:
  - This lookup returns file or directory status information.
  - It can retrieve various attributes such as file size, ownership, permissions, and timestamps.
  - Optionally, it can calculate a checksum for the file content.
options:
  _terms:
    description:
      - List of file or directory paths to retrieve status information for.
    required: True
  follow:
    description:
      - Whether to follow symlinks.
    type: bool
    default: False
  get_checksum:
    description:
      - Whether to compute the file's checksum.
    type: bool
    default: False
  checksum_algorithm:
    description:
      - Algorithm to use for checksum calculation. Only applicable if I(get_checksum) is set to True.
    type: str
    choices: ['md5', 'sha1', 'sha256']
    default: 'sha1'
'''

EXAMPLES = '''
- name: Get the status of a single file
  debug:
    msg: "{{ lookup('stat', '/path/to/file') }}"

- name: Get status of multiple files
  debug:
    msg: "{{ lookup('stat', '/path/to/file1', '/path/to/file2') }}"

- name: Get status and compute SHA256 checksum
  debug:
    msg: "{{ lookup('stat', '/path/to/file', get_checksum=True, checksum_algorithm='sha256') }}"

- name: Get status without following symlinks
  debug:
    msg: "{{ lookup('stat', '/path/to/symlink', follow=False) }}"
'''

RETURN = '''
_list:
  description:
    - List of dictionaries containing status information for each path.
  type: list
  elements: dict
  contains:
    exists:
      description: Whether the file or directory exists.
      type: bool
      returned: always
    size:
      description: Size of the file in bytes.
      type: int
      returned: when file exists
    uid:
      description: User ID of the file owner.
      type: int
      returned: when file exists
    gid:
      description: Group ID of the file owner.
      type: int
      returned: when file exists
    mode:
      description: File mode (permissions) as an octal string.
      type: str
      returned: when file exists
    permissions:
      description: Detailed permissions broken down by owner, group, and others.
      type: dict
      returned: when file exists
    atime:
      description: Last access time.
      type: float
      returned: when file exists
    mtime:
      description: Last modification time.
      type: float
      returned: when file exists
    ctime:
      description: Last status change time.
      type: float
      returned: when file exists
    isdir:
      description: Whether the path is a directory.
      type: bool
      returned: when file exists
    isfile:
      description: Whether the path is a file.
      type: bool
      returned: when file exists
    islink:
      description: Whether the path is a symlink.
      type: bool
      returned: when file exists
    is_readable:
      description: Whether the path is readable.
      type: bool
      returned: when file exists
    is_writable:
      description: Whether the path is writable.
      type: bool
      returned: when file exists
    is_executable:
      description: Whether the path is executable.
      type: bool
      returned: when file exists
    owner:
      description: Username of the file owner.
      type: str
      returned: when file exists
    group:
      description: Group name of the file owner.
      type: str
      returned: when file exists
    num_links:
      description: Number of hard links.
      type: int
      returned: when file exists
    last_modified:
      description: Last modification time as a string.
      type: str
      returned: when file exists
    checksum:
      description: Checksum of the file (if requested).
      type: str
      returned: when get_checksum=True and file exists
'''

class LookupModule(LookupBase):
  def run(self, terms: List[str], variables: Optional[Dict[str, Any]] = None, **kwargs: Any) -> List[Dict[str, Any]]:
    results: List[Dict[str, Any]] = []

    for term in terms:
      stat_result: Dict[str, Any] = self._get_stat(term, kwargs.get('follow', False))

      if kwargs.get('get_checksum', False) and stat_result.get('exists', False):
        stat_result['checksum'] = self._compute_checksum(term, kwargs.get('checksum_algorithm', 'sha1'))

      results.append(stat_result)

    return results

  def _get_stat(self, path: str, follow: bool = False) -> Dict[str, Any]:
    try:
      stat_info: os.stat_result
      if follow:
        stat_info = os.stat(path)
      else:
        stat_info = os.lstat(path)

      file_mode: int = stat_info.st_mode
      permissions: Dict[str, bool] = {
        'owner_readable': bool(file_mode & 0o400),
        'owner_writable': bool(file_mode & 0o200),
        'owner_executable': bool(file_mode & 0o100),
        'group_readable': bool(file_mode & 0o040),
        'group_writable': bool(file_mode & 0o020),
        'group_executable': bool(file_mode & 0o010),
        'other_readable': bool(file_mode & 0o004),
        'other_writable': bool(file_mode & 0o002),
        'other_executable': bool(file_mode & 0o001),
        'sticky': bool(file_mode & 0o1000),
        'setuid': bool(file_mode & 0o4000),
        'setgid': bool(file_mode & 0o2000),
      }

      try:
        owner_name: str = pwd.getpwuid(stat_info.st_uid).pw_name
      except KeyError:
        owner_name = str(stat_info.st_uid)

      try:
        group_name: str = grp.getgrgid(stat_info.st_gid).gr_name
      except KeyError:
        group_name = str(stat_info.st_gid)

      return {
        'exists': True,
        'size': stat_info.st_size,
        'uid': stat_info.st_uid,
        'gid': stat_info.st_gid,
        'mode': int(f'{file_mode & 0o7777:o}'),
        'permissions': permissions,
        'atime': stat_info.st_atime,
        'mtime': stat_info.st_mtime,
        'ctime': stat_info.st_ctime,
        'isdir': os.path.isdir(path),
        'isfile': os.path.isfile(path),
        'islink': os.path.islink(path),
        'is_readable': os.access(path, os.R_OK),
        'is_writable': os.access(path, os.W_OK),
        'is_executable': os.access(path, os.X_OK),
        'owner': owner_name,
        'group': group_name,
        'num_links': stat_info.st_nlink,
        'last_modified': time.ctime(stat_info.st_mtime)
      }
    except FileNotFoundError:
      return {
        'exists': False,
      }

  def _compute_checksum(self, path: str, algorithm: str = 'sha1') -> Optional[str]:
    hash_func: hashlib._Hash = hashlib.new(algorithm)

    try:
      with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
          hash_func.update(chunk)
      return hash_func.hexdigest()
    except (OSError, IOError):
      return None
