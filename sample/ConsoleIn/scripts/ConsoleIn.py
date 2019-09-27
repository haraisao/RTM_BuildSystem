#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @license the MIT License

 Copyright(C) 2018 Isao Hara,AIST,JP
 All rights reserved.

"""
from DataFlowRTC_Base import *

def DataIn(name, data):
  print("----", data)
  return

setFunction(DataIn)

##
# @class ProjectName
# 
# 
class ConsoleIn(DataFlowRTC_Base):
  ##
  # @brief constructor
  # @param manager Maneger Object
  # 
  def __init__(self, manager):
    DataFlowRTC_Base.__init__(self, manager)

  ##
  #
  # The initialize action (on CREATED->ALIVE transition)
  # formaer rtc_init_entry() 
  # 
  # @return RTC::ReturnCode_t
  # 
  #
  def onInitialize(self):
    DataFlowRTC_Base.onInitialize(self)
    
    return RTC.RTC_OK


  #####
  #   onFinalize
  #
  def onFinalize(self):

    return RTC.RTC_OK

  #####
  #   onStartup
  #
  #def onStartup(self, ec_id):
  #
  #  return RTC.RTC_OK

  #####
  #   onShutdown
  #
  #def onShutdown(self, ec_id):
  #
  #  return RTC.RTC_OK

  #####
  #   onActivated
  #
  def onActivated(self, ec_id):

    return RTC.RTC_OK

  #####
  #   onDeactivated
  #
  def onDeactivated(self, ec_id):

    return RTC.RTC_OK

  #####
  #   onAborting
  #
  #def onAborting(self, ec_id):
  #
  #  return RTC.RTC_OK

  #####
  #   onError
  #
  #def onError(self, ec_id):
  #
  #  return RTC.RTC_OK

  #####
  #   onReset
  #
  #def onReset(self, ec_id):
  #
  #  return RTC.RTC_OK

  #####
  #   onExecute
  #
  def onExecute(self, ec_id):
    try:
      if self._inIn.isNew():
        data = self._inIn.read()
        print("Received: ", data)
        print("Received: ", data.data)
        print("TimeStamp: ", data.tm.sec, "[s] ", data.tm.nsec, "[ns]")
    except:
      traceback.print_exc()

    try:
      data = input_with_timeout("Please input: ", 10)
      self._d_out.data = int(data)
      OpenRTM_aist.setTimestamp(self._d_out)
      print("Sending to subscriber: ", self._d_out.data)
      self._outOut.write()
    except TimeoutExpired:
      pass
    except InputTerminated:
      self.deactivate(ec_id)
      print("...Deactivate")
    except:
      traceback.print_exc()

    return RTC.RTC_OK

  #####
  #   onStateUpdate
  #
  #def onStateUpdate(self, ec_id):
  #
  #  return RTC.RTC_OK

  #####
  #   onRateChanged
  #
  #def onRateChanged(self, ec_id):
  #
  #  return RTC.RTC_OK

  #####
  #   onAction
  #
  #def onAction(self, ec_id):
  #
  #  return RTC.RTC_OK

  #####
  #   onModeChanged
  #
  #def onModeChanged(self, ec_id):
  #
  #  return RTC.RTC_OK


  ##
  # Callback method from RtcDataListenr
  # 
  def onData(self, name, data):
    print("\n====>", name,data)

    return RTC.RTC_OK


#########################################
#  Initializers
#

def main():
  mgr = rtc_init(ConsoleIn,  os.path.join(os.path.dirname(__file__), 'ConsoleIn.yaml'))
  mgr.runManager()

if __name__ == "__main__":
  main()

