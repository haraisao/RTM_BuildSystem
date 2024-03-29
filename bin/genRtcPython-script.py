#
#
import sys
import os
import os.path
import yaml
import re
import shutil
import traceback
import time
import difflib
import pprint

template_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template')

#
#  Load Yaml 
def read_rtc_yaml(fname="RTC"):
    (pname, ext)=os.path.splitext(os.path.basename(fname))
    if not ext :
        fname=fname+".yaml"

    try:
        f=open(fname, "r", encoding="utf-8")
        try:
            data=yaml.load(f, Loader=yaml.FullLoader)
        except:
            data=yaml.load(f)
        f.close()
        data['ProjectName'] = data['name']
        return data
    except:
        traceback.print_exc()
        return None

#
# Load Template file
def loadTemplate(fname, dirname=""):
    tmpl_fname=os.path.join(template_dir, "python", dirname, fname+".in")
    f=open(tmpl_fname, "r", encoding="utf-8")
    data=f.read()
    f.close()
    return data

#
# Output 
def writeFile(data, fname, dirname="", enc='utf-8'):
    if dirname and not os.path.exists(dirname):
        os.makedirs(dirname)
    out_fname=os.path.join(dirname, fname)
    try:
        fw=open(out_fname, "w", encoding=enc)
        fw.write(data)
        fw.close()
    except:
        print("Fail to output to ", fname)
    return

#
#
def file_diff(file1, text2):
    try:
        with open(file1) as f1:
            text1=f1.read()
        return  difflib.context_diff(text1.splitlines(keepends=True), text2.splitlines(keepends=True),
                        fromfile=os.path.basename(file1), tofile="new_"+os.path.basename(file1))
    except:
        return None
#
#
def rename_old_file(dirname, fname, data):
    full_fname=os.path.join(dirname, fname)
    diff = file_diff(full_fname, data)

    if diff :
        diff_txt = ''.join(diff)
        if diff_txt:
            tm=time.localtime()
            #backup_fname="%s.%d%03d%02d%02d" % (fname, tm.tm_year-2000, tm.tm_yday, tm.tm_hour, tm.tm_min)
            #print("==== copy %s to %s" % (full_fname,  backup_fname))
            #shutil.copy(full_fname, os.path.join(dirname, backup_fname))
            diff_fname="%s.%d%03d%02d%02d.diff" % (fname, tm.tm_year-2000, tm.tm_yday, tm.tm_hour, tm.tm_min)
            try:
                with open(os.path.join(dirname, diff_fname), "w", encoding='utf-8') as fw:
                    fw.write(diff_txt)
                print("==== save the diff to %s" % (diff_fname))
            except:
                print("==== Fail to save the diff to %s" % (os.path.join(dirname, diff_fname)))

            return True
        else:
            #print("==== %s is same, skip to generate" % fname)
            return False
    return True

def is_defined(attr, data):
    return ((attr in data) and data[attr])

#
#
def genFile(yaml_data, tmpl_dir, tmpl_name, out_dir, out_name, enc="", comment_sym="\#"):
    data=loadTemplate(tmpl_name, tmpl_dir)
    data=replaceAllKeys(data, yaml_data, "in "+tmpl_name)
    org_content = getFileContent(os.path.join(out_dir, tmpl_dir, out_name))
    org_code=getOwnCodeArea(org_content, comment_sym)
    for key in org_code:
        area=getCodeArea(data, key, 0, comment_sym )
        if area:
            data=data[:area[0]] + org_code[key][1] + data[area[1]:]

    if rename_old_file(os.path.join(out_dir, tmpl_dir), out_name , data):
        if enc:
            writeFile(data, out_name, os.path.join(out_dir, tmpl_dir), enc )
        else:
            writeFile(data, out_name, os.path.join(out_dir, tmpl_dir) )

#
#  CMakeLists.txt
def genCMakeLists(yaml_data, dirname="", dist=""):
    yaml_data['service_impl_h'] = ""
    yaml_data['service_impl_cpp'] = ""
    yaml_data['service_idl'] = ""
    if is_defined('serviceport', yaml_data):
        for sdata in yaml_data['serviceport']:
            if 'impl' in sdata:
                yaml_data['service_impl_h'] += "  include/"+sdata['impl']+".h\n"
                yaml_data['service_impl_cpp'] += "  src/"+sdata['impl']+".cpp\n"
            yaml_data['service_idl']="idl/%s_%s.idl\n" % (sdata['module_name'],  sdata['name'])

    genFile(yaml_data, dirname, "CMakeLists.txt", dist, "CMakeLists.txt", comment_sym="\#")

#
# XXX.py 
def genPythonFile(yaml_data, dist=""):
    outfname=yaml_data['ProjectName']+".py"
    genFile(yaml_data, "scripts", "ProjectName.py", dist, outfname, enc="", comment_sym="\#")

