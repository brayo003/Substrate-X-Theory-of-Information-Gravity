--[[
    SanctuaryDegradation.server.lua
    Phase 3 Critical Task: Sanctuary Degradation
    
    Each second player spends in sanctuary:
    - Memory field M increases by 0.001 per second (safety decays)
    - After 2 minutes, sanctuary starts flickering
    - After 5 minutes, stalker can circle outside
    - Visual feedback: lights flicker, shadows move
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Debris = game:GetService("Debris")

-- Dependencies
local Shared = ReplicatedStorage:WaitForChild("Shared")
-- This module now consumes the authoritative PlayerState rather than creating or requiring
-- MemoryField/TensionEngine directly.

-- Remote for client effects
local remote = ReplicatedStorage:FindFirstChild("V12_Sync") or Instance.new("RemoteEvent")
remote.Name = "V12_Sync"
remote.Parent = ReplicatedStorage

local SanctuaryDegradation = {}
SanctuaryDegradation.__index = SanctuaryDegradation

-- Degradation parameters
local DEGRADATION_CONFIG = {
    memoryIncreaseRate = 0.001,      -- M increase per second in sanctuary
    flickerStartTime = 120.0,        -- 2 minutes before flickering starts
    stalkerCircleTime = 300.0,       -- 5 minutes before stalker appears outside
    flickerInterval = 5.0,           -- Seconds between flickers
    flickerDuration = 0.5,           -- Duration of each flicker
    shadowMovementInterval = 10.0,   -- Seconds between shadow movements
    updateInterval = 1.0             -- How often to update degradation
}

function SanctuaryDegradation.new(player, playerState, sanctuaryController)
    local self = setmetatable({}, SanctuaryDegradation)

    self.Player = player
    self.PlayerState = playerState
    self.SanctuaryController = sanctuaryController
    
    -- Degradation state
    self.TimeInSanctuary = 0.0
    self.FlickeringActive = false
    self.StalkerCircling = false
    self.LastFlickerTime = 0
    self.LastShadowMovement = 0
    self.LastUpdateTime = 0
    
    -- Connect events
    self:connectEvents()
    
    print("SanctuaryDegradation initialized for player:", player.Name)
    return self
end

function SanctuaryDegradation:connectEvents()
    -- Update degradation state
    RunService.Heartbeat:Connect(function(dt)
        self:updateDegradation(dt)
    end)
end

function SanctuaryDegradation:updateDegradation(dt)
    -- Check if player is in sanctuary
    if not self.SanctuaryController or not self.SanctuaryController.IsInSanctuary then
        -- Reset when leaving sanctuary
        if self.TimeInSanctuary > 0 then
            self:onLeaveSanctuary()
        end
        self.TimeInSanctuary = 0
        return
    end
    
    -- Player is in sanctuary, accumulate time
    self.TimeInSanctuary = self.TimeInSanctuary + dt
    
    -- Update degradation effects periodically
    local now = tick()
    if now - self.LastUpdateTime >= DEGRADATION_CONFIG.updateInterval then
        self:updateDegradationEffects(dt)
        self.LastUpdateTime = now
    end
    
    -- Check for degradation milestones
    self:checkMilestones()
    
    -- Apply memory field increase
    self:increaseMemoryInSanctuary(dt)
end

function SanctuaryDegradation:increaseMemoryInSanctuary(dt)
    -- Increase memory field at current position
    local character = self.Player.Character
    if not character then return end
    
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end
    
    local position = hrp.Position
    
    local ps = self.PlayerState
    if not ps or not ps.MemoryField then return end

    local mem = ps.MemoryField
    -- Increase M at current position
    if mem.addMemoryAtPosition then
        mem:addMemoryAtPosition(position, DEGRADATION_CONFIG.memoryIncreaseRate * dt)
    end

    -- Also increase M growth multiplier temporarily
    if mem.setGrowthMultiplier then
        local currentMultiplier = mem.getGrowthMultiplier and mem:getGrowthMultiplier() or 1.0
        mem:setGrowthMultiplier(currentMultiplier + (DEGRADATION_CONFIG.memoryIncreaseRate * dt))
    end
end

function SanctuaryDegradation:checkMilestones()
    local time = self.TimeInSanctuary
    
    -- Milestone 1: Start flickering after 2 minutes
    if time >= DEGRADATION_CONFIG.flickerStartTime and not self.FlickeringActive then
        self:activateFlickering()
    end
    
    -- Milestone 2: Stalker circles after 5 minutes
    if time >= DEGRADATION_CONFIG.stalkerCircleTime and not self.StalkerCircling then
        self:activateStalkerCircling()
    end
end

function SanctuaryDegradation:activateFlickering()
    print("Sanctuary flickering activated for player:", self.Player.Name)
    self.FlickeringActive = true
    
    -- Send client notification
    remote:FireClient(self.Player, "sanctuary_flickering_start")
end

function SanctuaryDegradation:activateStalkerCircling()
    print("Stalker circling activated for player:", self.Player.Name)
    self.StalkerCircling = true
    
    -- Spawn circling stalker
    self:spawnCirclingStalker()
    
    -- Send client notification
    remote:FireClient(self.Player, "sanctuary_stalker_circle")
end

function SanctuaryDegradation:updateDegradationEffects(dt)
    local now = tick()
    
    -- Handle flickering
    if self.FlickeringActive then
        if now - self.LastFlickerTime >= DEGRADATION_CONFIG.flickerInterval then
            self:triggerFlicker()
            self.LastFlickerTime = now
        end
    end
    
    -- Handle shadow movements
    if self.StalkerCircling then
        if now - self.LastShadowMovement >= DEGRADATION_CONFIG.shadowMovementInterval then
            self:triggerShadowMovement()
            self.LastShadowMovement = now
        end
    end
    
    -- Update circling stalker
    if self.StalkerCircling then
        self:updateCirclingStalker(dt)
    end
end

function SanctuaryDegradation:triggerFlicker()
    -- Send flicker effect to client
    remote:FireClient(self.Player, "sanctuary_flicker")
    
    -- Also trigger in-world flicker
    self:createWorldFlicker()
end

function SanctuaryDegradation:createWorldFlicker()
    -- Create temporary lighting flicker
    local lighting = game:GetService("Lighting")
    local originalBrightness = lighting.Brightness
    
    -- Quick flicker
    lighting.Brightness = originalBrightness * 0.3
    task.wait(DEGRADATION_CONFIG.flickerDuration)
    lighting.Brightness = originalBrightness
end

function SanctuaryDegradation:triggerShadowMovement()
    -- Send shadow movement effect to client
    remote:FireClient(self.Player, "sanctuary_shadow_move")
    
    -- Create shadow movement in world
    self:createShadowMovement()
end

function SanctuaryDegradation:createShadowMovement()
    -- Create moving shadow effect around sanctuary
    local character = self.Player.Character
    if not character then return end
    
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end
    
    local playerPos = hrp.Position
    
    -- Create temporary shadow parts
    for i = 1, 3 do
        local shadow = Instance.new("Part")
        shadow.Size = Vector3.new(6, 0.1, 6)
        shadow.BrickColor = BrickColor.new("Really black")
        shadow.Material = Enum.Material.Neon
        shadow.Anchored = true
        shadow.CanCollide = false
        shadow.Transparency = 0.5
        
        -- Position around player
        local angle = (i / 3) * math.pi * 2
        local distance = 8 + math.random(-2, 2)
        shadow.Position = playerPos + Vector3.new(math.cos(angle) * distance, 0, math.sin(angle) * distance)
        
        shadow.Parent = workspace
        
        -- Animate movement
        local tween = game:GetService("TweenService"):Create(
            shadow,
            TweenInfo.new(2, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut),
            {Position = shadow.Position + Vector3.new(math.random(-2, 2), 0, math.random(-2, 2))}
        )
        tween:Play()
        
        -- Remove after animation
        tween.Completed:Connect(function()
            shadow:Destroy()
        end)
    end
end

function SanctuaryDegradation:spawnCirclingStalker()
    -- Create a circling stalker outside sanctuary
    local character = self.Player.Character
    if not character then return end
    
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end
    
    local playerPos = hrp.Position
    
    -- Create stalker
    local stalker = Instance.new("Model")
    stalker.Name = "CirclingStalker"
    
    local torso = Instance.new("Part")
    torso.Name = "Torso"
    torso.Size = Vector3.new(4, 6, 2)
    torso.BrickColor = BrickColor.new("Really black")
    torso.Material = Enum.Material.Neon
    torso.Transparency = 0.7
    torso.Anchored = true
    torso.CanCollide = false
    torso.Position = playerPos + Vector3.new(15, 0, 0) -- Start 15 studs away
    torso.Parent = stalker
    
    -- Add glow effect
    local glow = Instance.new("PointLight")
    glow.Color = Color3.new(0.8, 0, 0)
    glow.Brightness = 2
    glow.Range = 10
    glow.Parent = torso
    
    -- Add sound
    local sound = Instance.new("Sound")
    sound.SoundId = "rbxassetid://9127608562"
    sound.Volume = 0.3
    sound.Looped = true
    sound.Parent = torso
    sound:Play()
    
    stalker.Parent = workspace
    
    -- Store stalker reference
    self.CirclingStalker = stalker
    
    -- Start circling animation
    self:startCirclingAnimation(stalker, playerPos)
    
    -- Send to client
    remote:FireClient(self.Player, "circling_stalker_spawn", {
        position = torso.Position,
        stalkerId = "circling_stalker"
    })
end

function SanctuaryDegradation:startCirclingAnimation(stalker, centerPos)
    if not stalker then return end
    
    local torso = stalker:FindFirstChild("Torso")
    if not torso then return end
    
    -- Create circling motion
    local radius = 15
    local speed = 0.5 -- radians per second
    
    local startTime = tick()
    
    local connection
    connection = RunService.Heartbeat:Connect(function(dt)
        if not stalker.Parent then
            connection:Disconnect()
            return
        end
        
        local elapsed = tick() - startTime
        local angle = elapsed * speed
        
        -- Update position in circle
        local newPos = centerPos + Vector3.new(
            math.cos(angle) * radius,
            0,
            math.sin(angle) * radius
        )
        
        torso.Position = newPos
    end)
    
    -- Store connection for cleanup
    self.CirclingConnection = connection
end

function SanctuaryDegradation:updateCirclingStalker(dt)
    -- Update circling stalker behavior
    if not self.CirclingStalker or not self.CirclingStalker.Parent then return end
    
    local character = self.Player.Character
    if not character then return end
    
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end
    
    -- Update circle center to follow player slowly
    local playerPos = hrp.Position
    local stalkerTorso = self.CirclingStalker:FindFirstChild("Torso")
    if stalkerTorso then
        -- Gradually move circle center toward player
        local currentCenter = stalkerTorso.Position - Vector3.new(15, 0, 0) -- Approximate current center
        local newCenter = currentCenter:Lerp(playerPos, 0.01) -- Slow lerp
        
        -- Update animation with new center
        if self.CirclingConnection then
            self.CirclingConnection:Disconnect()
        end
        self:startCirclingAnimation(self.CirclingStalker, newCenter)
    end
end

function SanctuaryDegradation:onLeaveSanctuary()
    print("Player left sanctuary - degradation effects reset")
    
    -- Send client notification
    remote:FireClient(self.Player, "sanctuary_degradation_reset")
    
    -- Reset degradation state
    self.TimeInSanctuary = 0
    self.FlickeringActive = false
    self.StalkerCircling = false
    self.LastFlickerTime = 0
    self.LastShadowMovement = 0
    
    -- Remove circling stalker
    if self.CirclingStalker then
        if self.CirclingConnection then
            self.CirclingConnection:Disconnect()
        end
        self.CirclingStalker:Destroy()
        self.CirclingStalker = nil
    end
end

function SanctuaryDegradation:getDegradationState()
    -- Return current degradation state
    return {
        timeInSanctuary = self.TimeInSanctuary,
        flickeringActive = self.FlickeringActive,
        stalkerCircling = self.StalkerCircling,
        memoryIncreaseRate = DEGRADATION_CONFIG.memoryIncreaseRate
    }
end

function SanctuaryDegradation:destroy()
    -- Clean up all effects
    self:onLeaveSanctuary()
    
    print("SanctuaryDegradation destroyed for player:", self.Player.Name)
end

return SanctuaryDegradation
