local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local EventBus = require(script.Parent.Parent.shared.EventBus)
local PlayerState = require(script.Parent.Parent.shared.PlayerState)
local DerivedMetrics = require(script.Parent.Parent.shared.DerivedMetrics)
local ConsequenceModel = require(script.Parent.Parent.shared.ConsequenceModel)

local SystemManager = {}
SystemManager.__index = SystemManager

local PlayerStates = {}

function SystemManager.init()
    if SystemManager._initialized then return end
    SystemManager._initialized = true
    SystemManager.Bus = EventBus.new()
    PlayerStates = {}

    -- Wire player events
    Players.PlayerAdded:Connect(function(p) SystemManager:onPlayerAdded(p) end)
    Players.PlayerRemoving:Connect(function(p) SystemManager:onPlayerRemoving(p) end)

    -- create existing players
    for _, p in ipairs(Players:GetPlayers()) do
        SystemManager:onPlayerAdded(p)
    end

    -- Start update loop
    SystemManager._conn = RunService.Heartbeat:Connect(function(dt) SystemManager:update(dt) end)
end

function SystemManager:onPlayerAdded(player)
    -- create authoritative player state
    local ps = PlayerState.new(player)
    ps.Derived = DerivedMetrics.new(ps)
    ps.Consequences = ConsequenceModel.new(ps)
    PlayerStates[player.UserId] = ps
    SystemManager.Bus:emit("PlayerStateCreated", ps)
end

function SystemManager:onPlayerRemoving(player)
    local ps = PlayerStates[player.UserId]
    if ps then
        SystemManager.Bus:emit("PlayerStateDestroy", ps)
        ps:destroy()
        PlayerStates[player.UserId] = nil
    end
end

function SystemManager:getPlayerState(player)
    return PlayerStates[player.UserId]
end

function SystemManager:update(dt)
    -- update order per pipeline
    -- 1. collect inputs from runtime buffer (player-signal handled elsewhere)
    -- 2. Update Memory (call MemoryField step/update if exists)
    for _, ps in pairs(PlayerStates) do
        if ps.MemoryField and ps.MemoryField.update then pcall(ps.MemoryField.update, ps.MemoryField, dt) end
    end
    -- 3. Update Prediction
    for _, ps in pairs(PlayerStates) do
        if ps.PredictionField and ps.PredictionField.update then pcall(ps.PredictionField.update, ps.PredictionField, dt) end
    end
    -- 4. Update Tension
    for _, ps in pairs(PlayerStates) do
        if ps.TensionEngine and ps.TensionEngine.step then
            local signal = (ps.Runtime and ps.Runtime.EventStress) or 0
            local ok, ruptured = pcall(ps.TensionEngine.step, ps.TensionEngine, signal)
            ps.Metrics.Tension = ps.TensionEngine:getTension()
            if ok and ruptured then
                SystemManager.Bus:emit("RuptureOccurred", ps)
            end
        end
    end
    -- 5. Compute Derived Metrics
    for _, ps in pairs(PlayerStates) do
        ps.Metrics.IdentityDrift = ps.Derived:GetIdentityDrift()
        ps.Metrics.Predictability = ps.PredictionField and ps.PredictionField:getGlobalPredictability() or 0
        ps.Metrics.AverageMemory = ps.MemoryField and ps.MemoryField:getAverageMemory() or 0
    end
    -- 6. Evaluate Consequences (emit events if thresholds crossed)
    for _, ps in pairs(PlayerStates) do
        local breachProb = ps.Consequences:SanctuaryBreachProbability()
        if breachProb > 0.9 then
            SystemManager.Bus:emit("SanctuaryBreachImminent", ps)
        end
    end
    -- 7. Dispatch metric change events
    for _, ps in pairs(PlayerStates) do
        SystemManager.Bus:emit("TensionChanged", ps, ps.Metrics.Tension)
        SystemManager.Bus:emit("PredictionChanged", ps, ps.Metrics.Predictability)
        SystemManager.Bus:emit("MemoryChanged", ps, ps.Metrics.AverageMemory)
    end
    -- 8. Sync clients is up to controllers via EventBus
end

function SystemManager.destroy()
    if SystemManager._conn then SystemManager._conn:Disconnect() SystemManager._conn = nil end
    for _, ps in pairs(PlayerStates) do ps:destroy() end
    PlayerStates = {}
    SystemManager._initialized = false
end

return SystemManager
