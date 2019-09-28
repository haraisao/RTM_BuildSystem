#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

#  Copyright(C) 2018 Isao Hara,AIST,JP
#  All rights reserved
#  License: the MIT License
import os
import sys
import time
sys.path.append(os.path.dirname('__file__'))
sys.path.append(os.path.join(os.path.dirname('__file__'),"rtm"))

import yaml
from collections import OrderedDict

# Import RTM module
import omniORB
import RTC
import OpenRTM_aist


#
# Global Variables
_rtc_spec_dict_=None
_rtc_spec_=None
_rtc_class_=None
_rtc_name_=None
_rtc_dataports_=None
_rtc_serviceports_=None
_rtc_params_=None

#
#  Function
import msvcrt
import time

class TimeoutExpired(Exception):
    pass

class InputTerminated(Exception):
    pass

def input_with_timeout(prompt, timeout, timer=time.monotonic):
    sys.stdout.write(prompt)
    sys.stdout.flush()
    endtime = timer() + timeout
    result = []
    while timer() < endtime:
        if msvcrt.kbhit():
            result.append(msvcrt.getwche()) #XXX can it block on multibyte characters?
            if result[-1] == '\r':   #XXX check what Windows returns here
                return ''.join(result[:-1])
            elif  result[-1] == '\x04':   # Ctrl-D
                raise InputTerminated
        time.sleep(0.04) # just to yield to other processes/threads
    raise TimeoutExpired


def getGlobals():
    return globals()

def setGlobals(name, val):
    globals()[name] = val

def setFunction(fnc):
    globals()[fnc.__name__] = fnc
#########################################################################
#
# DataListener 
#   This class connected with DataInPort
#
class RtcDataListener(OpenRTM_aist.ConnectorDataListenerT):
    def __init__(self, name, typ, obj, func=None):
        self._name = name
        self._type = typ
        self._obj = obj
        self._func = func
    
    def __call__(self, info, cdrdata):
        data = OpenRTM_aist.ConnectorDataListenerT.__call__(self,
                        info, cdrdata, self._type)

        if self._func :
          self._func(self._name, data)

        else:
          self._obj.onData(self._name, data)

    def _set_callback(self, func):
        self._func = func

