# -*- coding: utf-8 -*-

from ansible.errors import AnsibleError
import re

#try:
#  import xxx
#  HAS_LIB = True
#except ImportError:
#  HAS_LIB = False

def my_custom_filter(text, surround='xXx'):
  #if not HAS_LIB:
  #  raise AnsibleError('You need to install "xxx" prior to running '
  #                     'mycustomfilter filter')
  return "{1} {0} {1}".format(text, surround)

class FilterModule(object):

  def filters(self):
    return {
      'mycustomfilter': my_custom_filter
    }
