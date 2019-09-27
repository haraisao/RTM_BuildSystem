
'''
   create Rtc Image by using SVG
'''
import sys
import os, os.path
import yaml
import html
import webbrowser


def rtc_doc(fname, arg_type="file"):
  profile=None
  if arg_type == "file":
    with open(fname, encoding="utf-8") as file:
      profile = yaml.load(file)
  else:
    profile=fname

  if not profile :
    print("=== No Profile")
    return None


  res='''
  <html>
   <head>
     <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
     <meta name="viewport" content="width=device-width,initial-scale=1.0" >
     <style>
      table, th, td {
       border-collapse: collapse;
       border: 1px solid #000;
       line-height: 1.5;
      }
      table th{
        background: #d9d9d9;
      }
     </style>
   </head>
  <body>
  '''

  res +="<h1>"+profile['name']+"</h1>"
  res += rtc_image(profile)

  res +="<h2>Profile</h2>"
  res += rtc_profile(profile)
  dp=rtc_dataport_table(profile)
  if dp:
    res +="<h2>Data Ports</h2>"
    res += dp

  sp = rtc_serviceport_table(profile)
  if sp :
    res +="<h2>Service Ports</h2>"
    res += sp
  cf=rtc_configuration_table(profile)
  if cf:
    res +="<h2>Configurations</h2>"
    res +=cf 
  res +="</body></html>"

  docname=profile['name']+".html"

  with open(docname, "w", encoding="utf-8") as file:
    file.write(res)

  webbrowser.open(docname)