#
# XXX.idl 
def genIDLFile(yaml_data, dist=""):
    if is_defined('serviceport', yaml_data):
        service_data={}
        for sdata in yaml_data['serviceport']:
            if 'module_name' in sdata :
                module_name=sdata['module_name']
                interface_name = sdata['name']
                outfname="%s_%s.idl" % (module_name, interface_name)
                service_data.clear()
                service_data['interface_name'] = interface_name
                service_data['module_name'] = module_name
                service_data['SERVICE_NAME'] = "%s_%s" % (module_name.upper(), interface_name.upper())

                if 'decls' in sdata:
                    decls=""
                    for x in sdata['decls']:
                        decls += "  %s;\n" % x
                    service_data['decls'] = decls
                else:
                    service_data['decls'] = ""

                if 'operations' in sdata:
                    funcs = ""
                    for x in sdata['operations']:
                        funcs += "    "+x+";\n"
                    service_data['service_function_idl'] = funcs
                else:
                    service_data['service_function_idl'] = ""
                
                service_data['description'] = sdata['description']

                genFile(service_data, "idl", "Service_module.idl", dist, outfname, enc="", comment_sym="\/\/")
                #data=loadTemplate("Service_module.idl", "idl")
                #data=replaceAllKeys(data, service_data, "in Service_module.idl")
                #
                #if rename_old_file(os.path.join(dist, "idl"), outfname , data):
                #    writeFile(data, outfname, os.path.join(dist, "idl") )

#
# XXX_impl.py 
def genServiceImplFile(yaml_data, dist=""):
    if is_defined('serviceport', yaml_data):
        service_data={}
        for sdata in yaml_data['serviceport']:
            if sdata['flow'] == 'provider':
                if 'module_name' in sdata:
                    module_name=sdata['module_name']
                interface_name = sdata['name']
                outfname=sdata['impl']+".py"
                service_data.clear()
                service_data['interface_name'] = interface_name
                service_data['service_name'] = module_name
                service_data['service_impl'] = sdata['impl']

                if is_defined('operations', sdata):
                    funcs = ""
                    for op in sdata['operations']:
                        resval=""
                        funcname = op.split(" ",1)
                        if funcname[0] != "void":
                            resval = "res"
                        val=re.match(r"([\w]+)\(([:,\s\w]*)\)", funcname[1])
                        args = val[2]
                        if args:
                            args_ar = args.split(',')
                            argv=[]
                            for x in args_ar:
                                v=x.split(" ")
                                if v[0] == "in":
                                    argv.append(v[-1])
                                elif v[0] == "out":
                                    if resval:
                                        resval += ","+v[-1]
                                    else:
                                        resval += v[-1]
                            if argv :
                                args = ", ".join(argv)
                                funcs += "  #\n  # %s\n" % op
                                funcs += "  def "+val[1]+"(self, "+args+"):\n"
                            else:
                                funcs += "  #\n  # %s\n" % op
                                funcs += "  def "+val[1]+"(self):\n"
                        else:
                            funcs += "  #\n  # %s\n" % op
                            funcs += "  def "+val[1]+"(self):\n"
                        funcs += "    try:\n"
                        funcs += "#---< %s\n#--->\n" % val[1]
                        funcs += "      return "+resval+"\n"
                        funcs += "    except AttributeError:\n      raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)\n\n"
                    service_data['service_function'] = funcs
                else:
                    service_data['service_function'] = ""

                genFile(service_data, "scripts", "Service_module.py", dist, outfname, enc="", comment_sym="\#")
                #data=loadTemplate("Service_module.py", "scripts")
                #data=replaceAllKeys(data, service_data, "in Service_module.py")
                #if rename_old_file(os.path.join(dist, "scripts"), outfname , data):
                #    writeFile(data, outfname, os.path.join(dist, "scripts") )

#
#  Replace Keys (@xxx@)
def replaceAllKeys(data, yaml_data, info=""):
    for x in getReplaceStrs(data):
        try:
            if x == 'action_define':
                data=data.replace('@'+x+'@', getActionsDefine(yaml_data))
            elif x == 'rtc_data':
                data=data.replace('@'+x+'@', pprint.pformat(yaml_data))
            else:
                data=data.replace('@'+x+'@', str(yaml_data[x]))
        except:
            print("Warning: Fail to replace", '@'+x+'@', info)
            pass
    return data

#
#  Get list of keys in a template file
def getReplaceStrs(data):
    plist = re.findall(r'@(\w+)@', data)
    return list(set(plist))

