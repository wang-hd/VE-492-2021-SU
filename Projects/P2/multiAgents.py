from util import manhattanDistance
from game import Directions
import random, util

from game import Agent

class ReflexAgent(Agent):
    """
    A reflex agent chooses an action at each choice point by examining
    its alternatives via a state evaluation function.

    The code below is provided as a guide.  You are welcome to change
    it in any way you see fit, so long as you don't touch our method
    headers.
    """


    def getAction(self, gameState):
        """
        You do not need to change this method, but you're welcome to.

        getAction chooses among the best options according to the evaluation function.

        Just like in the previous project, getAction takes a GameState and returns
        some Directions.X for some X in the set {NORTH, SOUTH, WEST, EAST, STOP}
        """
        # Collect legal moves and successor states
        legalMoves = gameState.getLegalActions()

        # Choose one of the best actions
        scores = [self.evaluationFunction(gameState, action) for action in legalMoves]
        bestScore = max(scores)
        bestIndices = [index for index in range(len(scores)) if scores[index] == bestScore]
        chosenIndex = random.choice(bestIndices) # Pick randomly among the best

        "Add more of your code here if you want to"

        return legalMoves[chosenIndex]

    def evaluationFunction(self, currentGameState, action):
        """
        Design a better evaluation function here.

        The evaluation function takes in the current and proposed successor
        GameStates (pacman.py) and returns a number, where higher numbers are better.

        The code below extracts some useful information from the state, like the
        remaining food (newFood) and Pacman position after moving (newPos).
        newScaredTimes holds the number of moves that each ghost will remain
        scared because of Pacman having eaten a power pellet.

        Print out these variables to see what you're getting, then combine them
        to create a masterful evaluation function.
        """
        # Useful information you can extract from a GameState (pacman.py)
        successorGameState = currentGameState.generatePacmanSuccessor(action)
        newPos = successorGameState.getPacmanPosition()
        newFood = successorGameState.getFood()
        newGhostStates = successorGameState.getGhostStates()
        newScaredTimes = [ghostState.scaredTimer for ghostState in newGhostStates]

        "*** YOUR CODE HERE ***"
        foodDistance = [manhattanDistance(newPos, food) for food in newFood.asList()]
        foodValue = 1/min(foodDistance) if len(foodDistance) != 0 else 0
        ghostDistance = [manhattanDistance(newPos, ghost.getPosition()) for ghost in newGhostStates]
        ghostValue = []
        for i in range(len(newGhostStates)):
            ghostDistance[i] += newScaredTimes[i]
            if ghostDistance[i] == 0:
                ghostValue.append(100)
            else:
                ghostValue.append(1/ghostDistance[i])
        return foodValue - max(ghostValue) + successorGameState.getScore()

def scoreEvaluationFunction(currentGameState):
    """
    This default evaluation function just returns the score of the state.
    The score is the same one displayed in the Pacman GUI.

    This evaluation function is meant for use with adversarial search agents
    (not reflex agents).
    """
    return currentGameState.getScore()

class MultiAgentSearchAgent(Agent):
    """
    This class provides some common elements to all of your
    multi-agent searchers.  Any methods defined here will be available
    to the MinimaxPacmanAgent, AlphaBetaPacmanAgent & ExpectimaxPacmanAgent.

    You *do not* need to make any changes here, but you can if you want to
    add functionality to all your adversarial search agents.  Please do not
    remove anything, however.

    Note: this is an abstract class: one that should not be instantiated.  It's
    only partially specified, and designed to be extended.  Agent (game.py)
    is another abstract class.
    """

    def __init__(self, evalFn = 'scoreEvaluationFunction', depth = '2'):
        self.index = 0 # Pacman is always agent index 0
        self.evaluationFunction = util.lookup(evalFn, globals())
        self.depth = int(depth)

class MinimaxAgent(MultiAgentSearchAgent):
    """
    Your minimax agent (question 2)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action from the current gameState using self.depth
        and self.evaluationFunction.

        Here are some method calls that might be useful when implementing minimax.

        gameState.getLegalActions(agentIndex):
        Returns a list of legal actions for an agent
        agentIndex=0 means Pacman, ghosts are >= 1

        gameState.generateSuccessor(agentIndex, action):
        Returns the successor game state after an agent takes an action

        gameState.getNumAgents():
        Returns the total number of agents in the game

        gameState.isWin():
        Returns whether or not the game state is a winning state

        gameState.isLose():
        Returns whether or not the game state is a losing state
        """
        "*** YOUR CODE HERE ***"
        def maxValue(gameState, depth, agentIndex):
            if gameState.isWin() or gameState.isLose() or depth == 0:
                return self.evaluationFunction(gameState)
            value = float('-inf')
            legalActions = gameState.getLegalActions(agentIndex)
            for action in legalActions:
                value = max(value, minValue(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1))
            return value

        def minValue(gameState, depth, agentIndex):
            if gameState.isWin() or gameState.isLose() or depth == 0:
                return self.evaluationFunction(gameState)
            value = float("inf")
            legalActions = gameState.getLegalActions(agentIndex)
            for action in legalActions:
                if agentIndex == gameState.getNumAgents() - 1:
                    value = min(value, maxValue(gameState.generateSuccessor(agentIndex, action), depth - 1, 0))
                else:
                    value = min(value, minValue(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1))
            return value

        legalActions = gameState.getLegalActions(0)
        values = [minValue(gameState.generateSuccessor(0, action), self.depth, 1) for action in legalActions]
        return legalActions[values.index(max(values))]

