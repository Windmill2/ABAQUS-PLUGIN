# -*- coding: utf-8 -*-
from abaqusGui import *
from abaqusConstants import ALL
import os


class WeldStepBuilder_plugin(AFXForm):

    def __init__(self, owner):
        AFXForm.__init__(self, owner)
        self.radioButtonGroups = {}

        self.cmd = AFXGuiCommand(mode=self, method='kernel',
            objectName='WeldStepBuilder', registerQuery=False)

        self.currentModelNameKw = AFXStringKeyword(self.cmd, 'currentModelName', True, 'Model-1')
        self.structureModelNameKw = AFXStringKeyword(self.cmd, 'structureModelName', True, 'Model-1-s')

        if not self.radioButtonGroups.has_key('jobType'):
            self.jobTypeKw1 = AFXIntKeyword(None, 'jobTypeDummy', True)
            self.jobTypeKw2 = AFXStringKeyword(self.cmd, 'jobType', True, 'both')
            self.radioButtonGroups['jobType'] = (self.jobTypeKw1, self.jobTypeKw2, {})
        self.radioButtonGroups['jobType'][2][601] = 'both'
        self.jobTypeKw1.setValue(601)
        self.radioButtonGroups['jobType'][2][602] = 'heat'
        self.radioButtonGroups['jobType'][2][603] = 'structure'

        if not self.radioButtonGroups.has_key('activeModule'):
            self.activeModuleKw1 = AFXIntKeyword(None, 'activeModuleDummy', True)
            self.activeModuleKw2 = AFXStringKeyword(self.cmd, 'activeModule', True, 'steps')
            self.radioButtonGroups['activeModule'] = (self.activeModuleKw1, self.activeModuleKw2, {})
        self.radioButtonGroups['activeModule'][2][701] = 'steps'
        self.activeModuleKw1.setValue(701)
        self.radioButtonGroups['activeModule'][2][702] = 'copy'
        self.radioButtonGroups['activeModule'][2][703] = 'birthdeath'
        self.radioButtonGroups['activeModule'][2][704] = 'heatload'
        self.radioButtonGroups['activeModule'][2][705] = 'temppredef'

        if not self.radioButtonGroups.has_key('stepType'):
            self.stepTypeKw1 = AFXIntKeyword(None, 'stepTypeDummy', True)
            self.stepTypeKw2 = AFXStringKeyword(self.cmd, 'stepType', True, 'HeatTransfer')
            self.radioButtonGroups['stepType'] = (self.stepTypeKw1, self.stepTypeKw2, {})
        self.radioButtonGroups['stepType'][2][801] = 'HeatTransfer'
        self.stepTypeKw1.setValue(801)
        self.radioButtonGroups['stepType'][2][802] = 'Visco'
        self.radioButtonGroups['stepType'][2][803] = 'StaticGeneral'
        self.radioButtonGroups['stepType'][2][804] = 'CoupledTempDisp'

        if not self.radioButtonGroups.has_key('convertStepType'):
            self.convertStepTypeKw1 = AFXIntKeyword(None, 'convertStepTypeDummy', True)
            self.convertStepTypeKw2 = AFXStringKeyword(self.cmd, 'convertStepType', True, 'Visco')
            self.radioButtonGroups['convertStepType'] = (self.convertStepTypeKw1, self.convertStepTypeKw2, {})
        self.radioButtonGroups['convertStepType'][2][811] = 'Visco'
        self.convertStepTypeKw1.setValue(811)
        self.radioButtonGroups['convertStepType'][2][812] = 'StaticGeneral'
        self.radioButtonGroups['convertStepType'][2][813] = 'CoupledTempDisp'

        self.numSegmentsKw = AFXIntKeyword(self.cmd, 'numSegments', True, 40)
        self.firstIndexKw = AFXIntKeyword(self.cmd, 'firstIndex', True, 1)
        self.stepPrefixKw = AFXStringKeyword(self.cmd, 'stepPrefix', True, 'Step-')
        self.previousStepNameKw = AFXStringKeyword(self.cmd, 'previousStepName', True, 'Step-1')
        self.shortTimePeriodKw = AFXFloatKeyword(self.cmd, 'shortTimePeriod', True, 0.001)
        self.longTimePeriodKw = AFXFloatKeyword(self.cmd, 'longTimePeriod', True, 800.0)
        self.shortInitialIncKw = AFXFloatKeyword(self.cmd, 'shortInitialInc', True, 0.001)
        self.longInitialIncKw = AFXFloatKeyword(self.cmd, 'longInitialInc', True, 0.001)
        self.viscoLongInitialIncKw = AFXFloatKeyword(self.cmd, 'viscoLongInitialInc', True, 0.0001)
        self.maxNumIncKw = AFXIntKeyword(self.cmd, 'maxNumInc', True, 100000)
        self.shortMinIncKw = AFXFloatKeyword(self.cmd, 'shortMinInc', True, 1e-08)
        self.shortMaxIncKw = AFXFloatKeyword(self.cmd, 'shortMaxInc', True, 0.001)
        self.longMinIncKw = AFXFloatKeyword(self.cmd, 'longMinInc', True, 1e-06)
        self.longMaxIncKw = AFXFloatKeyword(self.cmd, 'longMaxInc', True, 50.0)
        self.maxTempChangeKw = AFXFloatKeyword(self.cmd, 'maxTempChange', True, 100.0)
        self.viscoCETolKw = AFXFloatKeyword(self.cmd, 'viscoCETol', True, 0.0001)

        self.partInstanceNameKw = AFXStringKeyword(self.cmd, 'partInstanceName', True, 'Part-1-1')
        self.setPrefixKw = AFXStringKeyword(self.cmd, 'setPrefix', True, 'W-')
        self.interactionPrefixKw = AFXStringKeyword(self.cmd, 'interactionPrefix', True, 'Int-')
        self.killAllInteractionKw = AFXStringKeyword(self.cmd, 'killAllInteraction', True, '')
        self.loadPrefixKw = AFXStringKeyword(self.cmd, 'loadPrefix', True, 'Load-')
        self.loadStartStepNameKw = AFXStringKeyword(self.cmd, 'loadStartStepName', True, '')
        self.tempPredefPrefixKw = AFXStringKeyword(self.cmd, 'tempPredefPrefix', True, 'Predefined Field-')

        self.heatFluxKw = AFXFloatKeyword(self.cmd, 'heatFlux', True, 34000.0)
        self.amplitudeNameKw = AFXStringKeyword(self.cmd, 'amplitudeName', True, 'Amp-1')
        self.tempSetNameKw = AFXStringKeyword(self.cmd, 'tempSetName', True, 'ALL')
        self.tempOdbFileKw = AFXStringKeyword(self.cmd, 'tempOdbFile', True, 'e:/weld-heat/w-1/t-1.odb')
        self.tempFieldStartKw = AFXIntKeyword(self.cmd, 'tempFieldStart', True, 1)
        self.tempFieldEndKw = AFXIntKeyword(self.cmd, 'tempFieldEnd', True, 0)

        self.targetModelNameKw = AFXStringKeyword(self.cmd, 'targetModelName', True, 'Model-1-s')
        self.activeInStepKw = AFXBoolKeyword(self.cmd, 'activeInStep',
            AFXBoolKeyword.TRUE_FALSE, True, True)
        self.includeStrainKw = AFXBoolKeyword(self.cmd, 'includeStrain',
            AFXBoolKeyword.TRUE_FALSE, True, False)

    def getFirstDialog(self):
        import WeldStepBuilderDB
        return WeldStepBuilderDB.WeldStepBuilderDB(self)

    def doCustomChecks(self):
        for kw1, kw2, d in self.radioButtonGroups.values():
            try:
                value = d[kw1.getValue()]
                kw2.setValue(value)
            except:
                pass
        return True

    def okToCancel(self):
        return False


thisPath = os.path.abspath(__file__)
thisDir = os.path.dirname(thisPath)

toolset = getAFXApp().getAFXMainWindow().getPluginToolset()
toolset.registerGuiMenuButton(
    buttonText='Weld Step Builder...',
    object=WeldStepBuilder_plugin(toolset),
    messageId=AFXMode.ID_ACTIVATE,
    icon=None,
    kernelInitString='import WeldStepBuilder',
    applicableModules=ALL,
    version='1.1',
    author='Codex',
    description='Create repeated analysis steps, model change interactions, '
                'heat loads, and model copy/convert in Abaqus/CAE.',
    helpUrl='N/A'
)
