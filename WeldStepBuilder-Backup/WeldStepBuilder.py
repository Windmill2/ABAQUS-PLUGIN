from abaqus import *
from abaqusConstants import *


def kernel(numSegments, jobType, thermalModelName, structureModelName, partInstanceName,
           setPrefix, stepPrefix, firstIndex, previousStepName, shortTimePeriod,
           longTimePeriod, shortInitialInc, longInitialInc, viscoLongInitialInc, maxNumInc,
           shortMinInc, shortMaxInc, longMinInc, longMaxInc, maxTempChange,
           viscoCETol, heatFlux, amplitudeName, interactionPrefix, loadPrefix,
           tempPredefPrefix, tempSetName, tempOdbFile, tempFieldStart,
           tempFieldEnd, createHeatSteps, createViscoSteps, createModelChange,
           createHeatFluxLoads, createTemperatureFields):

    if numSegments <= 0:
        print 'WeldStepBuilder: Number of passes must be greater than zero.'
        return

    if jobType == 'heat':
        createViscoSteps = False
        createTemperatureFields = False
    elif jobType == 'structure':
        createHeatSteps = False
        createModelChange = False
        createHeatFluxLoads = False
    elif jobType != 'both':
        print 'WeldStepBuilder: Unknown jobType "%s".' % jobType
        return

    if tempFieldEnd <= 0:
        tempFieldEnd = 2 * numSegments + 1

    def stepName(n):
        return '%s%d' % (stepPrefix, n)

    def setName(i):
        return '%s%d' % (setPrefix, i)

    def interactionName(i):
        return '%s%d' % (interactionPrefix, i + 1)

    def loadName(i):
        return '%s%d' % (loadPrefix, i)

    def tempPredefName(i):
        return '%s%d' % (tempPredefPrefix, i + 1)

    thermal = None
    structure = None

    if mdb.models.has_key(thermalModelName):
        thermal = mdb.models[thermalModelName]
    if mdb.models.has_key(structureModelName):
        structure = mdb.models[structureModelName]

    if (createHeatSteps or createModelChange or createHeatFluxLoads) and not thermal:
        print 'WeldStepBuilder: Thermal model "%s" not found.' % thermalModelName
        return

    if (createViscoSteps or createTemperatureFields) and not structure:
        print 'WeldStepBuilder: Structural model "%s" not found.' % structureModelName
        return

    nStepsCreated = 0
    nInteractionsCreated = 0
    nLoadsCreated = 0
    nPredefsCreated = 0

    # Create heat-transfer steps on the thermal model, one short/long pair per pass.
    if createHeatSteps and thermal:
        for i in range(firstIndex, firstIndex + numSegments):
            prev = previousStepName
            if i > firstIndex:
                prev = stepName(2 * i - 1)
            shortStep = stepName(2 * i)
            if not thermal.steps.has_key(prev):
                print 'WeldStepBuilder: Previous step "%s" not found in "%s"; skipped %s.' % (
                    prev, thermalModelName, shortStep)
                continue
            if not thermal.steps.has_key(shortStep):
                thermal.HeatTransferStep(
                    name=shortStep,
                    previous=prev,
                    timePeriod=shortTimePeriod,
                    maxNumInc=maxNumInc,
                    initialInc=shortInitialInc,
                    minInc=shortMinInc,
                    maxInc=shortMaxInc,
                    deltmx=maxTempChange)
                nStepsCreated = nStepsCreated + 1
            longStep = stepName(2 * i + 1)
            if not thermal.steps.has_key(longStep):
                thermal.HeatTransferStep(
                    name=longStep,
                    previous=shortStep,
                    timePeriod=longTimePeriod,
                    maxNumInc=maxNumInc,
                    initialInc=longInitialInc,
                    minInc=longMinInc,
                    maxInc=longMaxInc,
                    deltmx=maxTempChange)
                nStepsCreated = nStepsCreated + 1

    # Create model-change interactions that make the weld material active during the short step.
    if createModelChange and thermal:
        assembly = thermal.rootAssembly
        if assembly.instances.has_key(partInstanceName):
            instance = assembly.instances[partInstanceName]
            for i in range(firstIndex, firstIndex + numSegments):
                setName_ = setName(i)
                if not instance.sets.has_key(setName_):
                    print 'WeldStepBuilder: Set "%s" not found in "%s".' % (setName_, partInstanceName)
                    continue
                step = stepName(2 * i)
                if not thermal.steps.has_key(step):
                    continue
                intName = interactionName(i)
                if thermal.interactions.has_key(intName):
                    continue
                thermal.ModelChange(
                    name=intName,
                    createStepName=step,
                    region=instance.sets[setName_],
                    activeInStep=True,
                    includeStrain=False)
                nInteractionsCreated = nInteractionsCreated + 1
        else:
            print 'WeldStepBuilder: Instance "%s" not found in thermal assembly.' % partInstanceName

    # Create and deactivate body heat-flux loads for each pass.
    if createHeatFluxLoads and thermal:
        assembly = thermal.rootAssembly
        if assembly.instances.has_key(partInstanceName):
            instance = assembly.instances[partInstanceName]
            for i in range(firstIndex, firstIndex + numSegments):
                setName_ = setName(i)
                if not instance.sets.has_key(setName_):
                    print 'WeldStepBuilder: Set "%s" not found in "%s".' % (setName_, partInstanceName)
                    continue
                step = stepName(2 * i + 1)
                if not thermal.steps.has_key(step):
                    continue
                name = loadName(i)
                if thermal.loads.has_key(name):
                    continue
                thermal.BodyHeatFlux(
                    name=name,
                    createStepName=step,
                    region=instance.sets[setName_],
                    magnitude=heatFlux,
                    amplitude=amplitudeName)
                nLoadsCreated = nLoadsCreated + 1
                deactivateStep = stepName(2 * i + 2)
                if thermal.steps.has_key(deactivateStep):
                    thermal.loads[name].deactivate(deactivateStep)
        else:
            print 'WeldStepBuilder: Instance "%s" not found in thermal assembly.' % partInstanceName

    # Create visco-elastic steps on the structural model.
    if createViscoSteps and structure:
        for i in range(firstIndex, firstIndex + numSegments):
            prev = previousStepName
            if i > firstIndex:
                prev = stepName(2 * i - 1)
            shortStep = stepName(2 * i)
            if not structure.steps.has_key(prev):
                print 'WeldStepBuilder: Previous step "%s" not found in "%s"; skipped %s.' % (
                    prev, structureModelName, shortStep)
                continue
            if not structure.steps.has_key(shortStep):
                structure.ViscoStep(
                    name=shortStep,
                    previous=prev,
                    timePeriod=shortTimePeriod,
                    maxNumInc=maxNumInc,
                    initialInc=shortInitialInc,
                    minInc=shortMinInc,
                    maxInc=shortMaxInc,
                    cetol=viscoCETol)
                nStepsCreated = nStepsCreated + 1
            longStep = stepName(2 * i + 1)
            if not structure.steps.has_key(longStep):
                structure.ViscoStep(
                    name=longStep,
                    previous=shortStep,
                    timePeriod=longTimePeriod,
                    maxNumInc=maxNumInc,
                    initialInc=viscoLongInitialInc,
                    minInc=longMinInc,
                    maxInc=longMaxInc,
                    cetol=viscoCETol)
                nStepsCreated = nStepsCreated + 1

    # Create temperature predefined fields from the thermal results ODB.
    if createTemperatureFields and structure:
        assembly = structure.rootAssembly
        if assembly.instances.has_key(partInstanceName):
            instance = assembly.instances[partInstanceName]
            if not instance.sets.has_key(tempSetName):
                print 'WeldStepBuilder: Set "%s" not found in "%s".' % (tempSetName, partInstanceName)
            else:
                for idx in range(tempFieldStart, tempFieldEnd + 1):
                    step = stepName(idx)
                    if not structure.steps.has_key(step):
                        continue
                    name = tempPredefName(idx)
                    if structure.predefinedFields.has_key(name):
                        continue
                    structure.Temperature(
                        name=name,
                        createStepName=step,
                        distributionType=FROM_FILE,
                        fileName=tempOdbFile,
                        beginStep=idx,
                        beginIncrement=None,
                        endStep=idx,
                        endIncrement=None,
                        interpolate=OFF,
                        absoluteExteriorTolerance=0.0,
                        exteriorTolerance=0.05)
                    nPredefsCreated = nPredefsCreated + 1
                    nextStep = stepName(idx + 1)
                    if structure.steps.has_key(nextStep):
                        structure.predefinedFields[name].resetToInitial(stepName=nextStep)
        else:
            print 'WeldStepBuilder: Instance "%s" not found in structural assembly.' % partInstanceName

    print 'WeldStepBuilder finished: %d steps, %d interactions, %d loads, %d temperature fields.' % (
        nStepsCreated, nInteractionsCreated, nLoadsCreated, nPredefsCreated)


