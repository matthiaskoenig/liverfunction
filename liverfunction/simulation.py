"""
Simulation helpers.
E.g. Dosing functions.
"""
import logging
import numpy as np
import pandas as pd
from collections import namedtuple

# import libsbml
import roadrunner
from roadrunner import SelectionRecord


# -----------------------------------------------------------------------------
# Dosing
# -----------------------------------------------------------------------------
class Dosing(object):
    """ Description of dosing for simulation."""

    def __init__(self, substance, route, dose, unit):
        self.substance = substance
        self.route = route
        self.dose = dose
        self.unit = unit

    def __repr__(self):
        return "{} [{}] {}".format(self.dose, self.unit, self.route)


def set_dosing(r, dosing, bodyweight=None, show=False):
    """ Sets dosing for simulation. """
    if dosing.route == "oral":
        pid = "PODOSE_{}".format(dosing.substance)
    elif dosing.route == "iv":
        pid = "IVDOSE_{}".format(dosing.substance)
    else:
        raise ValueError("Invalid dosing route: {}".format(dosing.route))

    # get dose in [mg]
    dose = dosing.dose
    if dosing.unit.endswith("kg"):
        if bodyweight is None:
            bodyweight = r.BW
        dose = dose * bodyweight

    # reset the model
    r.reset()
    reset_doses(r)
    r.setValue('init({})'.format(pid), dose)  # set dose in [mg]
    r.reset(SelectionRecord.GLOBAL_PARAMETER)
    r.reset()
    # r.resetAll()?
    if show:
        print_doses(r)


def get_doses_keys(r: roadrunner.ExecutableModel):
    """Get all the parameter ids for dosing information."""
    pids = r.model.getGlobalParameterIds()
    keys = []
    for pid in pids:
        if pid.startswith("PODOSE_") or pid.startswith("IVDOSE_"):
            keys.append(pid)
    return pids


def reset_doses(r):
    """ Sets all doses to zero. """
    for key in get_doses_keys(r):
        r.setValue('init({})'.format(key), 0)  # [mg]
    r.reset(SelectionRecord.GLOBAL_PARAMETER)
    r.reset()


def print_doses(r, name=None):
    """ Prints the complete dose information of the model. """
    if name:
        print('***', name, '***')
    for key in get_doses_keys():
        print('{}\t{}'.format(key, r.getValue(key)))


# -----------------------------------------------------------------------------
# Model loading
# -----------------------------------------------------------------------------
def set_selections(r: roadrunner.ExecutableModel, time=True,
                   floatingSpecies=True,
                   boundarySpecies=True,
                   parameters=True,
                   compartments=True,
                   reactions=True):
    """Sets model timecourse selections.
    Selections are the variables stored in the simulation results.

    :param r:
    :param time:
    :param floatingSpecies:
    :param boundarySpecies:
    :param parameterIds:
    :param compartments:
    :param reactions:
    :return:
    """
    selections = []
    if time:
        selections += ["time"]
    if floatingSpecies:
        selections += r.model.getFloatingSpeciesIds()
    if boundarySpecies:
        selections += r.model.getBoundarySpeciesIds()
    if parameters:
        selections += r.model.getGlobalParameterIds()
    if compartments:
        selections += r.model.getCompartmentIds()
    if reactions:
        selections += r.model.getReactionIds()

    r.timeCourseSelections = selections


def load_model(model_path):
    """ Loads model and sets selections.

    :param model_path:
    :return:
    """
    logging.info('Model:', model_path)
    r = roadrunner.RoadRunner(model_path)
    set_selections(r)
    return r


# -----------------------------------------------------------------------------
# Simulation
# -----------------------------------------------------------------------------
Result = namedtuple("Result", ['base', 'mean', 'std', 'min', 'max'])