#
#
#
def rtc_image(profile, view_w=600, pos0=260, align='center', style='', style2=''):
  res = ""
  if profile :
    pos=pos0
    n=0
    n_l=0
    n_r=0
    port_r=[]
    port_l=[]

    #  count data_ports
    if 'dataport' in profile:
      dataport = profile['dataport']
      for port in dataport:
        if port['flow'] == 'in' or port['flow'] == 'DataInPort':

          n_l += 1
          port_l.append(port)
          if n < n_l : n = n_l
        elif port['flow'] == 'out' or port['flow'] == 'DataOutPort':
          n_r += 1
          port_r.append(port)
          if n < n_r: n = n_r

    # count service_ports
    if 'serviceport' in profile and  profile['serviceport'] :
      serviceport = profile['serviceport']
      for port in serviceport :
        if port['flow'] == 'provider' :
          if 'place' in port and port['place'] == 'left':
            n_l += 1
            port_l.append(port)
            if n < n_l: n = n_l
          else:
            n_r += 1
            port_r.append(port)
            if n < n_r: n = n_r
  
        elif port['flow'] == 'consumer' :
          if 'place' in port and port['place'] == 'left':
            n_l += 1
            port_l.append(port)
            if n < n_l: n = n_l
          else:
            n_r += 1
            port_r.append(port)
            if n < n_r: n = n_r

    # Draw image
    port_h = 50
    height= 50 + port_h*(n -1)
    width=80

    view_h= height + 40

    rtc_name = profile['name']
    
    text_pos_x = pos + width/2
    text_pos_y = height + 30

    res='''
<p>
<div style="text-align:$align; $style2">
<svg width="$view_w" viewBox="0 0 $view_w $view_h" style="$style" >
     <defs>
        <path id="in_l" d="M0,0 h20 v20 h-20 L10,10Z" stroke="black" stroke-width="1" fill="green"/>
        <path id="out_r" d="M0,0 h10 L20,10 L10,20 h-10 Z" stroke="black" stroke-width="1" fill="green"/>

        <g id="consumer_r" stroke="black" stroke-width="1">
          <path d="M 0,0 h16 v16 h-16 Z" fill="green" />
          <path d="M 16,8 h8" />
          <path d="M 31,0 a 8,8 0 0,0 0,16" fill="none"/>
        </g>
        <g id="provider_r" stroke="black" stroke-width="1" fill="green">
          <path d="M 0,0 h16 v16 h-16 Z" />
          <path d="M 16,8 h8" />
          <circle cx="30" cy="8" r="6" />
        </g>
        <g id="consumer_l" stroke="black" stroke-width="1">
          <path d="M 0,0 h16 v16 h-16 Z" fill="green" />
          <path d="M 0,8 h -8" />
          <path d="M -16,0 a 8,8 0 0,1 0,16" fill="none" />
        </g>
        <g id="provider_l" stroke="black" stroke-width="1" fill="green">
          <path d="M 0,0 h16 v16 h-16 Z" />
          <path d="M 0,8 h-8" />
          <circle cx="-14" cy="8" r="6"/>
        </g>
    </defs>
    <rect x="$pos" y="10" width="$width" height="$height" fill="blue" stroke="black" />
    <text x="$text_pos_x" y="$text_pos_y" text-anchor="middle">$rtc_name</text>
    '''
    res=res.replace('$align', align)
    res=res.replace('$style2', style2)
    res=res.replace('$style', style)
    res=res.replace('$view_w', str(view_w))
    res=res.replace('$view_h', str(view_h))
    res=res.replace('$pos', str(pos))
    res=res.replace('$width', str(width))
    res=res.replace('$height', str(height))
    res=res.replace('$text_pos_x', str(text_pos_x))
    res=res.replace('$text_pos_y', str(text_pos_y))
    res=res.replace('$rtc_name', rtc_name)
    # Left side
    i=0
    for port in port_l:
      posx = pos - 15
      posy = 25 + port_h * i

      portname = port['name']
      if port['flow'] == 'DataInPort':
        portflow="in"
      elif port['flow'] == 'DataOutPort':
        portflow="out"
      else:
        portflow = port['flow']

      posy1 = posy+5
      posy2 = posy+20

      if portflow == 'in':
        posx1 = posx-10
        porttype = port['type']

      elif portflow == 'consumer' or portflow == 'provider':
        posx1 = posx-25
        porttype = port['if_type_name']
        if not porttype :
          porttype = port['interface']

      res +='''
    <use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#${portflow}_l"  x="$posx" y="$posy" />
    <text x="$posx1" y="$posy1" text-anchor="end">$portname</text>
    <text x="$posx1" y="$posy2" text-anchor="end">($porttype)</text>
      '''
      res=res.replace("${portflow}", portflow)
      res=res.replace("$posx1", str(posx1))
      res=res.replace("$posy1", str(posy1))
      res=res.replace("$posy2", str(posy2))
      res=res.replace("$posx", str(posx))
      res=res.replace("$posy", str(posy))
      res=res.replace("$portname", portname)
      res=res.replace("$porttype", porttype)

      i += 1

    # Right side
    i=0
    for port in port_r :
      posx = pos + width -5
      posy = 25 + port_h * i

      portname = port['name']
      if port['flow'] == 'DataInPort':
        portflow="in"
      elif port['flow'] == 'DataOutPort':
        portflow="out"
      else:
        portflow = port['flow']

      posy1 = posy+5
      posy2 = posy+20

      if portflow == 'out':
        posx1 = posx+30
        porttype = port['type']

      elif portflow == 'consumer' or portflow == 'provider':
        porttype = port['if_type_name']
        if not porttype:
          porttype = port['interface']

        posx1 = posx+40

      res +='''
    <use xmlns:xlink="http://www.w3.org/1999/xlink" xlink:href="#${portflow}_r"
      x="$posx" y="$posy" />
    <text x="$posx1" y="$posy1" text-anchor="start">$portname</text>
    <text x="$posx1" y="$posy2" text-anchor="start">($porttype)</text>
      '''

      res=res.replace("${portflow}", portflow)
      res=res.replace("$posx1", str(posx1))
      res=res.replace("$posy1", str(posy1))
      res=res.replace("$posy2", str(posy2))
      res=res.replace("$posx", str(posx))
      res=res.replace("$posy", str(posy))
      res=res.replace("$portname", portname)
      res=res.replace("$porttype", porttype)

      i += 1

    res += "</svg>\n</div>"

  return res


def rtc_profile(profile):
  res=""

  res += "<table>"
  keys=['instance_name', 'description', 'version', 'vendor', 'category', 'activity_type', 'max_instance', 
    'language', 'lang_type', 'exec_cxt.periodic.type','exec_cxt.periodic.rate',
    'openrtm.name', 'openrtm.version', 'os.name', 'corba.id']
  for k in keys:
    if k in profile:
      res += "<tr><th>%s</th><td>%s</td></tr>" % (k, str(profile[k]).encode('raw-unicode-escape').decode('utf-8', 'ignore'))

  res += "</table>"
  return res
