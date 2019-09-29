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
        data['ProjectName'] = pname
        return data
    except:
        traceback.print_exc()
        return None

#
# Load Template file
def loadTemplate(fname, dirname=""):
    tmpl_fname=os.path.join(template_dir, "c++", dirname, fname+".in")
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
#  CMakeLists.txt
def genCMakeLists(yaml_data, dirname="", dist=""):
    data=loadTemplate("CMakeLists.txt", dirname)
    data=replaceAllKeys(data, yaml_data, "in CMakeLists.txt("+dirname+")")
    if rename_old_file(os.path.join(dist, dirname), "CMakeLists.txt" , data):
        writeFile(data, "CMakeLists.txt", os.path.join(dist, dirname))

#
# XXX.cpp and XXXComp.cpp
def genCppFile(yaml_data, dist=""):
    outfname=yaml_data['ProjectName']

    data=loadTemplate("ProjectName.cpp", "src")
    data=replaceAllKeys(data, yaml_data, "in ProjectName.cpp")
    if rename_old_file(os.path.join(dist, "src"), outfname+".cpp" , data): 
        writeFile(data, outfname+".cpp", os.path.join(dist, "src"), 'utf_8_sig' )

    data2=loadTemplate("ProjectNameComp.cpp", "src")
    data2=replaceAllKeys(data2, yaml_data, "in ProjectNameComp.cpp")
    if rename_old_file(os.path.join(dist, "src"), outfname+"Comp.cpp" , data2): 
        writeFile(data2, outfname+"Comp.cpp", os.path.join(dist, "src"), 'utf_8_sig')

    #genCMakeLists(yaml_data, "src", dist)

#
#  XXX.h
def genHeaderFile(yaml_data, dist=""):
    data=loadTemplate("ProjectName.h", "include")
    data=replaceAllKeys(data, yaml_data, "in ProjectName.h")
    outfname=yaml_data['ProjectName']
    if rename_old_file(os.path.join(dist, "include"), outfname+".h" , data): 
        writeFile(data, outfname+".h", os.path.join(dist, "include"), 'utf_8_sig')

    #genCMakeLists(yaml_data, "include", dist)

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
                if is_defined('decls', sdata):
                    decls=""
                    for x in sdata['decls']:
                        decls += "  %s;\n" % x
                    service_data['decls'] = decls
                else:
                    service_data['decls'] = ""

                if is_defined('operations', sdata):
                    funcs = ""
                    for x in sdata['operations']:
                        funcs += "    "+x+";\n"
                    service_data['service_function_idl'] = funcs
                else:
                    service_data['service_function_idl'] = ""
                
                service_data['description'] = sdata['description']

                data=loadTemplate("Service_module.idl", "idl")
                data=replaceAllKeys(data, service_data, "in Service_module.idl")

                if rename_old_file(os.path.join(dist, "idl"), outfname , data):
                    writeFile(data, outfname, os.path.join(dist, "idl") )



#
# XXX_impl.py 
def genServiceImplFile(yaml_data, dist=""):
    if is_defined('serviceport', yaml_data):
        service_data={}
        for sdata in yaml_data['serviceport']:
            if sdata['flow'] == 'provider':
                if 'module_name' in sdata: module_name=sdata['module_name']
                interface_name = sdata['name']
                outfname=sdata['impl']

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
                        funcs += "      return "+resval+"\n"
                        funcs += "    except AttributeError:\n      raise CORBA.NO_IMPLEMENT(0, CORBA.COMPLETED_NO)\n\n"
                    service_data['service_function'] = funcs
                else:
                    service_data['service_function'] = ""

                #
                #
                data_h=loadTemplate("ServiceName_impl.h", "include")
                data_h=replaceAllKeys(data_h, service_data, "in ServiceName_impl.h")
                if rename_old_file(os.path.join(dist, "include"), outfname+".h" , data_h):
                    writeFile(data_h, outfname+".h", os.path.join(dist, "include") )
                #
                data_cpp=loadTemplate("ServiceName_impl.cpp", "src")
                data_cpp=replaceAllKeys(data_cpp, service_data, "in ServiceName_impl.cpp")
                if rename_old_file(os.path.join(dist, "src"), outfname+".cpp" , data_cpp):
                    writeFile(data_cpp, outfname+".cpp", os.path.join(dist, "src") )
                #


