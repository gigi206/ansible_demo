# lookup_plugins/stat.py

from ansible.plugins.lookup import LookupBase
import os
import hashlib
import pwd
import grp
import time

class LookupModule(LookupBase):
  def run(self, terms, variables=None, **kwargs):
    results = []

    for term in terms:
      stat_result = self._get_stat(term, kwargs.get('follow', False))

      if kwargs.get('get_checksum', False) and stat_result.get('exists'):
        stat_result['checksum'] = self._compute_checksum(term, kwargs.get('checksum_algorithm', 'sha1'))

      results.append(stat_result)

    return results

  def _get_stat(self, path, follow=False):
    try:
      if follow:
        stat_info = os.stat(path)
      else:
        stat_info = os.lstat(path)

      file_mode = stat_info.st_mode
      permissions = {
        'owner_readable': bool(file_mode & 0o400),
        'owner_writable': bool(file_mode & 0o200),
        'owner_executable': bool(file_mode & 0o100),
        'group_readable': bool(file_mode & 0o040),
        'group_writable': bool(file_mode & 0o020),
        'group_executable': bool(file_mode & 0o010),
        'other_readable': bool(file_mode & 0o004),
        'other_writable': bool(file_mode & 0o002),
        'other_executable': bool(file_mode & 0o001),
        'sticky': bool(file_mode & 0o1000)
      }

      try:
        owner_name = pwd.getpwuid(stat_info.st_uid).pw_name
      except KeyError:
        owner_name = str(stat_info.st_uid)

      try:
        group_name = grp.getgrgid(stat_info.st_gid).gr_name
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
        'is_readable': False,
        'is_writable': False,
        'is_executable': False,
        'owner': None,
        'group': None,
        'num_links': 0,
        'size_in_kb': 0,
        'size_in_mb': 0,
        'last_modified': None
      }

  def _compute_checksum(self, path, algorithm='sha1'):
    hash_func = hashlib.new(algorithm)

    try:
      with open(path, 'rb') as f:
        for chunk in iter(lambda: f.read(4096), b""):
          hash_func.update(chunk)
      return hash_func.hexdigest()
    except (OSError, IOError):
      return None
