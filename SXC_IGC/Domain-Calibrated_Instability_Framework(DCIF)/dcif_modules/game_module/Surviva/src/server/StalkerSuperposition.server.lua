--[[
    StalkerSuperposition.server.lua
    Phase 2 Critical Task: Stalker Superposition
    
    Creates two ghost stalkers:
    - One at highest M location (memory-based)
    - One at highest P location (prediction-based)
    
    When player commits to direction, one becomes real, other vanishes
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Debris = game:GetService("Debris")

-- Dependencies
local Shared = ReplicatedStorage:WaitForChild("Shared")
local MemoryField = require(Shared:WaitForChild("MemoryField"))
local PredictionField = require(script.Parent.PredictionField)

-- Remote for client effects
local remote = ReplicatedStorage:FindFirstChild("V12_Sync") or Instance.new("RemoteEvent")
remote.Name = "V12_Sync"
remote.Parent = ReplicatedStorage

local StalkerSuperposition = {}
StalkerSuperposition.__index = StalkerSuperposition

-- Superposition parameters
local SUPERPOSITION_CONFIG = {
    ghostTransparency = 0.7,          -- How transparent ghosts are
    ghostSize = Vector3.new(4, 6, 2),  -- Size of ghost stalkers
    soundRadius = 30,                  -- How far sound can be heard
    commitThreshold = 8,               -- Velocity threshold for "commitment"
    collapseDelay = 0.5,               -- Delay before collapse after commitment
    ghostLifetime = 10,                -- How long ghosts exist before re-evaluating
    updateInterval = 1.0               -- How often to update ghost positions
}

function StalkerSuperposition.new(player, playerState)
    local self = setmetatable({}, StalkerSuperposition)

    self.Player = player
    self.PlayerState = playerState
    self.MemoryField = playerState and playerState.MemoryField
    self.PredictionField = playerState and playerState.PredictionField
    
    -- Superposition state
    self.IsActive = false
    self.MemoryGhost = nil
    self.PredictionGhost = nil
    self.RealStalker = nil
    self.LastUpdateTime = 0
    self.GhostCreatedTime = 0
    
    -- Player commitment tracking
    self.LastPosition = Vector3.new()
    self.VelocityHistory = {}
    self.IsCommitted = false
    self.CommitDirection = Vector3.new()
    
    -- Connect events
    self:connectEvents()
    
    print("StalkerSuperposition initialized for player:", player.Name)
    return self
end

function StalkerSuperposition:connectEvents()
    -- Update superposition state
    RunService.Heartbeat:Connect(function(dt)
        self:update(dt)
    end)
end

function StalkerSuperposition:update(dt)
    local character = self.Player.Character
    if not character then return end
    
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end
    
    -- Track player movement for commitment detection
    self:trackPlayerMovement(hrp.Position, dt)
    
    -- Update ghost positions periodically
    local now = tick()
    if now - self.LastUpdateTime >= SUPERPOSITION_CONFIG.updateInterval then
        self:updateGhostPositions()
        self.LastUpdateTime = now
    end
    
    -- Check for commitment and collapse
    if self:IsActive and not self.IsCommitted then
        self:checkForCommitment()
    end
    
    -- Check if ghosts need to be recreated
    if self.IsActive and now - self.GhostCreatedTime >= SUPERPOSITION_CONFIG.ghostLifetime then
        self:recreateGhosts()
    end
    
    self.LastPosition = hrp.Position
end

function StalkerSuperposition:trackPlayerMovement(position, dt)
    -- Calculate velocity
    local velocity = (position - self.LastPosition) / dt
    table.insert(self.VelocityHistory, velocity)
    
    -- Keep only recent history
    if #self.VelocityHistory > 10 then
        table.remove(self.VelocityHistory, 1)
    end
    
    -- Calculate average velocity
    local avgVelocity = Vector3.new(0, 0, 0)
    for _, vel in ipairs(self.VelocityHistory) do
        avgVelocity = avgVelocity + vel
    end
    avgVelocity = avgVelocity / #self.VelocityHistory
    
    -- Check if player is committed to a direction
    local speed = avgVelocity.Magnitude
    if speed >= SUPERPOSITION_CONFIG.commitThreshold then
        if not self.IsCommitted then
            self.IsCommitted = true
            self.CommitDirection = avgVelocity.Unit
            self:onPlayerCommitted()
        end
    else
        self.IsCommitted = false
        self.CommitDirection = Vector3.new()
    end
end

function StalkerSuperposition:updateGhostPositions()
    if not self.IsActive then return end
    
    -- Get highest M location
    local memoryPos, memoryValue = self.MemoryField:getHighestMLocation()
    
    -- Get highest P location
    local predictionPos, predictionValue = self.PredictionField:getHighestPLocation()
    
    -- Update memory ghost
    if self.MemoryGhost and memoryPos then
        self:moveGhost(self.MemoryGhost, memoryPos, memoryValue, "memory")
    end
    
    -- Update prediction ghost
    if self.PredictionGhost and predictionPos then
        self:moveGhost(self.PredictionGhost, predictionPos, predictionValue, "prediction")
    end
end

function StalkerSuperposition:activateSuperposition()
    print("Activating stalker superposition for player:", self.Player.Name)
    self.IsActive = true
    self.GhostCreatedTime = tick()
    
    -- Create ghost stalkers
    self:createGhostStalkers()
    
    -- Send client notification
    remote:FireClient(self.Player, "superposition_activate")
end

function StalkerSuperposition:deactivateSuperposition()
    print("Deactivating stalker superposition for player:", self.Player.Name)
    self.IsActive = false
    self.IsCommitted = false
    
    -- Remove ghosts and real stalker
    self:removeAllStalkers()
    
    -- Send client notification
    remote:FireClient(self.Player, "superposition_deactivate")
end

function StalkerSuperposition:createGhostStalkers()
    -- Get positions for ghosts
    local memoryPos, memoryValue = self.MemoryField:getHighestMLocation()
    local predictionPos, predictionValue = self.PredictionField:getHighestPLocation()
    
    -- Create memory-based ghost
    if memoryPos and memoryValue > 0.1 then
        self.MemoryGhost = self:createGhost(memoryPos, memoryValue, "memory")
    end
    
    -- Create prediction-based ghost
    if predictionPos and predictionValue > 0.1 then
        self.PredictionGhost = self:createGhost(predictionPos, predictionValue, "prediction")
    end
    
    -- Send ghost data to client
    self:sendGhostDataToClient()
end

function StalkerSuperposition:createGhost(position, intensity, ghostType)
    local ghost = Instance.new("Part")
    ghost.Name = "GhostStalker_" .. ghostType
    ghost.Size = SUPERPOSITION_CONFIG.ghostSize
    ghost.BrickColor = ghostType == "memory" and BrickColor.new("Dark grey") or BrickColor.new("Really black")
    ghost.Material = Enum.Material.Neon
    ghost.Transparency = SUPERPOSITION_CONFIG.ghostTransparency
    ghost.Anchored = true
    ghost.CanCollide = false
    ghost.Position = position + Vector3.new(0, 3, 0) -- Elevate slightly
    ghost.Parent = workspace
    
    -- Add glow effect
    local glow = Instance.new("PointLight")
    glow.Color = ghostType == "memory" and Color3.new(0.5, 0.5, 0.5) or Color3.new(0.2, 0, 0.2)
    glow.Brightness = intensity * 2
    glow.Range = 10
    glow.Parent = ghost
    
    -- Create sound cue
    self:createGhostSound(ghost, ghostType, intensity)
    
    return ghost
end

function StalkerSuperposition:createGhostSound(ghost, ghostType, intensity)
    local sound = Instance.new("Sound")
    sound.SoundId = ghostType == "memory" and "rbxassetid://9127599111" or "rbxassetid://9127608562"
    sound.Volume = intensity * 0.3
    sound.Looped = true
    sound.SoundGroup = workspace:FindFirstChild("AmbientSounds")
    sound.Parent = ghost
    sound:Play()
    
    -- Add spatial sound effect
    sound.RollOffMaxDistance = SUPERPOSITION_CONFIG.soundRadius
    sound.RollOffMinDistance = 5
end

function StalkerSuperposition:moveGhost(ghost, position, intensity, ghostType)
    if not ghost then return end
    
    -- Smooth movement to new position
    local targetPos = position + Vector3.new(0, 3, 0)
    local tween = game:GetService("TweenService"):Create(
        ghost,
        TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {Position = targetPos}
    )
    tween:Play()
    
    -- Update glow intensity
    local glow = ghost:FindFirstChild("PointLight")
    if glow then
        glow.Brightness = intensity * 2
    end
    
    -- Update sound volume
    local sound = ghost:FindFirstChild("Sound")
    if sound then
        sound.Volume = intensity * 0.3
    end
end

function StalkerSuperposition:checkForCommitment()
    if not self.IsCommitted then return end
    
    -- Determine which ghost to collapse to based on commitment direction
    local targetGhost = self:determineCollapseTarget()
    
    if targetGhost then
        self:collapseTo(targetGhost)
    end
end

function StalkerSuperposition:determineCollapseTarget()
    local character = self.Player.Character
    if not character then return nil end
    
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return nil end
    
    local playerPos = hrp.Position
    
    -- Calculate distances to ghosts
    local memoryDistance = self.MemoryGhost and (self.MemoryGhost.Position - playerPos).Magnitude or math.huge
    local predictionDistance = self.PredictionGhost and (self.PredictionGhost.Position - playerPos).Magnitude or math.huge
    
    -- Check which ghost is in the direction of commitment
    local memoryDirection = self.MemoryGhost and (self.MemoryGhost.Position - playerPos).Unit or Vector3.new()
    local predictionDirection = self.PredictionGhost and (self.PredictionGhost.Position - playerPos).Unit or Vector3.new()
    
    local memoryAlignment = self.CommitDirection:Dot(memoryDirection)
    local predictionAlignment = self.CommitDirection:Dot(predictionDirection)
    
    -- Choose the ghost that aligns best with commitment direction
    if memoryAlignment > predictionAlignment then
        return self.MemoryGhost
    else
        return self.PredictionGhost
    end
end

function StalkerSuperposition:collapseTo(targetGhost)
    print("Collapsing superposition to target ghost for player:", self.Player.Name)
    
    -- Remove the other ghost
    if targetGhost == self.MemoryGhost and self.PredictionGhost then
        self:removeGhost(self.PredictionGhost)
        self.PredictionGhost = nil
    elseif targetGhost == self.PredictionGhost and self.MemoryGhost then
        self:removeGhost(self.MemoryGhost)
        self.MemoryGhost = nil
    end
    
    -- Convert target ghost to real stalker
    self.RealStalker = self:convertToRealStalker(targetGhost)
    
    -- Send collapse effect to client
    remote:FireClient(self.Player, "superposition_collapse", {
        position = self.RealStalker.Position,
        ghostType = targetGhost.Name:find("memory") and "memory" or "prediction"
    })
    
    -- Deactivate superposition
    self.IsActive = false
end

function StalkerSuperposition:convertToRealStalker(ghost)
    if not ghost then return nil end
    
    -- Make ghost solid and less transparent
    ghost.Transparency = 0.2
    ghost.BrickColor = BrickColor.new("Really black")
    ghost.CanCollide = true
    
    -- Enhance glow
    local glow = ghost:FindFirstChild("PointLight")
    if glow then
        glow.Color = Color3.new(1, 0, 0)
        glow.Brightness = 5
        glow.Range = 20
    end
    
    -- Enhance sound
    local sound = ghost:FindFirstChild("Sound")
    if sound then
        sound.Volume = 0.8
        sound.SoundId = "rbxassetid://9127608562" -- More aggressive sound
    end
    
    -- Rename to indicate it's real
    ghost.Name = "RealStalker"
    
    return ghost
end

function StalkerSuperposition:removeGhost(ghost)
    if ghost then
        -- Fade out effect
        local tween = game:GetService("TweenService"):Create(
            ghost,
            TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
            {Transparency = 1}
        )
        tween:Play()
        
        tween.Completed:Connect(function()
            ghost:Destroy()
        end)
    end
end

function StalkerSuperposition:removeAllStalkers()
    if self.MemoryGhost then
        self:removeGhost(self.MemoryGhost)
        self.MemoryGhost = nil
    end
    
    if self.PredictionGhost then
        self:removeGhost(self.PredictionGhost)
        self.PredictionGhost = nil
    end
    
    if self.RealStalker then
        self:removeGhost(self.RealStalker)
        self.RealStalker = nil
    end
end

function StalkerSuperposition:recreateGhosts()
    print("Recreating ghosts for player:", self.Player.Name)
    
    -- Remove existing ghosts
    self:removeAllStalkers()
    
    -- Create new ghosts
    self:createGhostStalkers()
    self.GhostCreatedTime = tick()
end

function StalkerSuperposition:sendGhostDataToClient()
    local ghostData = {}
    
    if self.MemoryGhost then
        ghostData.memory = {
            position = self.MemoryGhost.Position,
            intensity = self.MemoryField:getHighestMLocation() or 0
        }
    end
    
    if self.PredictionGhost then
        ghostData.prediction = {
            position = self.PredictionGhost.Position,
            intensity = self.PredictionField:getHighestPLocation() or 0
        }
    end
    
    remote:FireClient(self.Player, "ghost_update", ghostData)
end

function StalkerSuperposition:onPlayerCommitted()
    print("Player committed to direction:", self.Player.Name)
    
    -- Send commitment notification to client
    remote:FireClient(self.Player, "player_committed", {
        direction = self.CommitDirection,
        speed = self.VelocityHistory[#self.VelocityHistory].Magnitude
    })
end

function StalkerSuperposition:destroy()
    -- Clean up all stalkers
    self:removeAllStalkers()
    
    print("StalkerSuperposition destroyed for player:", self.Player.Name)
end

return StalkerSuperposition
