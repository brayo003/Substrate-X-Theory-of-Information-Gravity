-- ArtifactManager.server.lua
-- Handles: ruin spawning, artifact pools, tier progression, artifact loss on rupture

local ArtifactManager = {}
ArtifactManager.__index = ArtifactManager

-- Artifact pools per tier
local ARTIFACT_POOLS = {
    Tier1 = {
        {id = "shattered_mirror", name = "Shattered Mirror", effect = "tension_drain", value = 0.3, lore = "She looked for herself. Found nothing."},
        {id = "burnt_journal", name = "Burnt Journal", effect = "reveal_prediction", value = nil, lore = "He wrote everything down. Burned it. Died anyway."},
        {id = "broken_compass", name = "Broken Compass", effect = "follow_memory", value = nil, lore = "A child who wanted to go home. Never found it."},
        {id = "empty_locket", name = "Empty Locket", effect = "temp_sanctuary", value = nil, lore = "A parent who forgot their child's face. The Substrate remembers."},
        {id = "fractured_crown", name = "Fractured Crown", effect = "tension_inject", value = 0.2, lore = "The one who built it. The first to fall."}
    },
    Tier2 = {
        {id = "weeping_stone", name = "Weeping Stone", effect = "slow_stalker", value = nil, lore = "Tears that never dry."},
        {id = "caged_heart", name = "Caged Heart", effect = "absorb_rupture", value = nil, lore = "A heart that beat for too long."},
        {id = "silent_bell", name = "Silent Bell", effect = "silence_false_audio", value = 30, lore = "It rings, but no one hears."},
        {id = "twisted_key", name = "Twisted Key", effect = "unlock_doors", value = nil, lore = "It opens what should stay closed."},
        {id = "forgotten_idol", name = "Forgotten Idol", effect = "reveal_ruins", value = nil, lore = "They prayed. No one answered."}
    }
    -- Add Tier3, Tier4, Tier5 as needed
}

local TIER_THRESHOLDS = {
    Tier1 = 0,      -- M >= 0
    Tier2 = 30,     -- M >= 30
    Tier3 = 40,     -- M >= 40
    Tier4 = 50,     -- M >= 50
    Tier5 = 60      -- M >= 60
}

function ArtifactManager.new(playerState, player)
    local self = setmetatable({}, ArtifactManager)
    self.PlayerState = playerState
    self.TensionSystem = playerState and playerState.TensionEngine
    self.Player = player
    self.CollectedArtifacts = {}  -- {id = true}
    self.ActiveArtifacts = {}     -- currently held/equipped
    self.Ruins = {}               -- spawned ruin locations
    self.LastMSpawnCheck = 0
    return self
end

function ArtifactManager:GetCurrentTier()
    local ts = self.TensionSystem
    if not ts then return "Tier1" end
    local m = ts:getAverageMemory() * 100  -- convert to 0-100 scale
    if m >= TIER_THRESHOLDS.Tier5 then return "Tier5"
    elseif m >= TIER_THRESHOLDS.Tier4 then return "Tier4"
    elseif m >= TIER_THRESHOLDS.Tier3 then return "Tier3"
    elseif m >= TIER_THRESHOLDS.Tier2 then return "Tier2"
    else return "Tier1" end
end

function ArtifactManager:GetAvailableArtifacts()
    local tier = self:GetCurrentTier()
    local pool = ARTIFACT_POOLS[tier] or ARTIFACT_POOLS.Tier1
    local available = {}
    for _, artifact in ipairs(pool) do
        if not self.CollectedArtifacts[artifact.id] then
            table.insert(available, artifact)
        end
    end
    return available
end

function ArtifactManager:SpawnRuins()
    -- Clear old ruins
    for _, ruin in ipairs(self.Ruins) do
        if ruin and ruin.Parent then
            ruin:Destroy()
        end
    end
    self.Ruins = {}
    
    local tier = self:GetCurrentTier()
    local numRuins = (tier == "Tier1" and 1) or (tier == "Tier2" and 2) or (tier == "Tier3" and 3) or (tier == "Tier4" and 4) or 5
    
    -- Spawn ruins at random positions within map bounds (adjust as needed)
    for i = 1, numRuins do
        local ruin = Instance.new("Part")
        ruin.Name = "Ruin_" .. tier .. "_" .. i
        ruin.Size = Vector3.new(10, 5, 10)
        ruin.BrickColor = BrickColor.new("Dark grey")
        ruin.Material = Enum.Material.Slate
        ruin.Anchored = true
        ruin.CanCollide = true
        ruin:SetAttribute("RuinTier", tier)
        ruin:SetAttribute("ArtifactCollected", false)
        
        -- Random position within 500-2000 studs from spawn
        local angle = math.random() * 2 * math.pi
        local distance = math.random(500, 2000)
        ruin.Position = Vector3.new(math.cos(angle) * distance, 0, math.sin(angle) * distance)
        ruin.Parent = workspace
        
        table.insert(self.Ruins, ruin)
        
        -- Add glow effect to indicate artifact available
        local glow = Instance.new("PointLight", ruin)
        glow.Color = Color3.new(1, 0.5, 0)
        glow.Range = 15
        glow.Brightness = 2
    end
    
    print("[ArtifactManager] Spawned", numRuins, "ruins for tier", tier)
