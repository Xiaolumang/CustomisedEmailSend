import os
import re
x = re.search(r'.+(?=@)','fenglu.cai@salvationarmy.org.au').group(0)
x = x.replace('.',' ')
print(x.title())
