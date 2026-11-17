local ConsequenceModel = {}
ConsequenceModel.__index = ConsequenceModel

function ConsequenceModel.new(playerState)
    local self = setmetatable({}, ConsequenceModel)
    self.playerState = playerState
    return self
end

-- Example probability functions; deterministic but tunable
function ConsequenceModel:DoorLockProbability()
    local P = self.playerState.PredictionField:getGlobalPredictability() or 0
    return math.clamp(0.1 + 0.8 * P, 0, 1)
end

function ConsequenceModel:WallShiftProbability()
    local T = self.playerState.TensionEngine:getTension() or 0
    local P = self.playerState.PredictionField:getGlobalPredictability() or 0
    local score = 0.05 + 0.6 * T + 0.35 * P
    return math.clamp(score, 0, 1)
end

function ConsequenceModel:SanctuaryBreachProbability()
    local T = self.playerState.TensionEngine:getTension() or 0
    local P = self.playerState.PredictionField:getGlobalPredictability() or 0
    local M = self.playerState.MemoryField:getAverageMemory() or 0
    local score = 0.02 + 0.5 * T + 0.3 * P + 0.2 * M
    return math.clamp(score, 0, 1)
end

return ConsequenceModel
