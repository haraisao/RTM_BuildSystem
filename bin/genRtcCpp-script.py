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
#
#
def is_defined(attr, data):
    return ((attr in data) and data[attr])

def genFile(yaml_data, tmpl_dir, tmpl_name, out_dir, out_name, enc=""):
    data=loadTemplate(tmpl_name, tmpl_dir)
    data=replaceAllKeys(data, yaml_data, "in "+tmpl_name)
    if rename_old_file(os.path.join(out_dir, tmpl_dir), out_name , data):
        if enc:
            writeFile(data, out_name, os.path.join(out_dir, tmpl_dir), enc )
        else:
            writeFile(data, out_name, os.path.join(out_dir, tmpl_dir) )
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

    genFile(yaml_data, "src", "ProjectName.cpp", dist, outfname+".cpp", 'utf_8_sig')
    genFile(yaml_data, "src", "ProjectNameComp.cpp", dist, outfname+"Comp.cpp", 'utf_8_sig')

    #data=loadTemplate("ProjectName.cpp", "src")
    #data=replaceAllKeys(data, yaml_data, "in ProjectName.cpp")
    #if rename_old_file(os.path.join(dist, "src"), outfname+".cpp" , data): 
    #    writeFile(data, outfname+".cpp", os.path.join(dist, "src"), 'utf_8_sig' )

    #data2=loadTemplate("ProjectNameComp.cpp", "src")
    #data2=replaceAllKeys(data2, yaml_data, "in ProjectNameComp.cpp")
    #if rename_old_file(os.path.join(dist, "src"), outfname+"Comp.cpp" , data2): 
    #    writeFile(data2, outfname+"Comp.cpp", os.path.join(dist, "src"), 'utf_8_sig')

    #genCMakeLists(yaml_data, "src", dist)

#
#  XXX.h
def genHeaderFile(yaml_data, dist=""):
    outfname=yaml_data['ProjectName']
    genFile(yaml_data, "include", "ProjectName.h", dist, outfname+".h", 'utf_8_sig')
#    data=loadTemplate("ProjectName.h", "include")
#    data=replaceAllKeys(data, yaml_data, "in ProjectName.h")
#    outfname=yaml_data['ProjectName']
#    if rename_old_file(os.path.join(dist, "include"), outfname+".h" , data): 
#        writeFile(data, outfname+".h", os.path.join(dist, "include"), 'utf_8_sig')

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
# XXX_impl.cpp, h
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
                service_data['interface_type'] = interface_name
                #service_data['service_name'] = module_name
                service_data['module_name'] = module_name
                service_data['service_impl'] = sdata['impl']
                service_data['service_name'] = "%s_%s" % (module_name, interface_name)
                service_data['SERVICE_IMPL'] = sdata['impl'].upper()

                operations=parse_operations(sdata)

                impls=""
                ope_decl = ""
                for f in operations:
                    impls += generate_cpp_function(f)
                    ope_decl += generate_h_decls(f)

                service_data['operations_impl'] = impls
                service_data['operations'] = ope_decl

                genFile(service_data, "include", "ServiceName_impl.h", dist, outfname+".h", 'utf_8_sig' )
                genFile(service_data, "src", "ServiceName_impl.cpp", dist, outfname+".cpp", 'utf_8_sig' )


#
#
def parse_operations(data):
    if not is_defined('operations', data): return None

    operations = []

    for op in data['operations']:
        retval, funcname = op.split(" ",1)
        ope={}
        ope['retval'] = retval
        ope['module_name'] = data['module_name']
        ope['impl'] = data['impl']  
        #
        # val[1] :func, val[2]: args
        val=re.match(r"([\w]+)\(([:,\s\w]*)\)", funcname)
        ope['funcname'] = val[1]
        args = val[2]

        argv=[]
        #
        if args:
            args_ar = args.split(',')

            for x in args_ar:
                v = x.split(" ")
                arg=[]
                for val in v:
                    if val : arg.append(val)
                if len(arg) > 2:
                    argv.append(arg)
                else:
                    print("-- Error: invalid expression")

        ope['args'] = argv
        operations.append(ope)
    return operations    

def generate_h_decls(data):
    tmpl='''
   %s %s(%s)
      throw (CORBA::SystemException);
    '''
    res = tmpl % (argtype(data['retval'], data['module_name'] ,"return"), 
                    data['funcname'],  ', '.join(arg2ar(data['args'],  data['module_name'], "in")))
    return res

def generate_cpp_function(data):
    templ='''
/*
    %s %s::%s(%s)
*/
%s %s::%s(%s){
    #warn("Please imprement function.");
}
    '''
    res = templ % ( argtype(data['retval'],  data['module_name'], "return"), data['impl'],
                    data['funcname'],
                    ', '.join(arg2ar(data['args'],  data['module_name'], "in")),
                    argtype(data['retval'],  data['module_name'],"return"),  data['impl'],
                    data['funcname'], 
                    ', '.join(arg2ar(data['args'],  data['module_name'], "in")
             )
    )
    #print(res)
    return res
#
#
def arg2ar(data, mod_name, flag):
  res=[]
  for args in data:
    if args[0] == "in" or args[0] == "out" :
        if args[1] == "unsigned":
            res.append( "%s %s" % (argtype("unsigned "+args[2], mod_name, flag), args[3]) )
        else:
            res.append( "%s %s" % (argtype(args[1], mod_name, flag), args[2]) )
    else:
        print("Invalid format...")
  return res

return_type = {
    'octet' : '::CORBA::Octet',
    'short' : '::CORBA::Short', 
    'unsigned short' : '::CORBA::UShort',
    'long' : '::CORBA::Long',
    'unsigned long' : '::CORBA::ULong',
    'float' : '::CORBA::Float',
    'double' : '::CORBA::Double',
    'boolean' : '::CORBA::Boolean',
    'string' : 'char*',
    'wstring' : 'wchar*',
    'void' : 'void'  
    }

in_type ={
    'octet' : '::CORBA::Octet' ,
    'short' : '::CORBA::Short' , 
    'unsigned short' : '::CORBA::UShort',
    'long' : '::CORBA::Long',
    'unsigned long' : '::CORBA::ULong',
    'float' : '::CORBA::Float',
    'double' : '::CORBA::Double',
    'boolean' : '::CORBA::Boolean',
    'string' : 'const char*',
    'wstring' : 'const wchar*' 
    }

out_type ={
    'octet' : '::CORBA::Octet&' ,
    'short' : '::CORBA::Short&' , 
    'unsigned short' : '::CORBA::UShort&',
    'long' : '::CORBA::Long&',
    'unsigned long' : '::CORBA::ULong&',
    'float' : '::CORBA::Float&',
    'double' : '::CORBA::Double&',
    'boolean' : '::CORBA::Boolean&',
    'string' : '::CORBA::String_out',
    'wstring' : '::CORBA::WString_out'
    }

def argtype(name, mod_name, flag="in"):
  if flag == "in":
    if name in in_type:
        return in_type[name]
    else:
        if name.count("::"):
            return "const %s" % name
        else:
            return "const %s::%s" % (mod_name, name)

  elif flag == "out":
    if name in out_type:
        return out_type[name]
    else:   
        if name.count("::"):
            return "%s_out" % name
        else:
            return "%s::%s_out" % (mod_name, name)
  else:
    if name in return_type:
        return return_type[name]
    else:
        if name.count("::"):
            return "%s*" % name
        else:
            return "%s::%s*" % (mod_name, name)


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


