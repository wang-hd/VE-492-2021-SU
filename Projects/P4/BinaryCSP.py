from collections import deque
from Interface import *


# = = = = = = = QUESTION 1  = = = = = = = #


def consistent(assignment, csp, var, value):
    """
    Checks if a value assigned to a variable is consistent with all binary constraints in a problem.
    Do not assign value to var.
    Only check if this value would be consistent or not.
    If the other variable for a constraint is not assigned,
    then the new value is consistent with the constraint.

    Args:
        assignment (Assignment): the partial assignment
        csp (ConstraintSatisfactionProblem): the problem definition
        var (string): the variable that would be assigned
        value (value): the value that would be assigned to the variable
    Returns:
        boolean
        True if the value would be consistent with all currently assigned values, False otherwise
    """
    # TODO: Question 1
    for constraints in csp.binaryConstraints:
        if constraints.affects(var):
            others = constraints.otherVariable(var)
            if assignment.isAssigned(others) and not constraints.isSatisfied(value, assignment.assignedValues[others]):
                return False
    return True


def recursiveBacktracking(assignment, csp, orderValuesMethod, selectVariableMethod, inferenceMethod):
    """
    Recursive backtracking algorithm.
    A new assignment should not be created.
    The assignment passed in should have its domains updated with inferences.
    In the case that a recursive call returns failure or a variable assignment is incorrect,
    the inferences made along the way should be reversed.
    See maintainArcConsistency and forwardChecking for the format of inferences.

    Examples of the functions to be passed in:
    orderValuesMethod: orderValues, leastConstrainingValuesHeuristic
    selectVariableMethod: chooseFirstVariable, minimumRemainingValuesHeuristic
    inferenceMethod: noInferences, maintainArcConsistency, forwardChecking

    Args:
        assignment (Assignment): a partial assignment to expand upon
        csp (ConstraintSatisfactionProblem): the problem definition
        orderValuesMethod (function<assignment, csp, variable> returns list<value>):
            a function to decide the next value to try
        selectVariableMethod (function<assignment, csp> returns variable):
            a function to decide which variable to assign next
        inferenceMethod (function<assignment, csp, variable, value> returns set<variable, value>):
            a function to specify what type of inferences to use
    Returns:
        Assignment
        A completed and consistent assignment. None if no solution exists.
    """
    # TODO: Question 1
    if assignment.isComplete():
        return assignment
    var = selectVariableMethod(assignment, csp)
    if var == None:
        return None
    values = orderValuesMethod(assignment, csp, var)
    inferences = set([])
    for value in values:
        if consistent(assignment, csp, var, value):
            assignment.assignedValues[var] = value
            inferences = inferenceMethod(assignment, csp, var, value)
            if inferences != None:
                result = recursiveBacktracking(assignment, csp, orderValuesMethod, selectVariableMethod, inferenceMethod)
                if result != None:
                    return result
        assignment.assignedValues[var] = None
        if inferences != None:
            for inference in inferences:
                assignment.varDomains[inference[0]].add(inference[1])

    return None


def eliminateUnaryConstraints(assignment, csp):
    """
    Uses unary constraints to eleminate values from an assignment.

    Args:
        assignment (Assignment): a partial assignment to expand upon
        csp (ConstraintSatisfactionProblem): the problem definition
    Returns:
        Assignment
        An assignment with domains restricted by unary constraints. None if no solution exists.
    """
    domains = assignment.varDomains
    for var in domains:
        for constraint in (c for c in csp.unaryConstraints if c.affects(var)):
            for value in (v for v in list(domains[var]) if not constraint.isSatisfied(v)):
                domains[var].remove(value)
                # Failure due to invalid assignment
                if len(domains[var]) == 0:
                    return None
    return assignment


def chooseFirstVariable(assignment, csp):
    """
    Trivial method for choosing the next variable to assign.
    Uses no heuristics.
    """
    for var in csp.varDomains:
        if not assignment.isAssigned(var):
            return var


# = = = = = = = QUESTION 2  = = = = = = = #


