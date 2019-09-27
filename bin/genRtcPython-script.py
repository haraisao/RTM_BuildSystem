#
#
import sys
import os
import os.path
import yaml
import re
import shutil
import traceback

template_dir=os.path.join(os.path.dirname(os.path.abspath(__file__)), 'template')

#
#  Load Yaml 
def read_rtc_yaml(fname="RTC"):
    (pname, ext)=os.path.splitext(os.path.basename(fname))
    if not ext :
        fname=fname+".yaml"

    try:
        f=open(fname, "r", encoding="utf-8")
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
#  CMakeLists.txt
def genCMakeLists(yaml_data, dirname="", dist=""):
    data=loadTemplate("CMakeLists.txt", dirname)
    data=replaceAllKeys(data, yaml_data, "in CMakeLists.txt("+dirname+")")
    writeFile(data, "CMakeLists.txt", os.path.join(dist, dirname))

#
# XXX.py 
def genPythonFile(yaml_data, dist=""):
    outfname=yaml_data['ProjectName']

    data=loadTemplate("ProjectName.py", "scripts")
    data=replaceAllKeys(data, yaml_data, "in ProjectName.py")
    writeFile(data, outfname+".py", os.path.join(dist, "scripts"), 'utf_8_sig' )

    #genCMakeLists(yaml_data, "src", dist)

#
#  Replace Keys (@xxx@)
def replaceAllKeys(data, yaml_data, info=""):
    for x in getReplaceStrs(data):
        try:
            if x == 'action_define':
                data=data.replace('@'+x+'@', getActionsDefine(yaml_data))
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
    if 'actions' in data:
        for x in data['actions']:
            for xx in x.keys():
                if xx=='OnInitialize':
                    pass
                elif x[xx] :
                    if xx == 'OnFinalize':
                        val += "  #####\n  #   on%s\n  #\n" % (xx[2:])
                        val += "  def on%s(self):\n\n    return RTC.RTC_OK\n\n" % (xx[2:])
                    else:
                        val += "  #####\n  #   on%s\n  #\n" % (xx[2:])
                        val += "  def on%s(self, ec_id):\n\n    return RTC.RTC_OK\n\n" % (xx[2:])
                else:
                    if xx == 'OnFinalize':
                        val += "  #####\n  #   on%s\n" % (xx[2:])
                        val += "  #\n  #def on%s(self):\n  #\n  #  return RTC.RTC_OK\n\n" % (xx[2:])
                    else:
                        val += "  #####\n  #   on%s\n" % (xx[2:])
                        val += "  #\n  #def on%s(self, ec_id):\n  #\n  #  return RTC.RTC_OK\n\n" % (xx[2:])
    return val

#
# generate C++ files
def genPythonFiles(data, yaml_file, dist=""):
    genCMakeLists(data, "", dist)
    genPythonFile(data, dist)

    target_idl_dir = os.path.join(dist, 'idl')
    target_scripts_dir = os.path.join(dist, 'scripts')
    project_name=data['ProjectName']
    try:
        os.mkdir(target_idl_dir)
    except:
        pass
    templ_scripts_dir = os.path.join(template_dir, "Python", "scripts")
    #shutil.copy(os.path.join(templ_scripts_dir, "DataFlowRTC_Base.py"), target_scripts_dir)
    shutil.copy(yaml_file, os.path.join(target_scripts_dir, project_name+".yaml"))
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


