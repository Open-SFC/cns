#/usr/bin/python
import re
import textwrap
import os

print "[LOG] Copying necessary source files..."
os.system("cp -rf cns/openstack_dashboard/admin/ofclusters /usr/share/openstack-dashboard/openstack_dashboard/dashboards/admin/")
os.system("cp -rf cns/openstack_dashboard/api/ofcontroller.py /usr/share/openstack-dashboard/openstack_dashboard/api/")

def apply_patch(path, line_pattern, pattern, replace_str, before=False):
   text = open( path ).read()
   match_found=False
   matches = re.finditer(line_pattern, text)
   m = None      # optional statement. just for clarification
   for m in matches:
      match_found=True
      pass       # just loop to the end
   
   if (match_found):
      m.start()  
      m.end()    
      exists = re.search(pattern, text)
      if not exists:
         if before:
            text1 = text[0:m.start()] + replace_str + text[(m.start()):]
         else:
            text1 = text[0:m.end()] + replace_str + text[(m.end()+0):]
         f = open(path, 'w+')
         f.write(text1)
         print "[PATCHED] Patched File '%s' with...'%s'" % (str(path), str(replace_str))
         f.close()
      else:
         print "[IGONORED] Patch Igonred for the file '%s': '%s' already there..." % (str(path), str(pattern))

print "[LOG] Patching Openstack Dashboard for CNS..."

####
path = '/usr/share/openstack-dashboard/openstack_dashboard/api/__init__.py'
line_pattern = r'from openstack_dashboard.api import \w+'
pattern = 'from openstack_dashboard.api import ofcontroller'
replace_str = textwrap.dedent("""
                              from openstack_dashboard.api import ofcontroller
                              """)
apply_patch(path, line_pattern, pattern, replace_str)

####
line_pattern = r'"\w+"\,'
pattern = '"ofcontroller",'
replace_str = "\n    " + '"ofcontroller",'
apply_patch(path, line_pattern, pattern, replace_str)

####
path = '/usr/share/openstack-dashboard/openstack_dashboard/dashboards/admin/dashboard.py'
replace_str = 'class CrdPanels(horizon.PanelGroup):\n'
replace_str = replace_str + '    slug = "crd"\n'
replace_str = replace_str + '    name = _("Cloud Resource Discovery")\n'
replace_str = replace_str + "    panels = ('ofclusters',)\n\n"
line_pattern = r'class Admin\(horizon\.Dashboard\)'
pattern = 'class CrdPanels'
apply_patch(path, line_pattern, pattern, replace_str, before=True)

####
replace_str = ' CrdPanels,'
line_pattern = r'Panels,'
pattern = 'CrdPanels,'
apply_patch(path, line_pattern, pattern, replace_str)