def minimumRemainingValuesHeuristic(assignment, csp):
    """
    Selects the next variable to try to give a value to in an assignment.
    Uses minimum remaining values heuristic to pick a variable. Use degree heuristic for breaking ties.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
    Returns:
        the next variable to assign
    """
    nextVar = None
    domains = assignment.varDomains

    # TODO: Question 2
    def degreeHeruistic(csp, assignment, var):
        degree = 0
        for constraint in csp.binaryConstraints:
            others = assignment.isAssigned(constraint.otherVariable(var))
            if constraint.affects(var) and others == None:
                degree += 1
        return degree

    vars = [domain for domain in domains if not assignment.isAssigned(domain)]
    minLen = float('inf')
    minVar = None
    for var in vars:
        if len(domains[var]) <= minLen:
            if len(domains[var]) < minLen or degreeHeruistic(csp, assignment, var) < degreeHeruistic(csp, assignment, minLen):
                minLen = len(domains[var])
                minVar = var
    return minVar


def orderValues(assignment, csp, var):
    """
    Trivial method for ordering values to assign.
    Uses no heuristics.
    """
    return list(assignment.varDomains[var])


# = = = = = = = QUESTION 3  = = = = = = = #


def leastConstrainingValuesHeuristic(assignment, csp, var):
    """
    Creates an ordered list of the remaining values left for a given variable.
    Values should be attempted in the order returned.
    The least constraining value should be at the front of the list.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var (string): the variable to be assigned the values
    Returns:
        list<values>
        a list of the possible values ordered by the least constraining value heuristic
    """
    # TODO: Question 3
    dict = {}
    domain = assignment.varDomains[var]
    for val in domain:
        count = 0
        assignment.assignedValues[var] = val
        for constraint in csp.binaryConstraints:
            if constraint.affects(var):
                other = constraint.otherVariable(var)
                for otherVal in assignment.varDomains[other]:
                    if consistent(assignment, csp, other, otherVal):
                        count += 1
        dict[val] = count
        assignment.assignedValues[var] = None
    dict = sorted(dict.items(), key = lambda kv:(kv[1], kv[0]), reverse=True)
    answer = [item[0] for item in dict]
    return answer


def noInferences(assignment, csp, var, value):
    """
    Trivial method for making no inferences.
    """
    return set([])


# = = = = = = = QUESTION 4  = = = = = = = #


def forwardChecking(assignment, csp, var, value):
    """
    Implements the forward checking algorithm.
    Each inference should take the form of (variable, value)
    where the value is being removed from the domain of variable.
    This format is important so that the inferences can be reversed
    if they result in a conflicting partial assignment.
    If the algorithm reveals an inconsistency,
    any inferences made should be reversed before ending the function.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var (string): the variable that has just been assigned a value
        value (string): the value that has just been assigned
    Returns:
        set< tuple<variable, value> >
        the inferences made in this call or None if inconsistent assignment
    """
    inferences = set([])

    # TODO: Question 4
    for constraint in csp.binaryConstraints:
        if constraint.affects(var):
            other = constraint.otherVariable(var)
            if not assignment.isAssigned(other):
                removed = set([])
                for val in assignment.varDomains[other]:
                    if not consistent(assignment, csp, other, val):
                        inferences.add((other, val))
                        removed.add(val)
                if removed == assignment.varDomains[other]:
                    return None
    for inference in inferences:
        assignment.varDomains[inference[0]].remove(inference[1])

    return inferences


# = = = = = = = QUESTION 5  = = = = = = = #


def revise(assignment, csp, var1, var2, constraint):
    """
    Helper function to maintainArcConsistency and AC3.
    Remove values from var2 domain if constraint cannot be satisfied.
    Each inference should take the form of (variable, value)
    where the value is being removed from the domain of variable.
    This format is important so that the inferences can be reversed
    if they result in a conflicting partial assignment.
    If the algorithm reveals an inconsistency,
    any inferences made should be reversed before ending the function.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var1 (string): the variable with consistent values
        var2 (string): the variable that should have inconsistent values removed
        constraint (BinaryConstraint): the constraint connecting var1 and var2
    Returns:
        set<tuple<variable, value>>
        the inferences made in this call or None if inconsistent assignment
    """
    inferences = set([])

    # TODO: Question 5
    for val2 in assignment.varDomains[var2]:
        flag = False
        for val1 in assignment.varDomains[var1]:
            if constraint.isSatisfied(val1, val2):
                flag = True
                break
        if not flag:
            inferences.add((var2, val2))
    for inference in inferences:
        assignment.varDomains[inference[0]].remove(inference[1])
    if len(assignment.varDomains[var2]) == 0:
        return None
    return inferences