# ------------------------------------------------------------------------
# Module entry points used by the redesigned dialog.
# ------------------------------------------------------------------------

def _get_model(modelName):
    if modelName and mdb.models.has_key(modelName):
        return mdb.models[modelName]
    return None


def _stepName(prefix, n):
    return '%s%d' % (prefix, n)


def _tail_number(name):
    """Return (prefix, trailingInt) for names like 'Step-2' or 'Int-1'."""
    if not name:
        return None
    idx = len(name)
    while idx > 0 and name[idx - 1].isdigit():
        idx = idx - 1
    tail = name[idx:]
    if not tail:
        return None
    try:
        return (name[:idx], int(tail))
    except:
        return None


def _step_number_from_name(stepPrefix, stepName):
    if not stepName or not stepPrefix:
        return None
    if stepName in ('Initial', 'initial'):
        return 0
    if stepName.startswith(stepPrefix):
        tail = stepName[len(stepPrefix):]
        try:
            return int(tail)
        except:
            pass
    return None


def _current_model_name():
    try:
        vps = session.viewports[session.currentViewportName]
        if hasattr(vps.displayedObject, 'modelName'):
            name = vps.displayedObject.modelName
            if name:
                return name
    except:
        pass
    if len(mdb.models.keys()) > 0:
        return mdb.models.keys()[-1]
    return 'Model-1'