end

function ArtifactManager:TryCollectArtifact(ruin)
    local tier = ruin:GetAttribute("RuinTier")
    if ruin:GetAttribute("ArtifactCollected") then return false end
    
    local available = self:GetAvailableArtifacts()
    if #available == 0 then
        print("[ArtifactManager] No available artifacts in this tier")
        return false
    end
    
    -- Randomly select an artifact from available pool
    local artifact = available[math.random(1, #available)]
    self.CollectedArtifacts[artifact.id] = true
    ruin:SetAttribute("ArtifactCollected", true)
    
    -- Apply artifact effect
    self:ApplyArtifactEffect(artifact)
    
    -- Remove glow
    local glow = ruin:FindFirstChild("PointLight")
    if glow then glow:Destroy() end
    
    -- Send to client
    local remote = game:GetService("ReplicatedStorage"):FindFirstChild("V12_Sync")
    if remote then
        remote:FireClient(self.Player, "artifact_collected", artifact.name, artifact.lore)
    end
    
    print("[ArtifactManager]", self.Player.Name, "collected", artifact.name)
    return true
end

function ArtifactManager:ApplyArtifactEffect(artifact)
    if artifact.effect == "tension_drain" then
        self.TensionSystem:addArtifactTension(-artifact.value)
    elseif artifact.effect == "tension_inject" then
        self.TensionSystem:addArtifactTension(artifact.value)
    elseif artifact.effect == "slow_stalker" then
        -- Will be implemented when stalker AI is enhanced
        print("[Artifact] Slow stalker effect applied")
    elseif artifact.effect == "absorb_rupture" then
        -- Will be implemented
        print("[Artifact] Rupture absorption effect applied")
    elseif artifact.effect == "silence_false_audio" then
        -- Will be implemented
        print("[Artifact] False audio silenced for", artifact.value, "seconds")
    elseif artifact.effect == "unlock_doors" then
        -- Will be implemented
        print("[Artifact] Door unlock effect applied")
    elseif artifact.effect == "reveal_ruins" then
        -- Will be implemented
        print("[Artifact] Ruin reveal effect applied")
    elseif artifact.effect == "reveal_prediction" then
        -- Will be implemented
        print("[Artifact] Prediction reveal effect applied")
    elseif artifact.effect == "follow_memory" then
        -- Will be implemented
        print("[Artifact] Memory following effect applied")
    elseif artifact.effect == "temp_sanctuary" then
        -- Will be implemented
        print("[Artifact] Temporary sanctuary effect applied")
    end
end

function ArtifactManager:OnRupture()
    -- Remove a random artifact on rupture (optional)
    local collected = {}
    for id, _ in pairs(self.CollectedArtifacts) do
        table.insert(collected, id)
    end
    if #collected > 0 then
        local lostArtifact = collected[math.random(1, #collected)]
        self.CollectedArtifacts[lostArtifact] = nil
        print("[ArtifactManager]", self.Player.Name, "lost artifact on rupture:", lostArtifact)
        
        local remote = game:GetService("ReplicatedStorage"):FindFirstChild("V12_Sync")
        if remote then
            remote:FireClient(self.Player, "artifact_lost", lostArtifact)
        end
    end
end

function ArtifactManager:Update()
    local m = self.TensionSystem:getAverageMemory() * 100
    if m >= TIER_THRESHOLDS.Tier2 and self.LastMSpawnCheck == 0 then
        self.LastMSpawnCheck = m
        self:SpawnRuins()
    elseif m >= TIER_THRESHOLDS.Tier3 and self.LastMSpawnCheck < TIER_THRESHOLDS.Tier3 then
        self.LastMSpawnCheck = m
        self:SpawnRuins()
    elseif m >= TIER_THRESHOLDS.Tier4 and self.LastMSpawnCheck < TIER_THRESHOLDS.Tier4 then
        self.LastMSpawnCheck = m
        self:SpawnRuins()
    elseif m >= TIER_THRESHOLDS.Tier5 and self.LastMSpawnCheck < TIER_THRESHOLDS.Tier5 then
        self.LastMSpawnCheck = m
        self:SpawnRuins()
    end
end

function ArtifactManager:GetCollectedCount()
    local count = 0
    for _ in pairs(self.CollectedArtifacts) do count = count + 1 end
    return count
end

return ArtifactManager
