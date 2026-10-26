# -*- coding: utf-8 -*-
from abaqusGui import *
from abaqusConstants import *
from kernelAccess import mdb, session


class WeldStepBuilderDB(AFXDataDialog):

    [ID_READ_MODEL, ID_RUN_STEPS, ID_RUN_COPY, ID_RUN_BIRTH, ID_RUN_HEAT,
     ID_RUN_TEMP, ID_PREV_STEP, ID_KILL_ALL, ID_READ_INTERACTIONS,
     ID_LOAD_STEP] = range(AFXDataDialog.ID_LAST, AFXDataDialog.ID_LAST + 10)

    def __init__(self, form):
        self.form = form

        AFXDataDialog.__init__(self, form, 'Weld Step Builder',
            self.CANCEL, DIALOG_ACTIONS_SEPARATOR|DECOR_RESIZE)

        FXMAPFUNC(self, SEL_COMMAND, self.ID_READ_MODEL, WeldStepBuilderDB.onReadModel)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_RUN_STEPS, WeldStepBuilderDB.onRunSteps)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_RUN_COPY, WeldStepBuilderDB.onRunCopy)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_RUN_BIRTH, WeldStepBuilderDB.onRunBirth)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_RUN_HEAT, WeldStepBuilderDB.onRunHeat)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_RUN_TEMP, WeldStepBuilderDB.onRunTemp)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_PREV_STEP, WeldStepBuilderDB.onSelPreviousStep)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_KILL_ALL, WeldStepBuilderDB.onSelKillAll)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_READ_INTERACTIONS, WeldStepBuilderDB.onReadInteractions)
        FXMAPFUNC(self, SEL_COMMAND, self.ID_LOAD_STEP, WeldStepBuilderDB.onSelLoadStep)

        top = FXHorizontalFrame(self, opts=LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)

        gbCurrent = FXGroupBox(p=top, text='Current Model', opts=FRAME_GROOVE)
        haCurrent = FXHorizontalFrame(p=gbCurrent, opts=LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        AFXTextField(p=haCurrent, ncols=20, labelText='Model Name:',
            tgt=form.currentModelNameKw, sel=0)
        FXButton(p=haCurrent, text='Read Current Model', tgt=self,
            sel=self.ID_READ_MODEL, opts=BUTTON_NORMAL|LAYOUT_CENTER_Y,
            x=0, y=0, w=0, h=0, pl=2, pr=2, pt=1, pb=1)

        hfModule = FXHorizontalFrame(self, opts=LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)
        FXLabel(p=hfModule, text='Modules:', opts=JUSTIFY_LEFT|LAYOUT_CENTER_Y)
        FXRadioButton(p=hfModule, text='Analysis Steps', tgt=form.activeModuleKw1, sel=701)
        FXRadioButton(p=hfModule, text='Model Copy / Convert', tgt=form.activeModuleKw1, sel=702)
        FXRadioButton(p=hfModule, text='Birth / Death', tgt=form.activeModuleKw1, sel=703)
        FXRadioButton(p=hfModule, text='Heat Input', tgt=form.activeModuleKw1, sel=704)
        FXRadioButton(p=hfModule, text='Temp Field Import', tgt=form.activeModuleKw1, sel=705)

        # ---- Analysis Steps module ------------------------------------
        self.stepsFrame = FXVerticalFrame(self,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)

        gbStepType = FXGroupBox(p=self.stepsFrame, text='Analysis Step Type', opts=FRAME_GROOVE)
        FXRadioButton(p=gbStepType, text='Heat Transfer', tgt=form.stepTypeKw1, sel=801)
        FXRadioButton(p=gbStepType, text='Visco', tgt=form.stepTypeKw1, sel=802)
        FXRadioButton(p=gbStepType, text='Static General', tgt=form.stepTypeKw1, sel=803)
        FXRadioButton(p=gbStepType, text='Coupled Temp-Displacement', tgt=form.stepTypeKw1, sel=804)

        gbNames = FXGroupBox(p=self.stepsFrame, text='Model and Step Names', opts=FRAME_GROOVE)
        va1 = AFXVerticalAligner(p=gbNames, opts=0,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=va1, ncols=16, labelText='Number of passes:', tgt=form.numSegmentsKw, sel=0)
        self.previousStepCombo = AFXComboBox(va1, 16, 5, 'Previous step name:', self,
            self.ID_PREV_STEP, LAYOUT_FILL_X)
        AFXTextField(p=va1, ncols=16, labelText='Model:', tgt=form.currentModelNameKw, sel=0)

        gbInc = FXGroupBox(p=self.stepsFrame, text='Time and Increment Controls', opts=FRAME_GROOVE)
        va2 = AFXVerticalAligner(p=gbInc, opts=0,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=va2, ncols=16, labelText='Short step period:', tgt=form.shortTimePeriodKw, sel=0)
        AFXTextField(p=va2, ncols=16, labelText='Long step period:', tgt=form.longTimePeriodKw, sel=0)
        AFXTextField(p=va2, ncols=16, labelText='Max increments:', tgt=form.maxNumIncKw, sel=0)
        AFXTextField(p=va2, ncols=16, labelText='Short initial inc:', tgt=form.shortInitialIncKw, sel=0)
        AFXTextField(p=va2, ncols=16, labelText='Short min inc:', tgt=form.shortMinIncKw, sel=0)
        AFXTextField(p=va2, ncols=16, labelText='Short max inc:', tgt=form.shortMaxIncKw, sel=0)
        AFXTextField(p=va2, ncols=16, labelText='Long initial inc:', tgt=form.longInitialIncKw, sel=0)
        AFXTextField(p=va2, ncols=16, labelText='Visco long initial inc:', tgt=form.viscoLongInitialIncKw, sel=0)
        AFXTextField(p=va2, ncols=16, labelText='Long min inc:', tgt=form.longMinIncKw, sel=0)
        AFXTextField(p=va2, ncols=16, labelText='Long max inc:', tgt=form.longMaxIncKw, sel=0)
        AFXTextField(p=va2, ncols=16, labelText='Heat deltmx:', tgt=form.maxTempChangeKw, sel=0)
        AFXTextField(p=va2, ncols=16, labelText='Visco cetol:', tgt=form.viscoCETolKw, sel=0)

        runStepsHf = FXHorizontalFrame(p=self.stepsFrame, opts=LAYOUT_CENTER_X,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=DEFAULT_SPACING, pb=0)
        FXButton(p=runStepsHf, text='Execute Analysis Steps', tgt=self,
            sel=self.ID_RUN_STEPS, opts=BUTTON_NORMAL,
            x=0, y=0, w=0, h=0, pl=4, pr=4, pt=1, pb=1)

        # ---- Model Copy / Convert module -------------------------------
        self.copyFrame = FXVerticalFrame(self,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)

        gbCopyModels = FXGroupBox(p=self.copyFrame, text='Model Copy', opts=FRAME_GROOVE)
        vaCopy = AFXVerticalAligner(p=gbCopyModels, opts=0,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=vaCopy, ncols=16, labelText='Source model:', tgt=form.currentModelNameKw, sel=0)
        AFXTextField(p=vaCopy, ncols=16, labelText='Target model:', tgt=form.targetModelNameKw, sel=0)

        gbConvert = FXGroupBox(p=self.copyFrame, text='Convert Step Type', opts=FRAME_GROOVE)
        FXRadioButton(p=gbConvert, text='Visco', tgt=form.convertStepTypeKw1, sel=811)
        FXRadioButton(p=gbConvert, text='Static General', tgt=form.convertStepTypeKw1, sel=812)
        FXRadioButton(p=gbConvert, text='Coupled Temp-Displacement', tgt=form.convertStepTypeKw1, sel=813)

        runCopyHf = FXHorizontalFrame(p=self.copyFrame, opts=LAYOUT_CENTER_X,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=DEFAULT_SPACING, pb=0)
        FXButton(p=runCopyHf, text='Execute Model Copy / Convert', tgt=self,
            sel=self.ID_RUN_COPY, opts=BUTTON_NORMAL,
            x=0, y=0, w=0, h=0, pl=4, pr=4, pt=1, pb=1)

        # ---- Birth / Death module --------------------------------------
        self.birthFrame = FXVerticalFrame(self,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)

        gbBirth = FXGroupBox(p=self.birthFrame, text='Model Change Interaction', opts=FRAME_GROOVE)
        vaBirth = AFXVerticalAligner(p=gbBirth, opts=0,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=vaBirth, ncols=16, labelText='Model:', tgt=form.currentModelNameKw, sel=0)
        AFXTextField(p=vaBirth, ncols=16, labelText='Instance name:', tgt=form.partInstanceNameKw, sel=0)
        self.killAllInteractionCombo = AFXComboBox(vaBirth, 16, 5, 'Kill all interaction:',
            self, self.ID_KILL_ALL, LAYOUT_FILL_X)
        FXButton(p=vaBirth, text='Read Interactions', tgt=self,
            sel=self.ID_READ_INTERACTIONS, opts=BUTTON_NORMAL,
            x=0, y=0, w=0, h=0, pl=2, pr=2, pt=1, pb=1)
        AFXTextField(p=vaBirth, ncols=16, labelText='Set prefix:', tgt=form.setPrefixKw, sel=0)
        AFXTextField(p=vaBirth, ncols=16, labelText='Interaction prefix:', tgt=form.interactionPrefixKw, sel=0)
        AFXTextField(p=vaBirth, ncols=16, labelText='Number of passes:', tgt=form.numSegmentsKw, sel=0)
        FXCheckButton(p=gbBirth, text='Active in step', tgt=form.activeInStepKw, sel=0, opts=CHECKBUTTON_NORMAL)
        FXCheckButton(p=gbBirth, text='Include strain', tgt=form.includeStrainKw, sel=0, opts=CHECKBUTTON_NORMAL)

        runBirthHf = FXHorizontalFrame(p=self.birthFrame, opts=LAYOUT_CENTER_X,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=DEFAULT_SPACING, pb=0)
        FXButton(p=runBirthHf, text='Execute Birth / Death', tgt=self,
            sel=self.ID_RUN_BIRTH, opts=BUTTON_NORMAL,
            x=0, y=0, w=0, h=0, pl=4, pr=4, pt=1, pb=1)

        # ---- Heat Input module -----------------------------------------
        self.heatFrame = FXVerticalFrame(self,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)

        gbHeat = FXGroupBox(p=self.heatFrame, text='Body Heat Flux', opts=FRAME_GROOVE)
        vaHeat = AFXVerticalAligner(p=gbHeat, opts=0,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=vaHeat, ncols=16, labelText='Model:', tgt=form.currentModelNameKw, sel=0)
        AFXTextField(p=vaHeat, ncols=16, labelText='Instance name:', tgt=form.partInstanceNameKw, sel=0)
        self.loadStepCombo = AFXComboBox(vaHeat, 16, 5, 'Load start step:',
            self, self.ID_LOAD_STEP, LAYOUT_FILL_X)
        AFXTextField(p=vaHeat, ncols=16, labelText='Set prefix:', tgt=form.setPrefixKw, sel=0)
        AFXTextField(p=vaHeat, ncols=16, labelText='Number of passes:', tgt=form.numSegmentsKw, sel=0)
        AFXTextField(p=vaHeat, ncols=16, labelText='Body heat flux:', tgt=form.heatFluxKw, sel=0)
        AFXTextField(p=vaHeat, ncols=16, labelText='Amplitude:', tgt=form.amplitudeNameKw, sel=0)
        AFXTextField(p=vaHeat, ncols=16, labelText='Load prefix:', tgt=form.loadPrefixKw, sel=0)

        runHeatHf = FXHorizontalFrame(p=self.heatFrame, opts=LAYOUT_CENTER_X,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=DEFAULT_SPACING, pb=0)
        FXButton(p=runHeatHf, text='Execute Heat Input', tgt=self,
            sel=self.ID_RUN_HEAT, opts=BUTTON_NORMAL,
            x=0, y=0, w=0, h=0, pl=4, pr=4, pt=1, pb=1)

        # ---- Temp Field Import module ----------------------------------
        self.tempFrame = FXVerticalFrame(self,
            opts=FRAME_RAISED|FRAME_THICK|LAYOUT_FILL_X,
            x=0, y=0, w=0, h=0, pl=DEFAULT_SPACING, pr=DEFAULT_SPACING,
            pt=DEFAULT_SPACING, pb=DEFAULT_SPACING, hs=DEFAULT_SPACING, vs=DEFAULT_SPACING)

        gbTemp = FXGroupBox(p=self.tempFrame, text='Temperature Predefined Field From ODB', opts=FRAME_GROOVE)
        vaTemp = AFXVerticalAligner(p=gbTemp, opts=0,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=0, pb=0)
        AFXTextField(p=vaTemp, ncols=16, labelText='Model:', tgt=form.currentModelNameKw, sel=0)
        AFXTextField(p=vaTemp, ncols=16, labelText='Instance name:', tgt=form.partInstanceNameKw, sel=0)
        AFXTextField(p=vaTemp, ncols=16, labelText='Number of passes:', tgt=form.numSegmentsKw, sel=0)
        AFXTextField(p=vaTemp, ncols=16, labelText='Step prefix:', tgt=form.stepPrefixKw, sel=0)
        AFXTextField(p=vaTemp, ncols=16, labelText='Temp pref field prefix:', tgt=form.tempPredefPrefixKw, sel=0)
        AFXTextField(p=vaTemp, ncols=16, labelText='Temp set name:', tgt=form.tempSetNameKw, sel=0)
        AFXTextField(p=vaTemp, ncols=16, labelText='Thermal ODB file:', tgt=form.tempOdbFileKw, sel=0)
        AFXTextField(p=vaTemp, ncols=16, labelText='Temp field start step:', tgt=form.tempFieldStartKw, sel=0)
        AFXTextField(p=vaTemp, ncols=16, labelText='Temp field end step (0=auto):', tgt=form.tempFieldEndKw, sel=0)

        runTempHf = FXHorizontalFrame(p=self.tempFrame, opts=LAYOUT_CENTER_X,
            x=0, y=0, w=0, h=0, pl=0, pr=0, pt=DEFAULT_SPACING, pb=0)
        FXButton(p=runTempHf, text='Execute Temp Field Import', tgt=self,
            sel=self.ID_RUN_TEMP, opts=BUTTON_NORMAL,
            x=0, y=0, w=0, h=0, pl=4, pr=4, pt=1, pb=1)

        # ---- Module visibility transitions ------------------------------
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 701,
            self.stepsFrame, MKUINT(FXWindow.ID_SHOW, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 702,
            self.stepsFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 703,
            self.stepsFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 704,
            self.stepsFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 705,
            self.stepsFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)

        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 701,
            self.copyFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 702,
            self.copyFrame, MKUINT(FXWindow.ID_SHOW, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 703,
            self.copyFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 704,
            self.copyFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 705,
            self.copyFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)

        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 701,
            self.birthFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 702,
            self.birthFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 703,
            self.birthFrame, MKUINT(FXWindow.ID_SHOW, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 704,
            self.birthFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 705,
            self.birthFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)

        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 701,
            self.heatFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 702,
            self.heatFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 703,
            self.heatFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 704,
            self.heatFrame, MKUINT(FXWindow.ID_SHOW, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 705,
            self.heatFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)

        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 701,
            self.tempFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 702,
            self.tempFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 703,
            self.tempFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 704,
            self.tempFrame, MKUINT(FXWindow.ID_HIDE, SEL_COMMAND), None)
        self.addTransition(form.activeModuleKw1, AFXTransition.EQ, 705,
            self.tempFrame, MKUINT(FXWindow.ID_SHOW, SEL_COMMAND), None)

        self.copyFrame.hide()
        self.birthFrame.hide()
        self.heatFrame.hide()
        self.tempFrame.hide()
        self.refreshStepCombo()
        self.refreshInteractionsCombo()
        self.refreshLoadStepCombo()

    def show(self):
        if not self.shown():
            self.refreshStepCombo()
            self.refreshInteractionsCombo()
            self.refreshLoadStepCombo()
            AFXDataDialog.show(self)

    def _value(self, kw):
        try:
            return kw.getValue()
        except:
            return ''

    def _runCommand(self, functionName, *values):
        args = ', '.join(repr(v) for v in values)
        sendCommand('WeldStepBuilder.%s(%s)' % (functionName, args))

    def _radioString(self, groupName):
        try:
            kw1, kw2, mapping = self.form.radioButtonGroups[groupName]
            value = mapping[kw1.getValue()]
            kw2.setValue(value)
            return value
        except:
            return self._value(self.form.radioButtonGroups[groupName][1])

    def refreshStepCombo(self):
        self.previousStepCombo.clearItems()
        modelName = self._value(self.form.currentModelNameKw)
        steps = []
        try:
            steps = mdb.models[modelName].steps.keys()
        except:
            pass
        names = [s for s in steps if s != 'Initial']
        for name in names:
            self.previousStepCombo.appendItem(name)
        if len(names) > 0:
            previous = self._value(self.form.previousStepNameKw)
            if previous in names:
                index = names.index(previous)
            else:
                index = 0
                self.form.previousStepNameKw.setValue(names[index])
            self.previousStepCombo.setCurrentItem(index)
            self._inferStepInfo(names[index])
        return 1

    def onSelPreviousStep(self, sender, sel, ptr):
        text = self.previousStepCombo.getItemText(self.previousStepCombo.getCurrentItem())
        if text:
            self.form.previousStepNameKw.setValue(text)
            self._inferStepInfo(text)
        return 1

    def _inferStepInfo(self, previousName):
        if not previousName:
            return
        idx = len(previousName)
        while idx > 0 and previousName[idx - 1].isdigit():
            idx = idx - 1
        tail = previousName[idx:]
        if not tail:
            return
        prefix = previousName[:idx]
        try:
            number = int(tail)
        except:
            return
        if number % 2 == 0:
            firstIndex = number // 2 + 1
        else:
            firstIndex = (number + 1) // 2
        if prefix:
            self.form.stepPrefixKw.setValue(prefix)
        self.form.firstIndexKw.setValue(firstIndex)

    def onReadModel(self, sender, sel, ptr):
        try:
            vps = session.viewports[session.currentViewportName]
            name = vps.displayedObject.modelName
            if name:
                self.form.currentModelNameKw.setValue(name)
                self.refreshStepCombo()
                self.refreshInteractionsCombo()
                self.refreshLoadStepCombo()
        except:
            keys = mdb.models.keys()
            if len(keys) > 0:
                self.form.currentModelNameKw.setValue(keys[-1])
                self.refreshStepCombo()
                self.refreshInteractionsCombo()
                self.refreshLoadStepCombo()
        return 1

    def refreshInteractionsCombo(self):
        self.killAllInteractionCombo.clearItems()
        modelName = self._value(self.form.currentModelNameKw)
        interactions = []
        try:
            interactions = mdb.models[modelName].interactions.keys()
        except:
            pass
        for name in interactions:
            self.killAllInteractionCombo.appendItem(name)
        if len(interactions) > 0:
            previous = self._value(self.form.killAllInteractionKw)
            if previous in interactions:
                index = interactions.index(previous)
            else:
                index = 0
                self.form.killAllInteractionKw.setValue(interactions[index])
            self.killAllInteractionCombo.setCurrentItem(index)
        return 1

    def onSelKillAll(self, sender, sel, ptr):
        text = self.killAllInteractionCombo.getItemText(
            self.killAllInteractionCombo.getCurrentItem())
        if text:
            self.form.killAllInteractionKw.setValue(text)
        return 1

    def onReadInteractions(self, sender, sel, ptr):
        self.refreshInteractionsCombo()
        return 1

    def refreshLoadStepCombo(self):
        self.loadStepCombo.clearItems()
        modelName = self._value(self.form.currentModelNameKw)
        steps = []
        try:
            steps = mdb.models[modelName].steps.keys()
        except:
            pass
        names = [s for s in steps if s != 'Initial']
        for name in names:
            self.loadStepCombo.appendItem(name)
        if len(names) > 0:
            previous = self._value(self.form.loadStartStepNameKw)
            if previous in names:
                index = names.index(previous)
            else:
                index = 0
                self.form.loadStartStepNameKw.setValue(names[index])
                self._inferLoadStepInfo(names[index])
            self.loadStepCombo.setCurrentItem(index)
        return 1

    def onSelLoadStep(self, sender, sel, ptr):
        text = self.loadStepCombo.getItemText(self.loadStepCombo.getCurrentItem())
        if text:
            self.form.loadStartStepNameKw.setValue(text)
            self._inferLoadStepInfo(text)
        return 1

    def _inferLoadStepInfo(self, stepName):
        if not stepName:
            return
        idx = len(stepName)
        while idx > 0 and stepName[idx - 1].isdigit():
            idx = idx - 1
        tail = stepName[idx:]
        if not tail:
            return
        prefix = stepName[:idx]
        try:
            number = int(tail)
        except:
            return
        if prefix:
            self.form.stepPrefixKw.setValue(prefix)
        self.form.firstIndexKw.setValue(max(1, (number - 1) // 2))

    def onRunSteps(self, sender, sel, ptr):
        self._runCommand('create_steps',
            self._radioString('stepType'),
            self._value(self.form.numSegmentsKw),
            self._value(self.form.currentModelNameKw),
            '',
            self._value(self.form.stepPrefixKw),
            self._value(self.form.firstIndexKw),
            self._value(self.form.previousStepNameKw),
            self._value(self.form.shortTimePeriodKw),
            self._value(self.form.longTimePeriodKw),
            self._value(self.form.shortInitialIncKw),
            self._value(self.form.longInitialIncKw),
            self._value(self.form.viscoLongInitialIncKw),
            self._value(self.form.maxNumIncKw),
            self._value(self.form.shortMinIncKw),
            self._value(self.form.shortMaxIncKw),
            self._value(self.form.longMinIncKw),
            self._value(self.form.longMaxIncKw),
            self._value(self.form.maxTempChangeKw),
            self._value(self.form.viscoCETolKw))
        return 1

    def onRunCopy(self, sender, sel, ptr):
        self._runCommand('copy_model',
            self._value(self.form.currentModelNameKw),
            self._value(self.form.targetModelNameKw),
            self._radioString('convertStepType'),
            self._value(self.form.stepPrefixKw),
            self._value(self.form.interactionPrefixKw))
        return 1

    def onRunBirth(self, sender, sel, ptr):
        self._runCommand('create_model_change',
            self._value(self.form.numSegmentsKw),
            self._value(self.form.currentModelNameKw),
            self._value(self.form.partInstanceNameKw),
            self._value(self.form.setPrefixKw),
            self._value(self.form.interactionPrefixKw),
            self._value(self.form.killAllInteractionKw),
            self._value(self.form.firstIndexKw),
            self._value(self.form.stepPrefixKw),
            self._value(self.form.activeInStepKw),
            self._value(self.form.includeStrainKw))
        return 1

    def onRunHeat(self, sender, sel, ptr):
        self._runCommand('create_heat_loads',
            self._value(self.form.numSegmentsKw),
            self._value(self.form.currentModelNameKw),
            self._value(self.form.partInstanceNameKw),
            self._value(self.form.setPrefixKw),
            self._value(self.form.heatFluxKw),
            self._value(self.form.amplitudeNameKw),
            self._value(self.form.loadPrefixKw),
            self._value(self.form.firstIndexKw),
            self._value(self.form.stepPrefixKw),
            self._value(self.form.loadStartStepNameKw))
        return 1

    def onRunTemp(self, sender, sel, ptr):
        self._runCommand('create_temp_predefined_fields',
            self._value(self.form.numSegmentsKw),
            self._value(self.form.currentModelNameKw),
            self._value(self.form.partInstanceNameKw),
            self._value(self.form.tempSetNameKw),
            self._value(self.form.tempOdbFileKw),
            self._value(self.form.tempPredefPrefixKw),
            self._value(self.form.tempFieldStartKw),
            self._value(self.form.tempFieldEndKw),
            self._value(self.form.stepPrefixKw))
        return 1