def _create_step(model, stepType, name, previous, timePeriod, initialInc,
                 maxNumInc, minInc, maxInc, maxTempChange, viscoCETol):
    if stepType == 'HeatTransfer':
        model.HeatTransferStep(
            name=name,
            previous=previous,
            timePeriod=timePeriod,
            maxNumInc=maxNumInc,
            initialInc=initialInc,
            minInc=minInc,
            maxInc=maxInc,
            deltmx=maxTempChange)
    elif stepType == 'Visco':
        model.ViscoStep(
            name=name,
            previous=previous,
            timePeriod=timePeriod,
            maxNumInc=maxNumInc,
            initialInc=initialInc,
            minInc=minInc,
            maxInc=maxInc,
            cetol=viscoCETol)
    elif stepType == 'StaticGeneral':
        model.StaticStep(
            name=name,
            previous=previous,
            timePeriod=timePeriod,
            maxNumInc=maxNumInc,
            initialInc=initialInc,
            minInc=minInc,
            maxInc=maxInc,
            nlgeom=OFF)
    elif stepType == 'CoupledTempDisp':
        model.CoupledTempDisplacementStep(
            name=name,
            previous=previous,
            timePeriod=timePeriod,
            maxNumInc=maxNumInc,
            initialInc=initialInc,
            minInc=minInc,
            maxInc=maxInc,
            deltmx=maxTempChange)
    else:
        print 'WeldStepBuilder: Unknown step type "%s".' % stepType
        return 0
    return 1


