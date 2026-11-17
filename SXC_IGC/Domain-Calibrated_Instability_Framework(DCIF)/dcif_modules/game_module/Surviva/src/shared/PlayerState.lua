local ReplicatedStorage = game:GetService("ReplicatedStorage")

local Shared = ReplicatedStorage:WaitForChild("Shared")
local TensionEngine = require(Shared:WaitForChild("TensionEngine"))
local MemoryField = require(Shared:WaitForChild("MemoryField"))
local PredictionFieldModule = require(script.Parent.server and script.Parent.server.PredictionField or script.Parent.PredictionField)

local PlayerState = {}
PlayerState.__index = PlayerState

function PlayerState.new(player)
    local self = setmetatable({}, PlayerState)
    self.Player = player
    -- single ownership of subsystems per player
    self.MemoryField = MemoryField.new()
    -- provide MemoryField to PredictionField so PredictionField may read M for a weak one-way coupling
    self.PredictionField = PredictionFieldModule.new(self.MemoryField)
    self.TensionEngine = TensionEngine.new()

    self.ArtifactState = {Collected = {}}
    self.BookState = {Unlocked = {}}
    self.SanctuaryState = {InSanctuary = false}

    self.Metrics = {
        Tension = 0,
        Predictability = 0,
        AverageMemory = 0,
        IdentityDrift = 0
    }

    self.Runtime = {
        InSanctuary = false,
        StalkerNearby = false,
        LastPosition = nil,
        EventStress = 0,
        VelocityHistory = {},
        RecentActions = {}
    }

    return self
end

function PlayerState:getPlayer()
    return self.Player
end

function PlayerState:destroy()
    -- if subsystems need explicit cleanup, call them (best-effort)
    if self.MemoryField and self.MemoryField.destroy then pcall(self.MemoryField.destroy, self.MemoryField) end
    if self.PredictionField and self.PredictionField.destroy then pcall(self.PredictionField.destroy, self.PredictionField) end
    if self.TensionEngine and self.TensionEngine.reset then pcall(self.TensionEngine.reset, self.TensionEngine) end
end

return PlayerState
