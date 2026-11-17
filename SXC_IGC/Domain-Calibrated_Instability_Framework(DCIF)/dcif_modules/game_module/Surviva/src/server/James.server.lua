local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Shared = ReplicatedStorage:WaitForChild("Shared")

local TensionEngine = require(Shared:WaitForChild("TensionEngine"))
local SystemManager = require(script.Parent.SystemManager)
SystemManager.init()

local remote = ReplicatedStorage:FindFirstChild("V12_Sync") or Instance.new("RemoteEvent")
remote.Name = "V12_Sync"
remote.Parent = ReplicatedStorage

local playerSignal = ReplicatedStorage:FindFirstChild("PlayerSignal") or Instance.new("RemoteEvent")
print("V12 HORIZON ENGINE ONLINE")
print("System bootstrap: initializing controllers")

local Phase1 = require(script.Parent.Phase1Controller)
local Phase2 = require(script.Parent.Phase2Controller)

Phase1.init()
Phase2.init()

print("SystemManager and Phase controllers initialized")
function BookController:GetPlayerState(stalkerNearby, inSanctuary, revisitedHighMZone)
    return {
        T = self.TensionSystem:getTension(),
        M = self.TensionSystem:getAverageMemory(),
        P = self.TensionSystem:getPredictability(),
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
    if entry.effect then
        if entry.type == "interpretive" then
            entry.effect(self.Params)
        elseif entry.type == "prescriptive" then
            entry.effect(self.TensionSystem, self.Player)
        end
    end
    local displayText = self:GetEntryText(entry, state)
    remote:FireClient(self.Player, "book_entry", displayText, entry.type)
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
        remote:FireClient(self.Player, "book_prediction", prediction)
        self.PredictionActive = true
        self.LastPrediction = prediction
        self.LastPredictionTime = tick()
    end
end

function BookController:CheckPredictionOutcome(playerObeyed)
    if not self.PredictionActive then return end
    if playerObeyed then
        print("[Book] Player obeyed prediction")
    else
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

-- =========================
-- ARTIFACT MANAGER
-- =========================
local ArtifactManager = {}
ArtifactManager.__index = ArtifactManager

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
}

local TIER_THRESHOLDS = {Tier1 = 0, Tier2 = 30, Tier3 = 40, Tier4 = 50, Tier5 = 60}

function ArtifactManager.new(tensionSystem, player)
    local self = setmetatable({}, ArtifactManager)
    self.TensionSystem = tensionSystem
    self.Player = player
    self.CollectedArtifacts = {}
    self.ActiveArtifacts = {}
    self.Ruins = {}
    self.LastMSpawnCheck = 0
    return self
end

function ArtifactManager:GetCurrentTier()
    local m = self.TensionSystem:getAverageMemory() * 100
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
    for _, ruin in ipairs(self.Ruins) do
        if ruin and ruin.Parent then ruin:Destroy() end
    end
    self.Ruins = {}
    local tier = self:GetCurrentTier()
    local numRuins = (tier == "Tier1" and 1) or (tier == "Tier2" and 2) or (tier == "Tier3" and 3) or (tier == "Tier4" and 4) or 5
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
        local angle = math.random() * 2 * math.pi
        local distance = math.random(500, 2000)
        ruin.Position = Vector3.new(math.cos(angle) * distance, 0, math.sin(angle) * distance)
        ruin.Parent = workspace
        local glow = Instance.new("PointLight", ruin)
        glow.Color = Color3.new(1, 0.5, 0)
        glow.Range = 15
        glow.Brightness = 2
        table.insert(self.Ruins, ruin)
    end
    print("[ArtifactManager] Spawned", numRuins, "ruins for tier", tier)
end