def create_steps(stepType, numSegments, modelName, structureModelName,
                 stepPrefix, firstIndex, previousStepName, shortTimePeriod,
                 longTimePeriod, shortInitialInc, longInitialInc,
                 viscoLongInitialInc, maxNumInc, shortMinInc, shortMaxInc,
                 longMinInc, longMaxInc, maxTempChange, viscoCETol):
    if numSegments <= 0:
        print 'WeldStepBuilder: Number of passes must be greater than zero.'
        return

    model = _get_model(modelName)
    if stepType in ('Visco', 'StaticGeneral'):
        # Structural step types can target the structural model if one is given;
        # otherwise they fall back to the current/thermal model name.
        structModel = _get_model(structureModelName)
        if structModel is not None:
            model = structModel

    if model is None:
        print 'WeldStepBuilder: Model "%s" not found.' % modelName
        return

    nCreated = 0
    for i in range(firstIndex, firstIndex + numSegments):
        prev = previousStepName
        if i > firstIndex:
            prev = _stepName(stepPrefix, 2 * i - 1)
        if not model.steps.has_key(prev):
            print 'WeldStepBuilder: Previous step "%s" not found; skipped %s.' % (
                prev, _stepName(stepPrefix, 2 * i))
            continue

        shortName = _stepName(stepPrefix, 2 * i)
        if not model.steps.has_key(shortName):
            if _create_step(model, stepType, shortName, prev,
                            shortTimePeriod, shortInitialInc,
                            maxNumInc, shortMinInc, shortMaxInc,
                            maxTempChange, viscoCETol):
                nCreated = nCreated + 1

        longName = _stepName(stepPrefix, 2 * i + 1)
        if not model.steps.has_key(longName):
            longInitial = longInitialInc
            if stepType == 'Visco':
                longInitial = viscoLongInitialInc
            if _create_step(model, stepType, longName, shortName,
                            longTimePeriod, longInitial,
                            maxNumInc, longMinInc, longMaxInc,
                            maxTempChange, viscoCETol):
                nCreated = nCreated + 1

    print 'WeldStepBuilder create_steps finished: %d steps created (type %s).' % (
        nCreated, stepType)


