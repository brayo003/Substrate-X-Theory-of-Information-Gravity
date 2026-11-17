-- BookController.server.lua
-- Handles: threshold checking, entry unlocking, parameter modifiers, mislearning, predictions

local BookController = {}
BookController.__index = BookController

-- Entry definitions
local ENTRIES = {
    -- Observational (safe, no effect)
    {
        id = "memory_first",
        type = "observational",
        trigger = function(s) return s.M > 0.6 end,
        text = "You remember this place. The world remembers with you.",
        effect = nil,
        unlocked = false
    },
    {
        id = "belief_first",
        type = "observational",
        trigger = function(s) return s.P > 0.7 and s.stalkerNearby end,
        text = "Your belief becomes real.",
        effect = nil,
        unlocked = false
    },
    {
        id = "identity_first",
        type = "observational",
        trigger = function(s) return s.I > 0.7 end,
        text = "You move like it.",
        effect = nil,
        unlocked = false
    },
    {
        id = "sanctuary_first",
        type = "observational",
        trigger = function(s) return s.T > 1.2 and s.inSanctuary end,
        text = "It remembers where you hide.",
        effect = nil,
        unlocked = false
    },
    
    -- Interpretive (modify parameters)
    {
        id = "memory_growth",
        type = "interpretive",
        trigger = function(s) return s.M > 0.8 end,
        text = "The forest remembers your steps.",
        effect = function(params) params.memoryGrowthMultiplier = (params.memoryGrowthMultiplier or 1) * 1.1 end,
        unlocked = false
    },
    {
        id = "prediction_strength",
        type = "interpretive",
        trigger = function(s) return s.P > 0.8 and s.stalkerNearby end,
        text = "Your belief shapes reality.",
        effect = function(params) params.predictionMultiplier = (params.predictionMultiplier or 1) * 1.1 end,
        unlocked = false
    },
    {
        id = "sanctuary_decay",
        type = "interpretive",
        trigger = function(s) return s.T > 1.2 and s.inSanctuary end,
        text = "The sanctuary remembers your fear.",
        effect = function(params) params.sanctuaryDecayRate = (params.sanctuaryDecayRate or 0.95) * 0.95 end,
        unlocked = false
    },
    
    -- Prescriptive (hard effects)
    {
        id = "path_punishment",
        type = "prescriptive",
        trigger = function(s) return s.revisitedHighMZone end,
        text = "Walk where you have not.",
        effect = function(engine, player) engine.T_sys = engine.T_sys + 0.05 end,
        unlocked = false
    }
}

-- Mutation table (mislearning)
local MUTATIONS = {
    {
        original = "Walk where you have not.",
        mutated = "Walk where you remember.",
        condition = function(s) return s.T > 1.0 end
    },
    {
        original = "It expects you where you expect it.",
        mutated = "It expects you where you last saw it.",
        condition = function(s) return s.T > 1.0 end
    },
    {
        original = "Your fear feeds the night.",
        mutated = "Your fear feeds it. The night does not care.",
        condition = function(s) return s.T > 1.2 end
    }
}

function BookController.new(player, playerState)
    local self = setmetatable({}, BookController)
    self.Player = player
    -- Authoritative playerState contains the TensionEngine, MemoryField, PredictionField, etc.
    self.PlayerState = playerState
    self.TensionSystem = playerState and playerState.TensionEngine
    self.UnlockedEntries = {}
    self.Params = {
        memoryGrowthMultiplier = 1,
        predictionMultiplier = 1,
        sanctuaryDecayRate = 0.95
    }
    self.LastCheck = tick()
    self.CheckInterval = 10  -- seconds
    self.PredictionActive = false
    return self
end

function BookController:CalculateIdentityDrift()
    -- I_player = similarity between player movement and stalker model
    -- For now, approximate using P_sys and repetition rate
    local ts = self.TensionSystem
    if not ts then return 0 end
    local p = ts:getPredictability()
    local m = ts:getAverageMemory()
    return (p + m) / 2
end

function BookController:GetPlayerState(stalkerNearby, inSanctuary, revisitedHighMZone)
    local ts = self.TensionSystem
    if not ts then
        return {
            T = 0, M = 0, P = 0, I = 0,
            stalkerNearby = stalkerNearby,
            inSanctuary = inSanctuary,
            revisitedHighMZone = revisitedHighMZone
        }
    end
    return {
        T = ts:getTension(),
        M = ts:getAverageMemory(),
        P = ts:getPredictability(),
        I = self:CalculateIdentityDrift(),
        stalkerNearby = stalkerNearby,
        inSanctuary = inSanctuary,
        revisitedHighMZone = revisitedHighMZone
    }
end

function BookController:GetEntryText(entry, state)
    for _, mutation in ipairs(MUTATIONS) do
        if mutation.original == entry.text and mutation.condition(state) then
            return mutation.mutated
        end
    end
    return entry.text
end

function BookController:UnlockEntry(entry, state)
    if entry.unlocked then return false end
    entry.unlocked = true
    table.insert(self.UnlockedEntries, entry.id)
    
    -- Apply effect if interpretive or prescriptive
    if entry.effect then
        if entry.type == "interpretive" then
            entry.effect(self.Params)
        elseif entry.type == "prescriptive" then
            entry.effect(self.TensionSystem, self.Player)
        end
    end
    
    -- Send to client
    local remote = game:GetService("ReplicatedStorage"):FindFirstChild("V12_Sync")
    if remote then
        local displayText = self:GetEntryText(entry, state)
        remote:FireClient(self.Player, "book_entry", displayText, entry.type)
    end
    
    print("[Book] Unlocked:", entry.id, "for", self.Player.Name)
    return true
end

function BookController:CheckThresholds(state)
    for _, entry in ipairs(ENTRIES) do
        if not entry.unlocked and entry.trigger(state) then
            self:UnlockEntry(entry, state)
        end
    end
end

function BookController:PredictMovement(playerIntent)
    local I = self:CalculateIdentityDrift()
    if I < 0.7 then return end
    
    local prediction = nil
    if playerIntent.direction == "toward_highM" then
        prediction = "You will go there."
    elseif playerIntent.stalkerNearby then
        prediction = "You will run."
    end
    
    if prediction then
        local remote = game:GetService("ReplicatedStorage"):FindFirstChild("V12_Sync")
        if remote then
            remote:FireClient(self.Player, "book_prediction", prediction)
        end
        self.PredictionActive = true
        self.LastPrediction = prediction
        self.LastPredictionTime = tick()
    end
end

function BookController:CheckPredictionOutcome(playerObeyed)
    if not self.PredictionActive then return end
    
    if playerObeyed then
        -- Increase I_player
        -- Implementation: track in DataStore
        print("[Book] Player obeyed prediction")
    else
        -- T_sys spike
        self.TensionSystem.T_sys = self.TensionSystem.T_sys + 0.1
        print("[Book] Player resisted prediction - T_sys spike")
    end
    
    self.PredictionActive = false
end

function BookController:Update(stalkerNearby, inSanctuary, revisitedHighMZone)
    local now = tick()
    if now - self.LastCheck >= self.CheckInterval then
        self.LastCheck = now
        local state = self:GetPlayerState(stalkerNearby, inSanctuary, revisitedHighMZone)
        self:CheckThresholds(state)
    end
end

function BookController:GetUnlockedEntries()
    return self.UnlockedEntries
end

function BookController:GetParams()
    return self.Params
end

return BookController