#
#  Replace Keys (@xxx@)
def replaceAllKeys(data, yaml_data, info=""):
    for x in getReplaceStrs(data):
        try:
            if x == 'configuration':
                data=data.replace('@'+x+'@', getConfigrations_spec(yaml_data))
            elif x == 'bind_configuration':
                data=data.replace('@'+x+'@', getBindConfigrations(yaml_data))
            elif x == 'configuration_decl':
                data=data.replace('@'+x+'@', getConfigrationsDecl(yaml_data))
            elif x == 'dataport_decl':
                data=data.replace('@'+x+'@', getDataPortDecl(yaml_data))
            elif x == 'dataport_construct_decl':
                data=data.replace('@'+x+'@', getDataPortConstuctDecl(yaml_data))
            elif x == 'add_dataports':
                data=data.replace('@'+x+'@', getAddDataPort(yaml_data))
            elif x == 'data_listener':
                data=data.replace('@'+x+'@', getDataListener(yaml_data))
            elif x == 'action_decls':
                data=data.replace('@'+x+'@', getActionsDecl(yaml_data))
            elif x == 'action_define':
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
#  Configration spec
def getConfigrations_spec(data):
    val="\n"
    if is_defined('configuration', data):
        for x in data['configuration']:
            try:
                val += "    \"conf.default.%s\", \"%s\",\n" % (x['name'], str(x['default']))
                if '__constraints__' in x and x['__constraints__']:
                    val += "    \"conf.__constraints__.%s\", \"%s\",\n" % (x['name'], x['__constraints__'])
                if '__widgwt__' in x and x['__widget__'] :
                    val += "    \"conf.__widget__.%s\", \"%s\",\n" % (x['name'], x['__widget__'])
                if '__type__' in x  and x['__type__'] :
                    val += "    \"conf.__type__.%s\", \"%s\",\n" % (x['name'], x['__type__'])
                if '__description__' in x  and x['__description__'] :
                    val += "    \"conf.__description__.%s\", \"%s\",\n" % (x['name'], x['__description__'])
            except:
                print("Error...")
                pass
    return val

#
#  bindparametr
def getBindConfigrations(data):
    val="\n"
    if is_defined('configuration', data):
        for x in data['configuration']:
            try:
                val += "  bindParameter(\"%s\", m_%s, \"%s\");\n" % (x['name'], x['name'], str(x['default']))
            except:
                pass
    return val

#
#  declare configuration parameter in a header file
def getConfigrationsDecl(data):
    val="\n"
    if ('configuration' in data) and data['configuration']:
        for x in data['configuration']:
            try:
                dtype=x['__type__']
                if dtype == 'string': dtype="std::string"
                val += "  %s m_%s;\n" % (dtype, x['name'])
            except:
                pass
    return val

#
# declare dataport in a header file
def getDataPortDecl(data):
    res=""
    if is_defined('dataport', data):
        for x in data['dataport']:
            res += "  %s m_%s;\n" % (x['type'], x['name'])
            if x['flow'] == 'in':
                res += "  InPort<%s> m_%sIn;\n\n" % (x['type'], x['name'])
            else:
                res += "  OutPort<%s> m_%sOut;\n\n" % (x['type'], x['name'])
    return res

#
# dataport initalization in a constructor
def getDataPortConstuctDecl(data):
    res=""
    if is_defined('dataport', data):
        for x in data['dataport']:
            if x['flow'] == 'in':
                res += ",\n    m_%sIn(\"%s\", m_%s)" % ( x['name'], x['name'], x['name'])
            else:
                res += ",\n    m_%sOut(\"%s\", m_%s)" % ( x['name'], x['name'], x['name'])
    return res
#
# add port 
def getAddDataPort(data):
    res=""
    if is_defined('dataport', data) :
        for x in data['dataport']:
            if x['flow'] == 'in':
                res += "\n  addInPort(\"%s\", m_%sIn);" % ( x['name'], x['name'])
                if 'datalistener' in x:
                    res += "\n  m_%sIn.addConnectorDataListener(ON_BUFFER_WRITE, " % (x['name'])
                    res += "\n      new %sDataListener(\"ON_BUFFER_WRITE\", this), false); \n" % (x['datalistener'])
            else:
                res += "\n  addOutPort(\"%s\", m_%sOut);" % ( x['name'], x['name'])
    return res