##
# @class DataFlowRTC_Base
# @brief Base class for DataFlowComponent
# 
# 
class DataFlowRTC_Base(OpenRTM_aist.DataFlowComponentBase):
  
  ##
  # @brief constructor
  # @param manager Maneger Object
  # 
  def __init__(self, manager, rtc_dataports=None, rtc_services=None, rtc_params=None):
    OpenRTM_aist.DataFlowComponentBase.__init__(self, manager)

    if rtc_dataports is None:
      self._dataports=_rtc_dataports_
    else:
      self._dataports=rtc_dataports

    if rtc_services is None:
      self._services=_rtc_serviceports_
    else:
      self._services=rtc_services

    if rtc_params is None:
      self._params=_rtc_params_
    else:
      self._params=rtc_params

    self.globals=None

    #
    # set dataport
    for k in self._dataports.keys():
      _d, _p = init_dataport(k, self._dataports)

      if self._dataports[k]['flow'] == 'in':
        self.__dict__['_d_'+k] = _d
        self.__dict__['_'+k+'In'] = _p
        if 'datalistener' in self._dataports[k]:
          try:
            self.bindDataListener(k, eval(self._dataports[k]['datalistener'], globals()))
          except:
            print("No such function(%s), set default datalistener"  % (self._dataports[k]['datalistener']))
            self.bindDataListener(k)

      elif self._dataports[k]['flow'] == 'out':
        self.__dict__['_d_'+k] = _d
        self.__dict__['_'+k+'Out'] = _p
      else:
        pass

    # set service port
    for k in self._services.keys():
      if self._services[k]['flow'] == 'provider':
        self.__dict__['_'+k+'Port'] = OpenRTM_aist.CorbaPort(k)
        self.__dict__['_'+k+'_service'] = eval(self._services[k]['impl'],globals())()

      elif self._services[k]['flow'] == 'consumer':
        self.__dict__['_'+k+'Port'] = OpenRTM_aist.CorbaPort(k)
        if 'if_type' in self._services[k]:
          if_type = self._services[k]['if_type']
        else:
          if_type="%s.%s" % (self._services[k]['module_name'], k)
        if not self._services[k]['module_name'] in globals():
          import_str="import %s" % self._services[k]['module_name']
          exec(import_str,globals())
        #self.__dict__['_'+k+'_service'] = OpenRTM_aist.CorbaConsumer(interfaceType=self._services[k]['if_type'])
        self.__dict__['_'+k+'_service'] = OpenRTM_aist.CorbaConsumer(interfaceType=eval(if_type, globals()))


    # initialize of configuration-data.
    for x in init_params(self._params):
      self.__dict__['_'+x[0]] = [x[1]]

  ##
  #
  # The initialize action (on CREATED->ALIVE transition)
  # formaer rtc_init_entry() 
  # 
  # @return RTC::ReturnCode_t
  # 
  #
  def onInitialize(self):
    # Bind variables and configuration variable
    for k in self._params.keys():
      self.bindParameter(k, self.__dict__['_'+k], str(self._params[k]['default']))
                  
    # Set DataPort buffers
    for k in self._dataports.keys():
      if self._dataports[k]['flow'] == 'in':
        self.addOutPort(k, self.__dict__['_'+k+'In'])
      elif self._dataports[k]['flow'] == 'out':
        self.addOutPort(k, self.__dict__['_'+k+'Out'])
      else:
        pass

    # Set service ports
    service_keys = list(self._services.keys())
    if service_keys: service_keys.sort()

    for k in service_keys:
      s_port=self.__dict__['_'+k+'Port']
      service=self.__dict__['_'+k+'_service']
      
      if 'if_name' in self._services[k]:
        if_name = self._services[k]['if_name']
      else:
        if_name = "%s_%s" % (self._services[k]['module_name'], k)

      if 'if_type_name' in self._services[k]:
        if_type_name = self._services[k]['if_type_name']
      else:
        if_type_name = "%s::%s" % (self._services[k]['module_name'], k)

      if self._services[k]['flow'] == 'provider':
        #s_port.registerProvider(self._services[k]['if_name'], self._services[k]['if_type_name'], service)
        s_port.registerProvider(if_name, if_type_name, service)
        self.addPort(s_port)

      elif self._services[k]['flow'] == 'consumer':
        #s_port.registerConsumer(self._services[k]['if_name'], self._services[k]['if_type_name'], service)
        s_port.registerConsumer(if_name, if_type_name, service)
        self.addPort(s_port)
      else:
        pass

    return RTC.RTC_OK
  
  #
  #
  def onData(self, name, data):

    return RTC.RTC_OK

  #
  #
  def bindDataListener(self, portname, func=None):
    try:
      port = eval('self._'+portname+'In')
      if isinstance(port, OpenRTM_aist.InPort) :
        port.addConnectorDataListener(
          OpenRTM_aist.ConnectorDataListenerType.ON_BUFFER_WRITE,
          RtcDataListener(port._name, port._value, self, func))
        return True
      else:
        print("Invalid PortType")
        return False
    except:
      traceback.print_exc()
      return False

#########################################
#
#  Funcrions
#
def init_params(param):
  res=[]
  for k1 in param.keys():
    if param[k1]['__type__'] == 'string':
      val=param[k1]['default']
    else:
      #val=eval(param[k1]['default'])
      val=param[k1]['default']
    res.append([k1, val])
  return res

#
#
def init_dataport(name, dataport):
  dname=dataport[name]['type'].replace("::", ".")
  typ=dataport[name]['flow']
  m, d=dname.split('.')
  d_type = eval(m+"._d_"+d)
  v_arg = [None] * int((len(d_type) - 4) / 2)
  _d = instantiateDataType(eval(dname))
  if typ == 'in':
    _p = OpenRTM_aist.InPort(name, _d)
  elif typ == 'out':
    _p = OpenRTM_aist.OutPort(name, _d)
  else:
    _p = None

  return _d,_p