def maintainArcConsistency(assignment, csp, var, value):
    """
    Implements the maintaining arc consistency algorithm.
    Inferences take the form of (variable, value)
    where the value is being removed from the domain of variable.
    This format is important so that the inferences can be reversed
    if they result in a conflicting partial assignment.
    If the algorithm reveals an inconsistency,
    and inferences made should be reversed before ending the function.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
        var (string): the variable that has just been assigned a value
        value (string): the value that has just been assigned
    Returns:
        set<<variable, value>>
        the inferences made in this call or None if inconsistent assignment
    """
    inferences = set([])
    domains = assignment.varDomains

    # TODO: Question 5
    #  Hint: implement revise first and use it as a helper function"""
    reviseQueue = deque()

    for constraint in csp.binaryConstraints:
        if constraint.affects(var):
            reviseQueue.appendleft((var, constraint.otherVariable(var)))

    while len(reviseQueue) != 0:
        xi, xj = reviseQueue.pop()
        for constraint in csp.binaryConstraints:
            if constraint.affects(xi) and constraint.affects(xj):
                revisedInfs = revise(assignment, csp, xi, xj, constraint)
                if revisedInfs == None:
                    for inference in inferences:
                        assignment.varDomains[inference[0]].add(inference[1])
                    return None
                if len(revisedInfs) != 0:
                    for constraint in csp.binaryConstraints:
                        if constraint.affects(xj):
                            reviseQueue.appendleft((xj, constraint.otherVariable(xj)))
                    for revisedInf in revisedInfs:
                        inferences.add(revisedInf)
    return inferences


# = = = = = = = QUESTION 6  = = = = = = = #


def AC3(assignment, csp):
    """
    AC3 algorithm for constraint propagation.
    Used as a pre-processing step to reduce the problem
    before running recursive backtracking.

    Args:
        assignment (Assignment): the partial assignment to expand
        csp (ConstraintSatisfactionProblem): the problem description
    Returns:
        Assignment
        the updated assignment after inferences are made or None if an inconsistent assignment
    """
    inferences = set([])

    # TODO: Question 6
    #  Hint: implement revise first and use it as a helper function"""
    reviseQueue = deque()

    for var in csp.varDomains:
        for constraint in csp.binaryConstraints:
            if constraint.affects(var):
                other = constraint.otherVariable(var)
                reviseQueue.appendleft((var, other))

    while len(reviseQueue) != 0:
        xi, xj = reviseQueue.pop()
        for constraint in csp.binaryConstraints:
            if constraint.affects(xi) and constraint.affects(xj):
                revisedInfs = revise(assignment, csp, xi, xj, constraint)
                if revisedInfs == None:
                    for inference in inferences:
                        assignment.varDomains[inference[0]].add(inference[1])
                    return None
                if len(revisedInfs) != 0:
                    for constraint in csp.binaryConstraints:
                        if constraint.affects(xj):
                            reviseQueue.appendleft((xj, constraint.otherVariable(xj)))
                    for revisedInf in revisedInfs:
                        inferences.add(revisedInf)
    return assignment


def solve(csp, orderValuesMethod=leastConstrainingValuesHeuristic,
          selectVariableMethod=minimumRemainingValuesHeuristic,
          inferenceMethod=forwardChecking, useAC3=True):
    """
    Solves a binary constraint satisfaction problem.

    Args:
        csp (ConstraintSatisfactionProblem): a CSP to be solved
        orderValuesMethod (function): a function to decide the next value to try
        selectVariableMethod (function): a function to decide which variable to assign next
        inferenceMethod (function): a function to specify what type of inferences to use
        useAC3 (boolean): specifies whether to use the AC3 pre-processing step or not
    Returns:
        dictionary<string, value>
        A map from variables to their assigned values. None if no solution exists.
    """
    assignment = Assignment(csp)

    assignment = eliminateUnaryConstraints(assignment, csp)
    if assignment is None:
        return assignment

    if useAC3:
        assignment = AC3(assignment, csp)
        if assignment is None:
            return assignment

    assignment = recursiveBacktracking(assignment, csp, orderValuesMethod, selectVariableMethod, inferenceMethod)
    if assignment is None:
        return assignment

    return assignment.extractSolution()