#
#  declare DataListener in a header file
def getDataListener(data):
    defined_listener=[]
    tmplDataListener='''
/*!
 * @class DataListener
 * @brief
 */
class %sDataListener
  : public ConnectorDataListenerT<%s>
{
  USE_CONNLISTENER_STATUS;
public:
  /*!
   * @brief constructor
   */
  %sDataListener(const char* name, %s *data) : m_name(name), m_obj(data){};

  /*!
   * @brief destructor
   */
  virtual ~%sDataListener(){};

  virtual ReturnCode operator()( ConnectorInfo& info,
                                 %s& data){
    if ( m_name == "ON_BUFFER_WRITE" ) {
     /* onBufferWrite */
    }
    return NO_CHANGE;
  };

  %s *m_obj;
  std::string m_name;
};

'''
    res = ""

    if is_defined('dataport', data):
        for x in data['dataport']:
            if x['flow'] == 'in':
                if ('datalistener' in x) and (not x['datalistener'] in defined_listener):
                    res += tmplDataListener % (x['datalistener'], x['type'], x['datalistener'],
                                     data['ProjectName'], x['datalistener'], x['type'], data['ProjectName'])
                    defined_listener.append( x['datalistener'])
    return res

#
# declare actions
def getActionsDecl(data):
    val = "\n"
    if is_defined('actions', data):
        for x in data['actions']:
            for xx in x.keys():
                if x[xx] :
                    if xx == 'OnInitialize' or xx == 'OnFinalize':
                        val += "   virtual RTC::ReturnCode_t on%s();\n\n" % xx[2:]
                    else:
                        val += "   virtual RTC::ReturnCode_t on%s(RTC::UniqueId ec_id);\n\n" % xx[2:]
                else:
                    if xx == 'OnInitialize' or xx == 'OnFinalize':
                        val += "   /* virtual RTC::ReturnCode_t on%s(); */\n\n" % xx[2:]
                    else:
                        val += "   /* virtual RTC::ReturnCode_t on%s(RTC::UniqueId ec_id); */\n\n" % xx[2:]
    return val

#
# define actions
def getActionsDefine(data):
    val = "\n"
    project_name=data['ProjectName']
    if is_defined('actions', data) :
        for x in data['actions']:
            for xx in x.keys():
                if xx=='OnInitialize':
                    pass
                elif x[xx] :
                    if xx == 'OnFinalize':
                        val += "RTC::ReturnCode_t %s::on%s()\n{\n\n  return RTC::RTC_OK;\n}\n\n" % (project_name, xx[2:])
                    else:
                        val += "RTC::ReturnCode_t %s::on%s(RTC::UniqueId ec_id)\n{\n\n  return RTC::RTC_OK;\n}\n\n" % (project_name, xx[2:])
                else:
                    if xx == 'OnFinalize':
                        val += "/*\nRTC::ReturnCode_t %s::on%s()\n{\n\n  return RTC::RTC_OK;\n}\n*/\n\n" % (project_name, xx[2:])
                    else:
                        val += "/*\nRTC::ReturnCode_t %s::on%s(RTC::UniqueId ec_id)\n{\n\n  return RTC::RTC_OK;\n}\n*/\n\n" % (project_name, xx[2:])
    return val

#
# generate C++ files
def genCppFiles(data, dist=""):
    genCMakeLists(data, "", dist)
    genCppFile(data, dist)
    genHeaderFile(data, dist)
    genIDLFile(data, dist)
    genServiceImplFile(data, dist)
    
    target_idl_dir = os.path.join(dist, 'idl')
    try:
        os.mkdir(target_idl_dir)
    except:
        pass
    #templ_idl_dir = os.path.join(template_dir, "C++", "idl")
    #shutil.copy(os.path.join(templ_idl_dir, "BasicDataType.idl"), target_idl_dir)
    #shutil.copy(os.path.join(templ_idl_dir, "ExtendedDataTypes.idl"), target_idl_dir)
    #shutil.copy(os.path.join(templ_idl_dir, "InterfaceDataTypes.idl"), target_idl_dir)

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
        genCppFiles(data, dist_dir)