#
#
#
def rtc_dataport_table(profile, klass="docutils", colw="18:15:15:52"):
  res=""

  try:
    dataport = profile['dataport']

    if not dataport:
      res =""
      return res

    res ='''
      <table width="100%" class="$class">
        <colgroup>
    '''
    res = res.replace("$class", klass)

    cols = colw.split(":")
    for val in cols :
      res += "<col width=\""+val+"%\">\n"

    res +='''
        </colgroup>
        <thead><th>Name</th><th>Flow</th><th>Data Type</th><th>Description</th></thead>
        <tbody>
    '''

    for port in dataport :
      name=""
      flow=""
      typ=""
      description=""
      if 'name' in port: name = port['name']
      if name:
        if 'type' in port: typ = port['type']
        if 'description' in port: description = port['description'].encode('raw-unicode-escape').decode('utf-8', 'ignore')
        if 'flow' in port and (port['flow'] == 'in' or port['flow'] =='DataInPort'):
          flow = "InPort"
        elif 'flow' in port and (port['flow'] == 'out' or port['flow'] == 'DataOutPort') :
          flow = "OutPort"
        else:
          flow = ""
      res +="<tr><td>$name </td><td>$flow</td><td>$type</td><td>$description</td></tr>\n"
      res=res.replace("$name", name)
      res=res.replace("$flow", flow)
      res=res.replace("$type", typ)
      res=res.replace("$description", description)

    res +="\n</tbody>\n</table>"

  except:
    pass

  return res


def rtc_serviceport_table(profile, klass="docutils", colw="18:15:15:52"):
  res=""

  try:
    serviceport = profile['serviceport']

    if not serviceport:
      res =""
      return res

    res='''
      <table width="100%" class="$class">
        <colgroup>
    '''
    res = res.replace("$class", klass)
    cols = colw.split(":")
    for val in cols :
      res += "<col width=\"" +val +"%\">\n"

    res +='''
        </colgroup>
        <thead><th>Name</th><th>Service Type</th><th>Interface</th><th>Description</th></thead>
        <tbody>
    '''

    for port in serviceport :
      name=""
      flow=""
      typ=""
      description=""
      if 'name' in port : name = port['name']
      if name:
        if 'if_type_name' in port: typ = port['if_type_name']
        if not typ:
          if 'interface' in port : typ = port['interface']

        if 'description' in port: description = port['description']

        if 'flow' in port and port['flow'] == 'provider':
          flow = "Provider";
        elif 'flow' in port and port['flow'] == 'consumer':
          flow = "Consumer"
        else:
          pass
        res +="<tr><td>%s</td><td>%s</td><td>%s</td><td>%s</td></tr>\n" % (name, flow, typ, description)
    res +="</tbody>\n  </table>"
  except:
    pass
  return res

#
#
#
def rtc_configuration_table(profile, klass="docutils", colw="15:10:15:15:45"):
  res=""

  try:
    configuration = profile['configuration']
    if not configuration:
      res =""
      return res

    res='''
      <table width="100%" class="$class">
        <colgroup>
    '''
    res=res.replace("$class", klass)

    cols = colw.split(":")
    for val in cols :
      res += "<col width=\""+val+"%\">\n"

    res +='''
        </colgroup>
        <thead><th>Name</th><th>Data Type</th><th>Deafult Value</th><th>Constraints</th><th>Description</th></thead>
        <tbody>
    '''

    for port in configuration:
      name=""
      constraints=""
      typ="string"
      description=""
      defaultVal=""
      if 'name' in port: name = port['name']
      if name:
        if 'default' in port:  defaultVal = port['default']
        if '__type__' in port and  port['__type__']:  typ = html.escape(port['__type__'])
        if '__constraints__' in port and port['__constraints__']:  constraints = port['__constraints__']
        if '__description__' in port: description = port['__description__'].encode('raw-unicode-escape').decode('utf-8', 'ignore')

        res +='''
      <tr><td>$name </td><td>$type</td><td>$defaultVal</td>
       <td>$constraints</td><td>$description</td></tr>
        '''

        res=res.replace("$name", name)
        res=res.replace("$type", typ)
        res=res.replace("$defaultVal", str(defaultVal))
        res=res.replace("$constraints", constraints)
        res=res.replace("$description", description)

    res +="</tbody>\n  </table>"
  except:
    traceback.print_exc()
    pass
  return res

if __name__=='__main__':
  rtc_doc(sys.argv[1])