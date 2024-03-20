__metaclass__ = type

DOCUMENTATION = """
    name: users
    author: Ghislain LE MEUR
    version_added: "1.0"
    short_description: get users
    description:
        - This lookup returns the users from /etc/passwd
    options:
      _terms:
        description: user to get details
        required: False
      attribute:
        description: return a specify attribute for the user
        type: string
        required: False
        default: None
"""


from ansible.errors import AnsibleError, AnsibleOptionsError
from ansible.plugins.lookup import LookupBase
from ansible.utils.display import Display
import pwd
# import grp

display = Display()

class LookupModule(LookupBase):
  def run(self, terms, variables=None, **kwargs):

    ret = []
    self.set_options(var_options=variables, direct=kwargs)

    for term in terms:
      display.debug(f"File lookup term: {term}")
      try:
        user = pwd.getpwuid(int(term))
        # display.vvv("File lookup term: %s" % term)
      except ValueError:
        try:
          user = pwd.getpwnam(term)
        except KeyError as e:
          # raise AnsibleError(f"user {term} not found => {e}")
          raise AnsibleOptionsError(f"user {term} not found => {e}")
      except Exception:
        pass

      if self.get_option("attribute"):
        try:
          user = getattr(user, self.get_option("attribute"))
        except AttributeError as e:
          raise AnsibleOptionsError(f"attribute {self.get_option('attribute')} doesn't exist => {e}")

      ret.append(user)

    if not terms:
      ret.append(pwd.getpwall())

    return ret