def create_model_change(numSegments, modelName, partInstanceName, setPrefix,
                        interactionPrefix, killAllInteractionName, firstIndex,
                        stepPrefix, activeInStep, includeStrain):
    if numSegments <= 0:
        print 'WeldStepBuilder: Number of passes must be greater than zero.'
        return
    model = _get_model(modelName)
    if model is None:
        print 'WeldStepBuilder: Model "%s" not found.' % modelName
        return

    assembly = model.rootAssembly
    if not assembly.instances.has_key(partInstanceName):
        print 'WeldStepBuilder: Instance "%s" not found.' % partInstanceName
        return
    instance = assembly.instances[partInstanceName]

    nextIndex = firstIndex
    if killAllInteractionName and model.interactions.has_key(killAllInteractionName):
        intr = model.interactions[killAllInteractionName]
        killStep = _get_default(intr, 'createStepName', '')
        if killStep:
            idx = len(killStep)
            while idx > 0 and killStep[idx - 1].isdigit():
                idx = idx - 1
            if idx > 0 and idx < len(killStep):
                stepPrefix = killStep[:idx]
        if interactionPrefix and killAllInteractionName.startswith(interactionPrefix):
            tail = killAllInteractionName[len(interactionPrefix):]
            try:
                selectedNumber = int(tail)
                nextIndex = max(firstIndex, selectedNumber)
            except:
                pass
        if nextIndex == firstIndex:
            killIndex = _step_number_from_name(stepPrefix, killStep)
            if killIndex is not None:
                nextIndex = max(firstIndex, killIndex // 2 + 1)

    nCreated = 0
    for i in range(nextIndex, nextIndex + numSegments):
        setName_ = _stepName(setPrefix, i)
        if not instance.sets.has_key(setName_):
            print 'WeldStepBuilder: Set "%s" not found in "%s".' % (
                setName_, partInstanceName)
            continue
        step = _stepName(stepPrefix, 2 * i)
        if not model.steps.has_key(step):
            continue
        intName = '%s%d' % (interactionPrefix, i + 1)
        if model.interactions.has_key(intName):
            continue
        model.ModelChange(
            name=intName,
            createStepName=step,
            region=instance.sets[setName_],
            activeInStep=activeInStep,
            includeStrain=includeStrain)
        nCreated = nCreated + 1

    print 'WeldStepBuilder create_model_change finished: %d interactions created.' % nCreated


def create_heat_loads(numSegments, modelName, partInstanceName, setPrefix,
                      heatFlux, amplitudeName, loadPrefix, firstIndex,
                      stepPrefix, loadStartStepName=''):
    if numSegments <= 0:
        print 'WeldStepBuilder: Number of passes must be greater than zero.'
        return
    model = _get_model(modelName)
    if model is None:
        print 'WeldStepBuilder: Model "%s" not found.' % modelName
        return

    assembly = model.rootAssembly
    if not assembly.instances.has_key(partInstanceName):
        print 'WeldStepBuilder: Instance "%s" not found.' % partInstanceName
        return
    instance = assembly.instances[partInstanceName]

    startIndex = firstIndex
    if loadStartStepName:
        prefixEnd = len(loadStartStepName)
        while prefixEnd > 0 and loadStartStepName[prefixEnd - 1].isdigit():
            prefixEnd = prefixEnd - 1
        if prefixEnd > 0 and prefixEnd < len(loadStartStepName):
            stepPrefix = loadStartStepName[:prefixEnd]
            try:
                loadStep = int(loadStartStepName[prefixEnd:])
                startIndex = max(firstIndex, (loadStep - 1) // 2)
            except:
                pass

    nLoadsCreated = 0
    for i in range(startIndex, startIndex + numSegments):
        setName_ = _stepName(setPrefix, i)
        if not instance.sets.has_key(setName_):
            print 'WeldStepBuilder: Set "%s" not found in "%s".' % (
                setName_, partInstanceName)
            continue
        step = _stepName(stepPrefix, 2 * i + 1)
        if not model.steps.has_key(step):
            continue
        name = '%s%d' % (loadPrefix, i)
        if model.loads.has_key(name):
            continue
        model.BodyHeatFlux(
            name=name,
            createStepName=step,
            region=instance.sets[setName_],
            magnitude=heatFlux,
            amplitude=amplitudeName)
        nLoadsCreated = nLoadsCreated + 1
        deactivateStep = _stepName(stepPrefix, 2 * i + 2)
        if model.steps.has_key(deactivateStep):
            model.loads[name].deactivate(deactivateStep)

    print 'WeldStepBuilder create_heat_loads finished: %d loads created.' % nLoadsCreated


def create_temp_predefined_fields(numSegments, modelName, partInstanceName,
                                  tempSetName, tempOdbFile, tempPredefPrefix,
                                  tempFieldStart, tempFieldEnd, stepPrefix):
    if numSegments <= 0:
        print 'WeldStepBuilder: Number of passes must be greater than zero.'
        return
    model = _get_model(modelName)
    if model is None:
        print 'WeldStepBuilder: Model "%s" not found.' % modelName
        return

    assembly = model.rootAssembly
    if not assembly.instances.has_key(partInstanceName):
        print 'WeldStepBuilder: Instance "%s" not found.' % partInstanceName
        return
    instance = assembly.instances[partInstanceName]

    if tempFieldEnd <= 0:
        tempFieldEnd = 2 * numSegments + 1

    nPredefsCreated = 0
    for idx in range(tempFieldStart, tempFieldEnd + 1):
        step = _stepName(stepPrefix, idx)
        if not model.steps.has_key(step):
            continue
        name = '%s%d' % (tempPredefPrefix, idx + 1)
        if model.predefinedFields.has_key(name):
            continue
        kwargs = {
            'name': name,
            'createStepName': step,
            'distributionType': FROM_FILE,
            'fileName': tempOdbFile,
            'beginStep': idx,
            'beginIncrement': None,
            'endStep': idx,
            'endIncrement': None,
            'interpolate': OFF,
            'absoluteExteriorTolerance': 0.0,
            'exteriorTolerance': 0.05,
        }
        if tempSetName and instance.sets.has_key(tempSetName):
            kwargs['region'] = instance.sets[tempSetName]
        elif tempSetName:
            print 'WeldStepBuilder: Temp set "%s" not found in "%s".' % (
                tempSetName, partInstanceName)
            continue
        model.Temperature(**kwargs)
        nPredefsCreated = nPredefsCreated + 1
        nextStep = _stepName(stepPrefix, idx + 1)
        if model.steps.has_key(nextStep):
            model.predefinedFields[name].resetToInitial(stepName=nextStep)

    print 'WeldStepBuilder create_temp_predefined_fields finished: %d fields imported.' % nPredefsCreated


def _get_default(obj, name, default):
    try:
        if hasattr(obj, name):
            value = getattr(obj, name)
            if value is not None:
                return value
    except:
        pass
    return default


def _is_model_change_interaction(intr):
    try:
        clsName = intr.__class__.__name__.lower()
        if 'modelchange' in clsName or 'model_change' in clsName:
            return True
    except:
        pass
    for attrName in ('type', 'interactionType'):
        try:
            intType = str(_get_default(intr, attrName, '')).lower().replace('_', ' ')
            if 'model change' in intType or 'modelchange' in intType:
                return True
        except:
            pass
    return False


def _history_created_indexes(interaction):
    """Return the indexes of CREATED entries in an interaction history."""
    hist = _get_default(interaction, 'history', None)
    if hist is None:
        return []
    try:
        values = list(hist)
    except Exception:
        return []
    indexes = []
    for i, value in enumerate(values):
        try:
            label = str(value)
        except Exception:
            label = repr(value)
        upper = label.strip().upper()
        if upper == 'CREATED' or upper.endswith('CREATED'):
            indexes.append(i)
    return indexes


def _source_created_step_name(source, intrName):
    """Recover the step where a ModelChange interaction was created.

    Abaqus does not expose createStepName on a ModelChange object, but the
    interaction.history list lines up with source.steps.keys() and contains a
    CREATED marker at the step where the interaction was introduced. That is
    much more reliable than reconstructing names like Int-1 -> Step-2.
    """
    if not source:
        return ''
    if not source.interactions.has_key(intrName):
        return ''
    intr = source.interactions[intrName]
    indexes = _history_created_indexes(intr)
    if not indexes:
        return ''
    steps = list(source.steps.keys())
    nonInit = [name for name in steps if name != 'Initial']
    history = _get_default(intr, 'history', None)
    try:
        histLen = len(history)
    except Exception:
        histLen = -1
    # Normally history length matches len(steps), including Initial.
    if len(steps) == histLen:
        idx = indexes[0]
        if idx == 0 and len(indexes) > 1:
            idx = indexes[1]
        if idx < len(steps):
            return steps[idx]
    # Fall back if history excludes Initial.
    if len(nonInit) == histLen:
        idx = indexes[0]
        if idx < len(nonInit):
            return nonInit[idx]
    return ''


def _resolve_model_change_region(intr, assembly):
    region = _get_default(intr, 'region', None)
    if region is None:
        return None

    # In Abaqus 6.14/6.16 the region of a ModelChange interaction may be a
    # tuple such as ('setName', 'partName', 'instanceName', ...) instead of a
    # Region object. Try the tuple form first because attribute access on a
    # tuple in Abaqus' Python 2 kernel returns an error object rather than
    # raising AttributeError, which breaks the fallback logic below.
    if isinstance(region, tuple) or isinstance(region, list):
        def _name(value):
            if isinstance(value, basestring):
                if value:
                    return value
            return None
        setName = None
        instanceName = None
        partName = None
        if len(region) > 0:
            setName = _name(region[0])
        if len(region) > 1:
            partName = _name(region[1])
        if len(region) > 2:
            instanceName = _name(region[2])
        if setName:
            if instanceName and assembly.instances.has_key(instanceName):
                inst = assembly.instances[instanceName]
                if inst.sets.has_key(setName):
                    return inst.sets[setName]
            if assembly.sets.has_key(setName):
                return assembly.sets[setName]
            for inst in assembly.instances.values():
                if partName and not instanceName:
                    try:
                        if inst.part.name != partName:
                            continue
                    except:
                        pass
                if inst.sets.has_key(setName):
                    return inst.sets[setName]
        return None

    setName = None
    instanceName = None
    try:
        setName = region.name
    except:
        pass
    try:
        inst = region.instance
        if inst is not None:
            instanceName = inst.name
    except:
        pass
    if setName is None:
        try:
            sets = region.sets
            if sets:
                setName = sets.keys()[0]
        except:
            pass
    if instanceName is None:
        instanceName = _get_default(region, 'instanceName', None)
    if setName is None:
        return None
    if instanceName and assembly.instances.has_key(instanceName):
        inst = assembly.instances[instanceName]
        if inst.sets.has_key(setName):
            return inst.sets[setName]
    if assembly.sets.has_key(setName):
        return assembly.sets[setName]
    for inst in assembly.instances.values():
        if inst.sets.has_key(setName):
            return inst.sets[setName]
    return None


def _infer_copy_step_name(source, target, stepPrefix, interactionPrefix, intrName):
    """Derive the step where a copied ModelChange interaction should be created.

    The Birth/Death module creates interactions named ``<prefix><n>`` at the
    short (even-numbered) step ``<stepPrefix><2*n>``. Abaqus does not expose
    ``createStepName`` on a ModelChange object, so we rebuild the name from the
    interaction number only as a fallback; when history is available it gives
    the real created step directly.
    """

    createdByHistory = _source_created_step_name(source, intrName)
    if createdByHistory:
        return createdByHistory

    pair = _tail_number(intrName)
    stepIndex = None
    if pair is not None:
        prefix, number = pair
        stepIndex = 2 * number

    stepPrefix = stepPrefix or ''
    if not stepPrefix:
        # Infer from source steps that end in a trailing number, e.g. 'Step-2'.
        prefixCounts = {}
        for stepName in source.steps.keys():
            if stepName == 'Initial':
                continue
            pairStep = _tail_number(stepName)
            if pairStep is not None:
                prefix, number = pairStep
                if prefix:
                    prefixCounts[prefix] = prefixCounts.get(prefix, 0) + 1
        if prefixCounts:
            stepPrefix = max(prefixCounts.keys(), key=lambda k: prefixCounts[k])

    if stepIndex is None:
        # Fall back to the createStepName attribute; Abaqus may expose it in
        # some versions, even though 6.14/6.16 normally do not.
        return _get_default(intr, 'createStepName', '')

    name = _stepName(stepPrefix, stepIndex)
    if target.steps.has_key(name):
        return name
    return ''


def _step_order(model, stepName):
    """Return a sortable index for a step name by matching the model order."""
    try:
        keys = list(model.steps.keys())
        if stepName in keys:
            return keys.index(stepName)
    except Exception:
        pass
    pair = _tail_number(stepName)
    if pair is not None:
        _, number = pair
        return number * 1000
    return 10 ** 9


def _copy_model_change_interactions(source, target, stepPrefix, interactionPrefix):
    if not hasattr(target, 'ModelChange'):
        return 0
    assembly = target.rootAssembly
    sourceInteractions = []
    for name in source.interactions.keys():
        intr = source.interactions[name]
        if not _is_model_change_interaction(intr):
            continue
        if target.interactions.has_key(name):
            continue
        sourceInteractions.append((name, intr))

    # The thermal source model normally starts with one kill-all ModelChange,
    # then activates the weld metal one pass at a time. Abaqus does not expose
    # activeInStep as an attribute, so we mark the first created interaction
    # (in source step order) as the kill-all/inactive one and the rest as
    # activations.
    createdSteps = {}
    for name, intr in sourceInteractions:
        createdSteps[name] = _source_created_step_name(source, name)
    orderedNames = sorted(
        sourceInteractions,
        key=lambda item: _step_order(source, createdSteps[item[0]]))
    inactiveNames = set()
    if orderedNames:
        inactiveNames.add(orderedNames[0][0])

    nCopied = 0
    for name, intr in sourceInteractions:
        createStepName = _infer_copy_step_name(
            source, target, stepPrefix, interactionPrefix, name)
        if createStepName and not target.steps.has_key(createStepName):
            continue
        region = _resolve_model_change_region(intr, assembly)
        if region is None:
            print 'WeldStepBuilder: Could not resolve region for interaction "%s"; skipped.' % name
            continue
        activeInStep = name not in inactiveNames
        includeStrain = _get_default(intr, 'includeStrain', False)
        try:
            target.ModelChange(
                name=name,
                createStepName=createStepName,
                region=region,
                activeInStep=activeInStep,
                includeStrain=includeStrain)
            nCopied = nCopied + 1
        except Exception as exc:
            print 'WeldStepBuilder: Could not create ModelChange "%s" in step "%s": %s' % (
                name, createStepName, exc)
    return nCopied


def copy_model(sourceModelName, targetModelName, convertStepType,
               stepPrefix, interactionPrefix):
    source = _get_model(sourceModelName)
    if source is None:
        print 'WeldStepBuilder: Source model "%s" not found.' % sourceModelName
        return

    if mdb.models.has_key(targetModelName):
        print 'WeldStepBuilder: Target model "%s" exists; deleting it for a fresh copy.' % targetModelName
        del mdb.models[targetModelName]
    target = mdb.Model(name=targetModelName, objectToCopy=source)

    def getAttr(step, name, default):
        try:
            if hasattr(step, name):
                value = getattr(step, name)
                if value is not None:
                    return value
        except:
            pass
        return default

    records = []
    for name in target.steps.keys():
        if name == 'Initial':
            continue
        old = target.steps[name]
        records.append({
            'name': name,
            'previous': getAttr(old, 'previous', 'Initial'),
            'timePeriod': getAttr(old, 'timePeriod', 800.0),
            'initialInc': getAttr(old, 'initialInc', 0.001),
            'minInc': getAttr(old, 'minInc', 1e-06),
            'maxInc': getAttr(old, 'maxInc', 50.0),
            'maxNumInc': getAttr(old, 'maxNumInc', 100000),
            'deltmx': getAttr(old, 'deltmx', 100.0),
            'cetol': getAttr(old, 'cetol', 0.0001),
        })

    for rec in records:
        del target.steps[rec['name']]

    for rec in records:
        _create_step(target, convertStepType, rec['name'], rec['previous'],
                     rec['timePeriod'], rec['initialInc'], rec['maxNumInc'],
                     rec['minInc'], rec['maxInc'], rec['deltmx'], rec['cetol'])

    nInteractionsCopied = _copy_model_change_interactions(
        source, target, stepPrefix, interactionPrefix)

    print 'WeldStepBuilder copy_model finished: %d model-change interactions copied.' % nInteractionsCopied