#
#  DataType for CORBA
#
def instantiateDataType(dtype):
    if isinstance(dtype, int) : desc = [dtype]
    elif isinstance(dtype, tuple) : desc = dtype
    else :
        desc=omniORB.findType(dtype._NP_RepositoryId)

    if desc[0] in [omniORB.tcInternal.tv_alias ]: return instantiateDataType(desc[2])

    if desc[0] in [omniORB.tcInternal.tv_short,
                   omniORB.tcInternal.tv_long,
                   omniORB.tcInternal.tv_ushort,
                   omniORB.tcInternal.tv_ulong,
                   omniORB.tcInternal.tv_boolean,
                   omniORB.tcInternal.tv_char,
                   omniORB.tcInternal.tv_octet,
                   omniORB.tcInternal.tv_longlong,
                   omniORB.tcInternal.tv_enum
                  ]: return 0

    if desc[0] in [omniORB.tcInternal.tv_float,
                   omniORB.tcInternal.tv_double,
                   omniORB.tcInternal.tv_longdouble
                  ]: return 0.0

    if desc[0] in [omniORB.tcInternal.tv_sequence,
                   omniORB.tcInternal.tv_array,
                  ]: return []


    if desc[0] in [omniORB.tcInternal.tv_string ]: return ""
    if desc[0] in [omniORB.tcInternal.tv_wstring,
                   omniORB.tcInternal.tv_wchar
                  ]: return u""
    if desc[0] == omniORB.tcInternal.tv_struct:
        arg = []
        for i in  range(4, len(desc), 2):
            attr = desc[i]
            attr_type = desc[i+1]
            arg.append(instantiateDataType(attr_type))
        return desc[1](*arg)
    return None

#
#
def new_Time():
  tm=OpenRTM_aist.Time() 
  return RTC.Time(tm.sec,tm.usec)

#
#
#
yaml.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, lambda loader, node: OrderedDict(loader.construct_pairs(node)))

def load_rtc_data(fname='rtc.yaml'):
  #fname=os.path.join(os.path.dirname(__file__), fname)
  with open(fname, encoding="utf-8") as file:
    data = yaml.load(file)

  return data

#########################################
#
#
def mk_rtc_spec(spec_dict):
  keys=["implementation_id", "type_name", "description", "version", "vendor", "category", "activity_type", "component_type", "kind", "max_instance" ]
  
  if not "implementation_id" in spec_dict: spec_dict["implementation_id"] = spec_dict["name"]
  if not "type_name" in spec_dict: spec_dict["type_name"] = spec_dict["name"]

  res=[]
  for x in keys:
    res.append(x)
    res.append(str(spec_dict[x]))
  
  res.append("language")
  res.append("Python")
  res.append("lang_type")
  res.append("SCRIPT")
  
  param=spec_dict['configuration']
  param_keys=['default', '__type__', '__widget__', '__constraints__', '__description__']
  if param :
    for p in param:
      name=p['name']
      for x in param_keys:
        if p.has_key(x):  
          res.append('conf.'+x+'.'+name)
          res.append(str(p[x]))
  return res

#
#
#
def mk_rtc_dict(spec_dict, key):
  res=OrderedDict()
  try:
    lst=spec_dict[key]
    for x in lst:
      d=dict()
      for k in x.keys():
        if k != 'name':
          d[k] = x[k]
      res[x['name']]=d
    return  res
  except:
    return {}

#
#
#
def RtcModuleInit(manager):
  global _rtc_spec_, _rtc_class_, _rtc_name_

  profile = OpenRTM_aist.Properties(defaults_str=_rtc_spec_)
  manager.registerFactory(profile, _rtc_class_, OpenRTM_aist.Delete)
  comp = manager.createComponent(_rtc_name_)

#
#
#
def rtc_init(klass, rtc_yaml='rtc.yaml'):
  global _rtc_spec_dict_, _rtc_spec_, _rtc_class_, _rtc_name_, _rtc_dataports_, _rtc_serviceports_, _rtc_params_

  _rtc_spec_dict_=load_rtc_data(fname=rtc_yaml)
  _rtc_spec_=mk_rtc_spec(_rtc_spec_dict_)
  _rtc_class_=klass
  _rtc_name_=_rtc_spec_dict_['implementation_id']
  _rtc_dataports_=mk_rtc_dict(_rtc_spec_dict_,'dataport')
  _rtc_serviceports_=mk_rtc_dict(_rtc_spec_dict_,'serviceport')
  _rtc_params_=mk_rtc_dict(_rtc_spec_dict_,'configuration')

  #if 'service_modules' in _rtc_spec_dict_:
  #  for m in _rtc_spec_dict_['service_modules']:
  #    m=m.strip()
  #    if m :
  #      import_str="from "+m+" import *"
  #      exec(import_str,globals())

  if 'serviceport' in _rtc_spec_dict_:
    for sp in _rtc_spec_dict_['serviceport']:
      if 'impl' in sp:
        m = sp['impl'].strip()
        if m :
          import_str="from %s import *" % m
          exec(import_str,globals())
  
  mgr = OpenRTM_aist.Manager.init(sys.argv)
  mgr.setModuleInitProc(RtcModuleInit)
  mgr.activateManager()

  return mgr