def simulate(r, tend, steps, dosing, changes={}, parameters=None,
             sensitivity=0.1, selections=None, yfun=None):
    """ Performs model simulation simulation with option on fallback.

    Does not support changes to the model yet.
    """
    # set selections
    if selections == None:
        set_selections(r)
    else:
        r.timeCourseSelections = selections

    if changes is None:
        changes = {}

    # reset all
    resetAll(r)
    reset_doses(r)

    # dosing
    if dosing is not None:
        # get bodyweight
        if "BW" in changes:
            bodyweight = changes["BW"]
        else:
            bodyweight = r.BW

        set_dosing(r, dosing, bodyweight=bodyweight)

    # general changes
    for key, value in changes.items():
        r[key] = value
    s = r.simulate(start=0, end=tend, steps=steps)
    s_base = pd.DataFrame(s, columns=s.colnames)

    if yfun:
        # conversion functio
        yfun(s_base)

    if parameters is None:
        return s_base
    else:
        # baseline
        Np = 2 * len(parameters)
        (Nt, Ns) = s_base.shape
        shape = (Nt, Ns, Np)

        # empty array for storage
        s_data = np.empty(shape) * np.nan

        # all parameter changes
        idx = 0
        for pid in parameters.keys():
            for change in [1.0 + sensitivity, 1.0 - sensitivity]:
                resetAll(r)
                reset_doses(r)
                # dosing
                if dosing:
                    set_dosing(r, dosing, bodyweight=bodyweight)
                # general changes
                for key, value in changes.items():
                    r[key] = value
                # parameter changes
                value = r[pid]
                new_value = value * change
                r[pid] = new_value

                s = r.simulate(start=0, end=tend, steps=steps)
                if yfun:
                    # conversion function
                    s = pd.DataFrame(s, columns=s.colnames)
                    yfun(s)
                    s_data[:, :, idx] = s
                else:
                    s_data[:, :, idx] = s
                idx += 1

        s_mean = pd.DataFrame(np.mean(s_data, axis=2), columns=s_base.columns)
        s_std = pd.DataFrame(np.std(s_data, axis=2), columns=s_base.columns)
        s_min = pd.DataFrame(np.min(s_data, axis=2), columns=s_base.columns)
        s_max = pd.DataFrame(np.max(s_data, axis=2), columns=s_base.columns)

        return Result(base=s_base, mean=s_mean, std=s_std, min=s_min, max=s_max)


def resetAll(r):
    """ Reset all model variables to CURRENT init(X) values.

    This resets all variables, S1, S2 etc to the CURRENT init(X) values. It also resets all
    parameters back to the values they had when the model was first loaded.
    """
    r.reset(roadrunner.SelectionRecord.TIME |
            roadrunner.SelectionRecord.RATE |
            roadrunner.SelectionRecord.FLOATING |
            roadrunner.SelectionRecord.GLOBAL_PARAMETER)



def parameters_for_sensitivity(r, model_path):
    """ Get the parameter ids for the sensitivity analysis.

    This includes all constant parameters (not changed via assignments),
    excluding
    - parameters with value=0 (no effect on model, dummy parameter)
    - parameters which are physical constants, e.g., molecular weights
    """
    try:
        import tesbml as libsbml
    except ImportError:
        import libsbml

    doc = libsbml.readSBMLFromFile(model_path)
    model = doc.getModel()

    # constant parameters in model
    pids_const = []
    for p in model.getListOfParameters():
        if p.getConstant() == True:
            pids_const.append(p.getId())

    # print('constant parameters:', len(pids_const))

    # filter parameters
    parameters = {}
    for pid in pids_const:
        # dose parameters
        if (pid.startswith("IVDOSE_")) or (pid.startswith("PODOSE_")):
            continue

        # physical parameters
        if (pid.startswith("Mr_")) or pid in ["R_PDB"]:
            continue

        # zero parameters
        value = r[pid]
        if np.abs(value) < 1E-8:
            continue

        parameters[pid] = value

    return parameters
