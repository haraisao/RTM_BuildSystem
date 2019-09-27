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
#  CMakeLists.txt
def genCMakeLists(yaml_data, dirname="", dist=""):
    data=loadTemplate("CMakeLists.txt", dirname)
    data=replaceAllKeys(data, yaml_data, "in CMakeLists.txt("+dirname+")")
    writeFile(data, "CMakeLists.txt", os.path.join(dist, dirname))

#
# XXX.cpp and XXXComp.cpp
def genCppFile(yaml_data, dist=""):
    outfname=yaml_data['ProjectName']

    data=loadTemplate("ProjectName.cpp", "src")
    data=replaceAllKeys(data, yaml_data, "in ProjectName.cpp")
    writeFile(data, outfname+".cpp", os.path.join(dist, "src"), 'utf_8_sig' )

    data2=loadTemplate("ProjectNameComp.cpp", "src")
    data2=replaceAllKeys(data2, yaml_data, "in ProjectNameComp.cpp")
    writeFile(data2, outfname+"Comp.cpp", os.path.join(dist, "src"), 'utf_8_sig')

    #genCMakeLists(yaml_data, "src", dist)

#
#  XXX.h
def genHeaderFile(yaml_data, dist=""):
    data=loadTemplate("ProjectName.h", "include")
    data=replaceAllKeys(data, yaml_data, "in ProjectName.h")
    outfname=yaml_data['ProjectName']
    writeFile(data, outfname+".h", os.path.join(dist, "include"), 'utf_8_sig')

    #genCMakeLists(yaml_data, "include", dist)

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
    if 'configuration' in data and data['configuration']:
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
    if 'configuration' in data and data['configuration']:
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
    if 'configuration' in data and data['configuration']:
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
    if 'dataport' in data and data['dataport']:
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
    if 'dataport' in data and data['dataport']:
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
    if 'dataport' in data and data['dataport']:
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
    if 'dataport' in data:
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
    if 'actions' in data:
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
    if 'actions' in data:
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