function ArtifactManager:TryCollectArtifact(ruin)
    local tier = ruin:GetAttribute("RuinTier")
    if ruin:GetAttribute("ArtifactCollected") then return false end
    local available = self:GetAvailableArtifacts()
    if #available == 0 then return false end
    local artifact = available[math.random(1, #available)]
    self.CollectedArtifacts[artifact.id] = true
    ruin:SetAttribute("ArtifactCollected", true)
    if artifact.effect == "tension_drain" then
        self.TensionSystem:addArtifactTension(-artifact.value)
    elseif artifact.effect == "tension_inject" then
        self.TensionSystem:addArtifactTension(artifact.value)
    elseif artifact.effect == "slow_stalker" then
        print("[Artifact] Slow stalker effect applied")
    elseif artifact.effect == "absorb_rupture" then
        print("[Artifact] Rupture absorption effect applied")
    elseif artifact.effect == "silence_false_audio" then
        print("[Artifact] False audio silenced for", artifact.value, "seconds")
    elseif artifact.effect == "unlock_doors" then
        print("[Artifact] Door unlock effect applied")
    elseif artifact.effect == "reveal_ruins" then
        print("[Artifact] Ruin reveal effect applied")
    elseif artifact.effect == "reveal_prediction" then
        print("[Artifact] Prediction reveal effect applied")
    elseif artifact.effect == "follow_memory" then
        print("[Artifact] Memory following effect applied")
    elseif artifact.effect == "temp_sanctuary" then
        print("[Artifact] Temporary sanctuary effect applied")
    end
    local glow = ruin:FindFirstChild("PointLight")
    if glow then glow:Destroy() end
    remote:FireClient(self.Player, "artifact_collected", artifact.name, artifact.lore)
    print("[ArtifactManager]", self.Player.Name, "collected", artifact.name)
    return true
end

function ArtifactManager:OnRupture()
    local collected = {}
    for id, _ in pairs(self.CollectedArtifacts) do table.insert(collected, id) end
    if #collected > 0 then
        local lostArtifact = collected[math.random(1, #collected)]
        self.CollectedArtifacts[lostArtifact] = nil
        print("[ArtifactManager]", self.Player.Name, "lost artifact on rupture:", lostArtifact)
        remote:FireClient(self.Player, "artifact_lost", lostArtifact)
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

-- =========================
-- SXC LOCAL DRIFT (Temporal Noise)
-- =========================
local x_noise = 0.0
local r_param, a_param, b_param = 0.153267, 1.0, 1.0
local dt_fixed = 0.05
local sigma_param = 0.01

local function sxc_step(val)
    local noise = (math.random() * 2 - 1) * sigma_param
    local drift = r_param * val + a_param * val^2 - b_param * val^3
    return val + dt_fixed * drift + noise
end

-- =========================
-- EVENT STRESS TRACKING
-- =========================
local eventStressAccumulator = 0
local eventStressDecay = 0.95

function AddHuntingStress()
    eventStressAccumulator = eventStressAccumulator + 0.3
end

function AddGatheringStress()
    eventStressAccumulator = eventStressAccumulator + 0.15
end

function AddArtifactStress()
    eventStressAccumulator = eventStressAccumulator + 0.8
end

-- =========================
-- CLIENT SIGNAL HANDLER (V12 Protocol integration)
-- =========================
local clientSignalBuffer = {}
local BUFFER_SIZE = 10

playerSignal.OnServerEvent:Connect(function(player, signal)
    local validSignal = math.clamp(signal or 0, 0, 2)
    if not clientSignalBuffer[player] then
        clientSignalBuffer[player] = {}
    end
    local buffer = clientSignalBuffer[player]
    table.insert(buffer, validSignal)
    if #buffer > BUFFER_SIZE then
        table.remove(buffer, 1)
    end
    local avgSignal = 0
    for _, s in ipairs(buffer) do
        avgSignal = avgSignal + s
    end
    avgSignal = avgSignal / #buffer
    _G.ClientSignal[player] = avgSignal
end)

_G.ClientSignal = {}

-- =========================
-- SANCTUARY ZONE DETECTION
-- =========================
local inSanctuary = {}
local sanctuaryParts = {}

for _, part in ipairs(workspace:GetDescendants()) do
    if part:IsA("BasePart") and part:GetAttribute("Sanctuary") then
        table.insert(sanctuaryParts, part)
    end
end

local function isPlayerInSanctuary(player)
    local char = player.Character
    if not char then return false end
    local hrp = char:FindFirstChild("HumanoidRootPart")
    if not hrp then return false end
    for _, part in ipairs(sanctuaryParts) do
        if part:IsA("BasePart") and hrp.Position.Y > part.Position.Y - 5 and hrp.Position.Y < part.Position.Y + 10 then
            if math.abs(hrp.Position.X - part.Position.X) < part.Size.X/2 + 2 and
               math.abs(hrp.Position.Z - part.Position.Z) < part.Size.Z/2 + 2 then
                return true
            end
        end
    end
    return false
end

-- =========================
-- STILLNESS TRAP
-- =========================
local lastPosition = {}
local stillnessTimer = {}
local stillnessVisualTimer = {}
local wallsClosed = {}

-- =========================
-- TELEMETRY LOGGING
-- =========================
local telemetryTimer = 0

local function printTelemetry(T, M, P, velMag, signal, state, eventStress)
    local t_pct = math.floor(T * 100)
    local m_fmt = string.format("%.3f", M)
    local p_fmt = string.format("%.3f", P)
    local v_fmt = string.format("%.1f", velMag)
    local sig_fmt = string.format("%.3f", signal)
    local stress_fmt = string.format("%.2f", eventStress)
    print(string.format(
        "[V12 TELEMETRY] Tension: %d%% | State: %s | Signal: %s | Stress: %s || Vel: %s | M_Avg: %s | P_Sys: %s",
        t_pct, state, sig_fmt, stress_fmt, v_fmt, m_fmt, p_fmt
    ))
end

-- =========================
-- HIGH P CONSEQUENCES HELPER FUNCTIONS
-- =========================
local function playSoundAt(position, soundId, volume)
    local sound = Instance.new("Sound")
    sound.SoundId = soundId
    sound.Volume = volume or 0.5
    sound.Parent = position
    sound:Play()
    task.wait(0.5)
    sound:Destroy()
end

-- =========================
-- SHATTER SYSTEM
-- =========================
local ShatterController = {}
ShatterController.__index = ShatterController

local SHATTER_DURATION = 10
local TRAIL_DELAY = 2
local GRAB_DEGRADATION = 0.9

local function createShatterController(tensionSystem, stalker, player)
    local self = setmetatable({}, ShatterController)
    self.TensionSystem = tensionSystem
    self.Stalker = stalker
    self.Player = player
    self.Active = false
    self.TrailBuffer = {}
    self.BufferSize = TRAIL_DELAY / 0.05
    self.OriginalControls = nil
    self.InputConnection = nil
    self.RecordConnection = nil
    self.TrailConnection = nil
    return self
end

function ShatterController:ShouldTrigger()
    local tension = self.TensionSystem:getTension()
    local predictability = self.TensionSystem:getPredictability()
    return tension > 1.15 and predictability > 0.7 and not self.Active
end

function ShatterController:Activate()
    if self.Active then return end
    self.Active = true
    local character = self.Player.Character
    local humanoid = character and character:FindFirstChild("Humanoid")
    if humanoid then
        self.OriginalControls = humanoid.AutoRotate
        humanoid.AutoRotate = false
        humanoid.PlatformStand = true
    end
    self:SetupInputInversion()
    self:StartBodyTrailing()
    remote:FireClient(self.Player, "shatter_start")
    print("[Shatter] Activated for", self.Player.Name)
    task.wait(SHATTER_DURATION)
    self:Deactivate()
end

function ShatterController:SetupInputInversion()
    local UserInputService = game:GetService("UserInputService")
    self.InputConnection = UserInputService.InputBegan:Connect(function(input, gameProcessed)
        if gameProcessed or not self.Active then return end
        local moveDirection = nil
        if input.KeyCode == Enum.KeyCode.W then
            moveDirection = Vector3.new(0, 0, -1)
        elseif input.KeyCode == Enum.KeyCode.S then
            moveDirection = Vector3.new(0, 0, 1)
        elseif input.KeyCode == Enum.KeyCode.A then
            moveDirection = Vector3.new(-1, 0, 0)
        elseif input.KeyCode == Enum.KeyCode.D then
            moveDirection = Vector3.new(1, 0, 0)
        end
        if moveDirection and self.Stalker and self.Stalker.Parent then
            local stalkerHrp = self.Stalker:FindFirstChild("HumanoidRootPart")
            if stalkerHrp then
                local newPos = stalkerHrp.Position + (moveDirection * 5)
                stalkerHrp.CFrame = CFrame.new(newPos)
            end
        end
    end)
end

function ShatterController:StartBodyTrailing()
    local RunService = game:GetService("RunService")
    self.RecordConnection = RunService.Heartbeat:Connect(function()
        if not self.Active then return end
        local stalkerHrp = self.Stalker and self.Stalker:FindFirstChild("HumanoidRootPart")
        if stalkerHrp then
            table.insert(self.TrailBuffer, stalkerHrp.Position)
            if #self.TrailBuffer > self.BufferSize then
                table.remove(self.TrailBuffer, 1)
            end
        end
    end)
    self.TrailConnection = RunService.Heartbeat:Connect(function()
        if not self.Active then return end
        local character = self.Player.Character
        local hrp = character and character:FindFirstChild("HumanoidRootPart")
        if hrp and #self.TrailBuffer > 0 then
            local trailPos = self.TrailBuffer[1]
            if trailPos then
                hrp.CFrame = CFrame.new(trailPos)
            end
        end
    end)
end

function ShatterController:OnGrab()
    local character = self.Player.Character
    local humanoid = character and character:FindFirstChild("Humanoid")
    if humanoid then
        humanoid.WalkSpeed = humanoid.WalkSpeed * GRAB_DEGRADATION
    end
    remote:FireClient(self.Player, "the_grab")
    print("[Shatter] The Grab executed on", self.Player.Name)
end

function ShatterController:Deactivate()
    if not self.Active then return end
    self.Active = false
    local character = self.Player.Character
    local humanoid = character and character:FindFirstChild("Humanoid")
    if humanoid then
        humanoid.AutoRotate = self.OriginalControls ~= false
        humanoid.PlatformStand = false
    end
    if self.InputConnection then self.InputConnection:Disconnect() end
    if self.RecordConnection then self.RecordConnection:Disconnect() end
    if self.TrailConnection then self.TrailConnection:Disconnect() end
    remote:FireClient(self.Player, "shatter_end")
    print("[Shatter] Deactivated for", self.Player.Name)
end

function ShatterController:Update()
    if self:ShouldTrigger() then
        self:Activate()
    end
end

-- =========================
-- ANIMAL BEHAVIOR SYSTEM
-- =========================
local AnimalController = {}
AnimalController.__index = AnimalController

local ANIMAL_STATES = {NORMAL=0, OBSERVER=1, ENCIRCLEMENT=2, ALARM=3, NECROSIS=4}

local function createAnimalController(tensionSystem, player)
    local self = setmetatable({}, AnimalController)
    self.TensionSystem = tensionSystem
    self.Player = player
    self.Animals = {}
    self.CurrentState = ANIMAL_STATES.NORMAL
    self.EncirclementRadius = 30
    return self
end

function AnimalController:RegisterAnimal(animal)
    table.insert(self.Animals, animal)
end

function AnimalController:GetCurrentState()
    local tension = self.TensionSystem:getTension()
    if tension > 1.1 then return ANIMAL_STATES.NECROSIS
    elseif tension > 0.9 then return ANIMAL_STATES.ALARM
    elseif tension > 0.7 then return ANIMAL_STATES.ENCIRCLEMENT
    elseif tension > 0.4 then return ANIMAL_STATES.OBSERVER
    else return ANIMAL_STATES.NORMAL end
end

function AnimalController:Update()
    local newState = self:GetCurrentState()
    if newState ~= self.CurrentState then
        self.CurrentState = newState
        remote:FireAllClients("animal_state", self.CurrentState)
    end
    self:UpdateAnimalBehaviors()
end

function AnimalController:UpdateAnimalBehaviors()
    local playerPos = self.Player.Character and self.Player.Character:FindFirstChild("HumanoidRootPart")
    if not playerPos then return end
    for _, animal in ipairs(self.Animals) do
        if animal and animal.Parent then
            self:UpdateAnimalBehavior(animal, playerPos.Position)
        end
    end
end

function AnimalController:UpdateAnimalBehavior(animal, playerPos)
    local humanoid = animal:FindFirstChild("Humanoid")
    local hrp = animal:FindFirstChild("HumanoidRootPart")
    if not humanoid or not hrp then return end
    local dist = (hrp.Position - playerPos).Magnitude
    if self.CurrentState == ANIMAL_STATES.NORMAL then
        humanoid.WalkSpeed = 16
    elseif self.CurrentState == ANIMAL_STATES.OBSERVER then
        if dist < 40 then
            humanoid.WalkSpeed = 0
            hrp.CFrame = CFrame.lookAt(hrp.Position, playerPos)
        end
    elseif self.CurrentState == ANIMAL_STATES.ENCIRCLEMENT then
        if dist < 30 and dist > 15 then
            local direction = (hrp.Position - playerPos).Unit
            local perpendicular = Vector3.new(-direction.Z, 0, direction.X)
            local targetPos = playerPos + perpendicular * self.EncirclementRadius
            humanoid:MoveTo(targetPos)
            humanoid.WalkSpeed = 12
        end
    elseif self.CurrentState == ANIMAL_STATES.ALARM then
        if dist < 20 then
            local direction = (playerPos - hrp.Position).Unit
            local blockPos = playerPos + direction * 5
            humanoid:MoveTo(blockPos)
            humanoid.WalkSpeed = 8
            if math.random() < 0.01 then
                playSoundAt(hrp, "rbxassetid://9127608562", 0.7)
            end
        end
    elseif self.CurrentState == ANIMAL_STATES.NECROSIS then
        if dist < 30 then
            hrp.CFrame = hrp.CFrame * CFrame.Angles(0, math.sin(tick() * 20) * 0.1, 0)
            if math.random() < 0.005 then
                animal:Destroy()
            end
        end
    end
end

function AnimalController:CleanupDeadAnimals()
    for i = #self.Animals, 1, -1 do
        if not self.Animals[i].Parent then
            table.remove(self.Animals, i)
        end
    end
end

-- =========================
-- MEMORY FLOODING SYSTEM
-- =========================
local MemoryFlooding = {}
MemoryFlooding.__index = MemoryFlooding

local DataStoreService = game:GetService("DataStoreService")
local PathDataStore = DataStoreService:GetDataStore("PlayerPaths")
local GHOST_DURATION = 5
local MAX_GHOSTS = 3
local FLOOD_THRESHOLD = 0.9

local function createMemoryFlooding(tensionSystem, player)
    local self = setmetatable({}, MemoryFlooding)
    self.TensionSystem = tensionSystem
    self.Player = player
    self.Ghosts = {}
    self.LastSpawnTime = 0
    self.SpawnInterval = 10
    self.PathConnection = nil
    return self
end

function MemoryFlooding:ShouldSpawn()
    local p = self.TensionSystem:getPredictability()
    local now = tick()
    return p > FLOOD_THRESHOLD and #self.Ghosts < MAX_GHOSTS and (now - self.LastSpawnTime) > self.SpawnInterval
end

function MemoryFlooding:SpawnGhost()
    self.LastSpawnTime = tick()
    self:CreateRandomGhost()
end

function MemoryFlooding:CreateRandomGhost()
    local ghost = Instance.new("Model")
    ghost.Name = "MemoryGhost"
    local part = Instance.new("Part")
    part.Size = Vector3.new(4, 6, 2)
    part.BrickColor = BrickColor.new("White")
    part.Material = Enum.Material.Neon
    part.Transparency = 0.7
    part.Anchored = true
    part.CanCollide = false
    part.Parent = ghost
    ghost.Parent = workspace
    local startPos = self.Player.Character and self.Player.Character:FindFirstChild("HumanoidRootPart")
    if startPos then
        part.Position = startPos.Position + Vector3.new(math.random(-20, 20), 0, math.random(-20, 20))
    end
    local direction = Vector3.new(math.random(-1, 1), 0, math.random(-1, 1)).Unit
    local speed = 5
    local wanderConnection
    wanderConnection = game:GetService("RunService").Heartbeat:Connect(function(dt)
        if not ghost.Parent then
            wanderConnection:Disconnect()
            return
        end
        part.Position = part.Position + direction * speed * dt
    end)
    table.insert(self.Ghosts, ghost)
    task.wait(GHOST_DURATION)
    ghost:Destroy()
    wanderConnection:Disconnect()
    for i, g in ipairs(self.Ghosts) do
        if g == ghost then table.remove(self.Ghosts, i) end
    end
end

function MemoryFlooding:Update()
    if self:ShouldSpawn() then
        self:SpawnGhost()
    end
end

-- =========================
-- STILLNESS TRAP WALLS CLOSE
-- =========================
local function closeWallsAroundPlayer(player)
    local root = player.Character and player.Character:FindFirstChild("HumanoidRootPart")
    if not root then return end
    for _, wall in ipairs(workspace:GetDescendants()) do
        if wall:IsA("BasePart") and wall:GetAttribute("ClosingWall") then
            local direction = (wall.Position - root.Position).Unit
            local targetPos = wall.Position + direction * 5
            local tween = game:GetService("TweenService"):Create(wall,
                TweenInfo.new(3, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut),
                {Position = targetPos}
            )
            tween:Play()
        end
    end
end

-- =========================
-- CONSEQUENCE COOLDOWNS
-- =========================
local Cooldowns = {
    DoorLock = 0,
    WallShift = 0,
    FloorCollapse = 0,
    SanctuaryBreach = 0
}

-- =========================
-- INITIALIZE SYSTEMS
-- =========================
local shatter = nil
local animals = nil
local memoryFlooding = nil
local bookController = nil
local artifactManager = nil

-- =========================
-- MAIN LOOP
-- =========================
local LastUpdate = tick()
local LastSync = tick()
local SYNC_INTERVAL = 0.5

print("V12 HORIZON ENGINE ONLINE")
print("Sanctuary and Stillness Trap Active")

game:GetService("RunService").Heartbeat:Connect(function()
    local now = tick()
    local dt = now - LastUpdate
    LastUpdate = now

    eventStressAccumulator = eventStressAccumulator * eventStressDecay

    -- Update cooldowns
    for key, timeRemaining in pairs(Cooldowns) do
        if timeRemaining > 0 then
            Cooldowns[key] = timeRemaining - dt
        end
    end

    local player = game.Players:GetPlayers()[1]
    if player and player.Character and player.Character:FindFirstChild("HumanoidRootPart") then
        local root = player.Character.HumanoidRootPart

        -- get authoritative player state and its tension system
        local ps = SystemManager.getPlayerState(player)
        local TensionSystem = ps and ps.TensionEngine

        if not shatter then
            local stalker = workspace:FindFirstChild("Stalker")
            -- Use authoritative player state
            shatter = createShatterController(ps, stalker, player)
            animals = createAnimalController(ps, player)
            memoryFlooding = createMemoryFlooding(ps, player)
            bookController = BookController.new(player, ps)
            artifactManager = ArtifactManager.new(ps, player)
            
            for _, animal in ipairs(workspace:GetDescendants()) do
                if animal:IsA("Model") and animal:GetAttribute("Animal") then
                    animals:RegisterAnimal(animal)
                end
            end
        end

        local sanctuary = isPlayerInSanctuary(player)
        if sanctuary and not inSanctuary[player] then
            inSanctuary[player] = true
            print("Player entered sanctuary")
        elseif not sanctuary and inSanctuary[player] then
            inSanctuary[player] = false
            print("Player left sanctuary")
        end

        if not inSanctuary[player] then
            TensionSystem:updateMemory(root.Position)
        end
        
        local M_avg = TensionSystem:getAverageMemory()
        local P = TensionSystem:getPredictability()

        -- STILLNESS TRAP
        local currentPos = root.Position
        if lastPosition[player] then
            local distance = (currentPos - lastPosition[player]).Magnitude
            if distance < 0.1 then
                local speed = 1
                if P > 0.6 then
                    speed = 1 + P
                end
                stillnessTimer[player] = (stillnessTimer[player] or 0) + dt * speed
                stillnessVisualTimer[player] = (stillnessVisualTimer[player] or 0) + dt * speed
                if stillnessVisualTimer[player] > 10 and stillnessVisualTimer[player] < 30 then
                    remote:FireClient(player, "stillness_shadow")
                end
                if stillnessVisualTimer[player] > 60 and not wallsClosed[player] then
                    wallsClosed[player] = true
                    closeWallsAroundPlayer(player)
                    remote:FireClient(player, "walls_closing")
                end
                if stillnessTimer[player] > 120 then
                    player.Character.Humanoid.Health = 0
                    remote:FireClient(player, "game_over", "absorbed")
                    stillnessTimer[player] = 0
                elseif stillnessTimer[player] > 30 then
                    TensionSystem:updateMemory(currentPos)
                    if stillnessTimer[player] > 35 then
                        print("Stillness trap triggered: memory increased")
                        stillnessTimer[player] = 30
                    end
                end
            else
                stillnessTimer[player] = 0
                stillnessVisualTimer[player] = 0
                wallsClosed[player] = false
            end
        end
        lastPosition[player] = currentPos

        x_noise = sxc_step(x_noise)

        local serverRawSignal = 
            (root.Velocity.Magnitude / 20) * 0.6 +
            -- memory (M_avg) removed so memory does not directly influence tension signal
            (math.abs(x_noise) * 0.30) +
            eventStressAccumulator
        
        local clientSignal = _G.ClientSignal[player] or 0
        local blendedSignal = serverRawSignal * 0.7 + clientSignal * 0.3
        local signal = math.clamp(blendedSignal, 0, 2.0)

        local state, didRupture = TensionSystem:update(signal, root.Position)
        local tension = TensionSystem:getTension()

        if inSanctuary[player] then
            TensionSystem:applySanctuaryDecay(dt, 0.95)
        end

        local Lighting = game:GetService("Lighting")
        local stalker = workspace:FindFirstChild("Stalker")
        
        if didRupture then
            print("!!! RUPTURE EVENT TRIGGERED !!!")
            Lighting.Brightness = 0.05
            remote:FireClient(player, "rupture_effect")
            if stalker then
                local originalPos = stalker.Position
                local manifestPos = root.Position + Vector3.new(math.random(-15, 15), 0, math.random(-15, 15))
                stalker.Position = manifestPos
                remote:FireClient(player, "stalker_manifest")
                task.wait(0.5)
                stalker.Position = Vector3.new(0, -100, 0)
                task.wait(2)
                local target = TensionSystem:getMaxMemoryPosition()
                if target then
                    stalker.Position = target + Vector3.new(0, 3, 0)
                end
            end
            if artifactManager then artifactManager:OnRupture() end
        else
            if state == "HIGH" or state == "CRITICAL" then
                Lighting.Brightness = 0.6
            elseif state == "MEDIUM" then
                Lighting.Brightness = 1.2
            elseif state == "RECOVERY" then
                Lighting.Brightness = 0.3
            else
                Lighting.Brightness = 2.0
            end
        end

        -- Throttled sync
        if now - LastSync >= SYNC_INTERVAL then
            LastSync = now
            remote:FireAllClients(tension)
        end
        
        _G.V12_Tension = tension

        if stalker and not didRupture then
            local target = TensionSystem:getMaxMemoryPosition()
            if target then 
                stalker.Position = target + Vector3.new(0, 3, 0) 
            end
        end

        -- Update BookController and ArtifactManager
        if bookController then
            bookController:Update(stalker and (root.Position - stalker.Position).Magnitude < 50, inSanctuary[player], false)
        end
        if artifactManager then artifactManager:Update() end

        -- HIGH P CONSEQUENCES (with cooldowns)
        if P > 0.4 and math.random() < 0.01 then
            playSoundAt(root, "rbxassetid://9127608562", 0.4)
        end
        if P > 0.6 and math.random() < 0.005 then
            remote:FireClient(player, "false_visual")
            playSoundAt(root, "rbxassetid://9127608562", 0.3)
        end
        if P > 0.4 and math.random() < 0.002 then
            remote:FireClient(player, "resource_decay")
        end
        if inSanctuary[player] and P > 0.4 and math.random() < 0.01 then
            remote:FireClient(player, "sanctuary_flicker")
        end
        if inSanctuary[player] and P > 0.6 and Cooldowns.SanctuaryBreach <= 0 and math.random() < 0.005 then
            if stalker then
                Cooldowns.SanctuaryBreach = 30
                local spawnPos = root.Position + Vector3.new(math.random(-15, 15), 0, math.random(-15, 15))
                stalker.Position = spawnPos
                playSoundAt(stalker, "rbxassetid://9127608562", 0.8)
                print("Sanctuary breach! Stalker appeared inside")
                task.delay(3, function()
                    local target = TensionSystem:getMaxMemoryPosition()
                    if target and stalker and stalker.Parent then
                        stalker.Position = target + Vector3.new(0, 3, 0)
                    end
                end)
            end
        end
        
        if P > 0.7 and Cooldowns.DoorLock <= 0 then
            local nearestDoor = nil
            local nearestDist = 20
            for _, door in ipairs(workspace:GetDescendants()) do
                if door:IsA("BasePart") and door:GetAttribute("Door") and not door:GetAttribute("Locked") then
                    local dist = (door.Position - root.Position).Magnitude
                    if dist < nearestDist then
                        nearestDist = dist
                        nearestDoor = door
                    end
                end
            end
            if nearestDoor and nearestDist < 5 then
                Cooldowns.DoorLock = 15
                nearestDoor:SetAttribute("Locked", true)
                playSoundAt(nearestDoor, "rbxassetid://9127599111", 0.7)
                remote:FireClient(player, "door_lock", nearestDoor.Position)
                print("Door locked")
                task.delay(10, function()
                    if nearestDoor and nearestDoor.Parent then
                        nearestDoor:SetAttribute("Locked", false)
                    end
                end)
            end
        end
        
        if P > 0.8 and Cooldowns.WallShift <= 0 and math.random() < 0.002 then
            local shiftableWalls = {}
            for _, wall in ipairs(workspace:GetDescendants()) do
                if wall:IsA("BasePart") and wall:GetAttribute("Shiftable") and not wall:GetAttribute("IsShifting") then
                    table.insert(shiftableWalls, wall)
                end
            end
            if #shiftableWalls > 0 then
                Cooldowns.WallShift = 20
                local wall = shiftableWalls[math.random(1, #shiftableWalls)]
                wall:SetAttribute("IsShifting", true)
                local originalPos = wall.Position
                local newPos = originalPos + Vector3.new(math.random(-10, 10), 0, math.random(-10, 10))
                local tween = game:GetService("TweenService"):Create(wall, TweenInfo.new(2, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut), {Position = newPos})
                tween:Play()
                playSoundAt(wall, "rbxassetid://9127599111", 0.5)
                print("Wall shifted")
                task.delay(15, function()
                    if wall and wall.Parent then
                        local backTween = game:GetService("TweenService"):Create(wall, TweenInfo.new(2, Enum.EasingStyle.Quad, Enum.EasingDirection.InOut), {Position = originalPos})
                        backTween:Play()
                        backTween.Completed:Wait()
                        wall:SetAttribute("IsShifting", false)
                    end
                end)
            end
        end
        
        if P > 0.8 and Cooldowns.FloorCollapse <= 0 and math.random() < 0.002 then
            local raycastParams = RaycastParams.new()
            raycastParams.FilterType = Enum.RaycastFilterType.Blacklist
            raycastParams.FilterDescendantsInstances = {player.Character}
            local rayResult = workspace:Raycast(root.Position, Vector3.new(0, -5, 0), raycastParams)
            if rayResult and rayResult.Instance:GetAttribute("Collapsible") and not rayResult.Instance:GetAttribute("IsCollapsed") then
                local floor = rayResult.Instance
                Cooldowns.FloorCollapse = 15
                floor:SetAttribute("IsCollapsed", true)
                local collapseTween = game:GetService("TweenService"):Create(floor, TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.In), {CFrame = floor.CFrame * CFrame.new(0, -3, 0)})
                collapseTween:Play()
                playSoundAt(floor, "rbxassetid://9127599111", 0.8)
                remote:FireClient(player, "floor_collapse")
                print("Floor collapsed")
                task.delay(10, function()
                    if floor and floor.Parent then
                        local respawnTween = game:GetService("TweenService"):Create(floor, TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out), {CFrame = floor.CFrame * CFrame.new(0, 3, 0)})
                        respawnTween:Play()
                        respawnTween.Completed:Wait()
                        floor:SetAttribute("IsCollapsed", false)
                    end
                end)
            end
        end
        
        if P > 0.7 and math.random() < 0.01 then
            local lagMs = math.random(50, 150)
            remote:FireClient(player, "input_lag", lagMs)
            print("Input lag triggered: " .. lagMs .. "ms")
        end

        if shatter then shatter:Update() end
        if animals then 
            animals:Update()
            animals:CleanupDeadAnimals()
        end
        if memoryFlooding then memoryFlooding:Update() end

        telemetryTimer = telemetryTimer + dt
        if telemetryTimer >= 1.0 then
            telemetryTimer = 0
            printTelemetry(tension, M_avg, P, root.Velocity.Magnitude, signal, state, eventStressAccumulator)
        end
    end
end)