#
# define actions
def getActionsDefine(data):
    val = "\n"
    project_name=data['ProjectName']

    if is_defined('actions', data):
        for x in data['actions']:
            for xx in x.keys():
                if xx=='OnInitialize':
                    pass
                elif x[xx] :
                    if xx == 'OnFinalize':
                        val += "  #####\n  #   on%s\n  #\n" % (xx[2:])
                        val += "  def on%s(self):\n#---< %s\n#--->\n    return RTC.RTC_OK\n\n" % (xx[2:], xx)
                    else:
                        val += "  #####\n  #   on%s\n  #\n" % (xx[2:])
                        val += "  def on%s(self, ec_id):\n#---< %s\n#--->\n    return RTC.RTC_OK\n\n" % (xx[2:], xx)
                else:
                    pass
                    #if xx == 'OnFinalize':
                    #    val += "  #####\n  #   on%s\n" % (xx[2:])
                    #    val += "  #\n  #def on%s(self):\n  #\n  #  return RTC.RTC_OK\n\n" % (xx[2:])
                    #else:
                    #    val += "  #####\n  #   on%s\n" % (xx[2:])
                    #    val += "  #\n  #def on%s(self, ec_id):\n  #\n  #  return RTC.RTC_OK\n\n" % (xx[2:])

    if is_defined('dataport', data) :
        for port in data['dataport']:
            if 'datalistener' in port:
                val += "  #####\n  #   onData\n  #\n"
                val += "  def onData(self, name, data):\n    print(name, data)\n#---< OnData\n#--->\n\n"
                val += "    return RTC.RTC_OK\n\n"
                break
    return val

def getFileContent(fname):
    res=""
    try:
        with open(fname, "r", encoding="utf-8") as f:
            res=f.read()
    except:
        pass
    return res

start_pattern=r"%s\-{3,}\<"
end_pattern=r"%s\-{3,}\>"

def getOwnCodeArea(content, comment_sym="\#"):
    start = 0
    mobj=1
    res={}
    start_mark=(start_pattern % comment_sym) +" [\w]+"
    end_mark=(end_pattern % comment_sym)
    while mobj:
        mobj = re.search(start_mark, content[start:])
        if mobj:
            mobj_e = re.search(end_mark, content[start+mobj.end():])
            if mobj_e:
                spos=start+mobj.end()
                epos=start+mobj.end()+mobj_e.start()
                res[mobj[0][6:].strip()] = [[spos, epos], content[spos:epos]]
                
                start += mobj.end() + mobj_e.end()
            else:
                spos=start+mobj.end()
                epos=-1
                res[mobj[0][6:].strip()] = [[spos, -1], content[spos:]]
                mobj = False
    return res

def getCodeArea(content, key, start=0, comment_sym="\#"):
    start_mark=(start_pattern % comment_sym) + (" %s" % key)
    end_mark=(end_pattern % comment_sym)
    mobj = re.search(start_mark, content[start:])
    if mobj:
        mobj_e = re.search(end_mark, content[start+mobj.end():])
        spos=start+mobj.end()
        if mobj_e:
            epos=start+mobj.end()+mobj_e.start()
            return [spos, epos]        
        else:
            None
    return None

#
# generate Python files
def genPythonFiles(data, yaml_file, dist=""):
    #genCMakeLists(data, "", dist)
    genPythonFile(data, dist)
    genIDLFile(data, dist)
    genServiceImplFile(data, dist)

    target_idl_dir = os.path.join(dist, 'idl')
    target_scripts_dir = os.path.join(dist, 'scripts')
    project_name=data['ProjectName']
    try:
        os.mkdir(target_idl_dir)
    except:
        pass
    templ_scripts_dir = os.path.join(template_dir, "Python", "scripts")
    shutil.copy(os.path.join(templ_scripts_dir, "DataFlowRTC_Base.py"), target_scripts_dir)
    #shutil.copy(yaml_file, os.path.join(target_scripts_dir, project_name+".yaml"))
    shutil.copy(os.path.join(template_dir, "Python", "idlcompile.bat"), dist)
    shutil.copy(os.path.join(template_dir, "Python", "rtc.conf"), dist)
    shutil.copy(os.path.join(template_dir,"Python", "ProjectName.exe"), os.path.join(dist, project_name+".exe"))
#
#  M A I N
if __name__ == '__main__':
    dist_dir = ""
    if len(sys.argv) > 2:
        dist_dir = sys.argv[2]

    if len(sys.argv) < 2:
        print("Usage:", sys.argv[0], "YamlFile", "[Dist Dir]")
        sys.exit()

    if dist_dir == ".":
        disr_dir=""
    elif  dist_dir == "":
        dist_dir=os.path.splitext(os.path.basename(sys.argv[1]))[0]

    data=read_rtc_yaml(sys.argv[1])
    if data:
        genPythonFiles(data, sys.argv[1], dist_dir)