class AlphaBetaAgent(MultiAgentSearchAgent):
    """
    Your minimax agent with alpha-beta pruning (question 3)
    """

    def getAction(self, gameState):
        """
        Returns the minimax action using self.depth and self.evaluationFunction
        """
        "*** YOUR CODE HERE ***"
        def maxValue(gameState, depth, agentIndex, alpha, beta):
            if gameState.isWin() or gameState.isLose() or depth == 0:
                return self.evaluationFunction(gameState)
            value = float('-inf')
            legalActions = gameState.getLegalActions(agentIndex)
            for action in legalActions:
                value = max(value, minValue(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1, alpha, beta))
                if value > beta:
                    return value
                alpha = max(alpha, value)
            return value

        def minValue(gameState, depth, agentIndex, alpha, beta):
            if gameState.isWin() or gameState.isLose() or depth == 0:
                return self.evaluationFunction(gameState)
            value = float("inf")
            legalActions = gameState.getLegalActions(agentIndex)
            for action in legalActions:
                if agentIndex == gameState.getNumAgents() - 1:
                    value = min(value, maxValue(gameState.generateSuccessor(agentIndex, action), depth - 1, 0, alpha, beta))
                else:
                    value = min(value, minValue(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1, alpha, beta))
                if value < alpha:
                    return value
                beta = min(beta, value)
            return value

        alpha = float('-inf')
        beta = float('inf')
        legalActions = gameState.getLegalActions(0)
        currValue = float('-inf')
        bestAction = legalActions[0]
        for action in legalActions:
            newValue = minValue(gameState.generateSuccessor(0, action), self.depth, 1, alpha, beta)
            if newValue > currValue:
                bestAction = action
                currValue = newValue
            alpha = max(alpha, currValue)
        return bestAction

class ExpectimaxAgent(MultiAgentSearchAgent):
    """
      Your expectimax agent (question 4)
    """

    def getAction(self, gameState):
        """
        Returns the expectimax action using self.depth and self.evaluationFunction

        All ghosts should be modeled as choosing uniformly at random from their
        legal moves.
        """
        "*** YOUR CODE HERE ***"
        def expectedValue(gameState, depth, agentIndex):
            if gameState.isWin() or gameState.isLose() or depth == 0:
                return self.evaluationFunction(gameState)
            value = float('-inf')
            expValue = 0
            legalActions = gameState.getLegalActions(agentIndex)
            if agentIndex == 0:
                for action in legalActions:
                    value = max(value, expectedValue(gameState.generateSuccessor(0, action), depth, agentIndex + 1))
            else:
                for action in legalActions:
                    if agentIndex == gameState.getNumAgents() - 1:
                        expValue += expectedValue(gameState.generateSuccessor(agentIndex, action), depth - 1, 0)
                    else:
                        expValue += expectedValue(gameState.generateSuccessor(agentIndex, action), depth, agentIndex + 1)
                value = expValue/len(legalActions)
            return value

        legalActions = gameState.getLegalActions(0)
        values = [expectedValue(gameState.generateSuccessor(0, action), self.depth, 1) for action in legalActions]
        return legalActions[values.index(max(values))]


def betterEvaluationFunction(currentGameState):
    """
    Your extreme ghost-hunting, pellet-nabbing, food-gobbling, unstoppable
    evaluation function (question 5).

    DESCRIPTION: <write something here so we know what you did>
    """
    "*** YOUR CODE HERE ***"
    pacPos = currentGameState.getPacmanPosition()
    foodList = currentGameState.getFood().asList()
    ghostStates = currentGameState.getGhostStates()
    scaredTimes = [ghost.scaredTimer for ghost in ghostStates]

    if currentGameState.isWin():
        return float('inf')
    elif currentGameState.isLose():
        return float('-inf')

    foodDistance = [manhattanDistance(pacPos, food) for food in foodList]
    ghostDistance = [manhattanDistance(pacPos, ghost.getPosition()) for ghost in ghostStates]
    for i in range(len(ghostStates)):
        ghostDistance[i] += scaredTimes[i]
    foodValue = 10/min(foodDistance)
    ghostValue = 1/min(ghostDistance) if min(ghostDistance) > 5 else 50/min(ghostDistance)
    return foodValue - ghostValue + currentGameState.getScore()

# Abbreviation
better = betterEvaluationFunction
