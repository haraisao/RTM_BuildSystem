#!/usr/bin/env python
# -*- coding: utf-8 -*-
# -*- Python -*-

"""
 @license the MIT License

 Copyright(C) 2018 Isao Hara,AIST,JP
 All rights reserved.

"""
from DataFlowRTC_Base import *

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

  #####
  #   onData
  #
  def onData(self, name, data):
    print(name, data)

    return RTC.RTC_OK




#########################################
#  Initializers
#

def main():
  mgr = rtc_init(ConsoleIn,  os.path.join(os.path.dirname(__file__), 'ConsoleIn.yaml'))
  mgr.runManager()

if __name__ == "__main__":
  main()

