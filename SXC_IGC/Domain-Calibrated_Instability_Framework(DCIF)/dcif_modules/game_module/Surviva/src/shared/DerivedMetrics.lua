local DerivedMetrics = {}
DerivedMetrics.__index = DerivedMetrics

function DerivedMetrics.new(playerState)
    local self = setmetatable({}, DerivedMetrics)
    self.playerState = playerState
    return self
end

function DerivedMetrics:GetIdentityDrift()
    local p = self.playerState.PredictionField:getGlobalPredictability() or 0
    local m = self.playerState.MemoryField:getAverageMemory() or 0
    return (p + m) / 2
end

function DerivedMetrics:GetThreatLevel()
    return self.playerState.TensionEngine:getTension()
end

function DerivedMetrics:GetCommitmentScore()
    -- simple velocity-based commit score if available
    if self.playerState.Runtime and self.playerState.Runtime.VelocityHistory then
        local sum = 0
        for _, v in ipairs(self.playerState.Runtime.VelocityHistory) do
            sum = sum + v.Magnitude
        end
        local avg = (#self.playerState.Runtime.VelocityHistory > 0) and (sum / #self.playerState.Runtime.VelocityHistory) or 0
        return avg
    end
    return 0
end

function DerivedMetrics:GetBehaviorEntropy()
    -- placeholder: count distinct actions over recent window
    local actions = self.playerState.Runtime and self.playerState.Runtime.RecentActions or {}
    local seen = {}
    for _, a in ipairs(actions) do seen[a] = true end
    local distinct = 0
    for _ in pairs(seen) do distinct = distinct + 1 end
    return distinct
end

return DerivedMetrics
