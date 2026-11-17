--[[
    StillnessTrapController.server.lua
    Phase 1 Critical Task: Stillness Trap
    
    If player stands still >30 seconds:
    - Memory field (M) increases 3x faster at current position
    - Environment closes in (walls shift, shadows extend)
    - After 60 seconds: ambient sounds stop (silence = dread)
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Debris = game:GetService("Debris")

-- Dependencies
local Shared = ReplicatedStorage:WaitForChild("Shared")
local MemoryField = require(Shared:WaitForChild("MemoryField"))

-- Remote for client effects
local remote = ReplicatedStorage:FindFirstChild("V12_Sync") or Instance.new("RemoteEvent")
remote.Name = "V12_Sync"
remote.Parent = ReplicatedStorage

local StillnessTrapController = {}
StillnessTrapController.__index = StillnessTrapController

-- Stillness trap parameters
local STILLNESS_CONFIG = {
    stillnessThreshold = 0.1,        -- Movement speed threshold for "still"
    stillnessTimeThreshold = 30.0,   -- Seconds before trap activates
    severeStillnessTime = 60.0,      -- Seconds for severe effects
    memoryMultiplier = 3.0,          -- M growth multiplier when still
    environmentUpdateInterval = 10.0, -- Seconds between environment effects
    positionCheckInterval = 0.5      -- How often to check player movement
}

function StillnessTrapController.new(player, playerState)
    local self = setmetatable({}, StillnessTrapController)
    
    self.Player = player
    self.PlayerState = playerState
    self.MemoryField = playerState and playerState.MemoryField
    
    -- Stillness tracking
    self.IsStill = false
    self.StillnessStartTime = 0
    self.TotalStillnessTime = 0
    self.LastPosition = Vector3.new()
    self.LastRotation = CFrame.new()
    self.LastEnvironmentEffect = 0
    
    -- Effects tracking
    self.TrapActive = false
    self.SevereTrapActive = false
    
    -- Connect events
    self:connectEvents()
    
    print("StillnessTrapController initialized for player:", player.Name)
    return self
end

function StillnessTrapController:connectEvents()
    -- Check stillness every heartbeat
    RunService.Heartbeat:Connect(function(dt)
        self:updateStillness(dt)
    end)
end

function StillnessTrapController:updateStillness(dt)
    local character = self.Player.Character
    if not character then return end
    
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end
    
    local currentPos = hrp.Position
    local currentRot = hrp.CFrame
    
    -- Check if player has moved significantly
    local positionDelta = (currentPos - self.LastPosition).Magnitude
    local rotationDelta = (currentRot.LookVector - self.LastRotation.LookVector).Magnitude
    
    local isMoving = positionDelta > STILLNESS_CONFIG.stillnessThreshold or 
                    rotationDelta > STILLNESS_CONFIG.stillnessThreshold
    
    if isMoving then
        -- Player moved, reset stillness tracking
        if self.IsStill then
            self:onPlayerMoved()
        end
        self.IsStill = false
        self.StillnessStartTime = 0
        self.TotalStillnessTime = 0
        self.TrapActive = false
        self.SevereTrapActive = false
    else
        -- Player is still
        if not self.IsStill then
            self:onPlayerBecameStill()
        end
        self.IsStill = true
        self:updateStillnessEffects(dt)
    end
    
    -- Update last position/rotation
    self.LastPosition = currentPos
    self.LastRotation = currentRot
end

function StillnessTrapController:onPlayerBecameStill()
    print(self.Player.Name, "became still - trap countdown started")
    self.StillnessStartTime = tick()
end

function StillnessTrapController:onPlayerMoved()
    print(self.Player.Name, "moved - stillness trap reset")
    
    -- Send client effect to clear stillness effects
    remote:FireClient(self.Player, "stillness_end")
    
    -- Reset memory field growth multiplier
    if self.MemoryField.setGrowthMultiplier then
        self.MemoryField:setGrowthMultiplier(1.0)
    end
end

function StillnessTrapController:updateStillnessEffects(dt)
    local now = tick()
    local stillnessDuration = now - self.StillnessStartTime
    self.TotalStillnessTime = self.TotalStillnessTime + dt
    
    -- Check if trap should activate
    if stillnessDuration >= STILLNESS_CONFIG.stillnessTimeThreshold and not self.TrapActive then
        self:activateTrap()
    end
    
    -- Check for severe effects
    if stillnessDuration >= STILLNESS_CONFIG.severeStillnessTime and not self.SevereTrapActive then
        self:activateSevereEffects()
    end
    
    -- Apply ongoing effects
    if self.TrapActive then
        self:applyTrapEffects(dt)
    end
    
    -- Periodic environment effects
    if self.TrapActive and now - self.LastEnvironmentEffect >= STILLNESS_CONFIG.environmentUpdateInterval then
        self:triggerEnvironmentEffect()
        self.LastEnvironmentEffect = now
    end
end

function StillnessTrapController:activateTrap()
    print(self.Player.Name, "stillness trap ACTIVATED")
    self.TrapActive = true
    
    -- Send client effect
    remote:FireClient(self.Player, "stillness_trap_activate")
    
    -- Apply memory field growth multiplier
    if self.MemoryField.setGrowthMultiplier then
        self.MemoryField:setGrowthMultiplier(STILLNESS_CONFIG.memoryMultiplier)
    end
end

function StillnessTrapController:activateSevereEffects()
    print(self.Player.Name, "severe stillness effects ACTIVATED - silence begins")
    self.SevereTrapActive = true
    
    -- Send client effect for silence
    remote:FireClient(self.Player, "stillness_silence")
end

function StillnessTrapController:applyTrapEffects(dt)
    -- Effect 1: Memory field increases 3x faster at current position
    -- This is handled by the growth multiplier set in activateTrap()
    
    -- Additional memory field boost at current position
    if self.MemoryField.addMemoryAtPosition then
        local character = self.Player.Character
        if character and character:FindFirstChild("HumanoidRootPart") then
            local pos = character.HumanoidRootPart.Position
            -- Add extra memory at current position
            self.MemoryField:addMemoryAtPosition(pos, dt * STILLNESS_CONFIG.memoryMultiplier)
        end
    end
end

function StillnessTrapController:triggerEnvironmentEffect()
    print(self.Player.Name, "environment closing in due to stillness")
    
    -- Send client effect for environment changes
    remote:FireClient(self.Player, "stillness_environment_close")
    
    -- Create subtle environmental changes in the world
    self:createEnvironmentalEffects()
end

function StillnessTrapController:createEnvironmentalEffects()
    local character = self.Player.Character
    if not character then return end
    
    local playerPos = character.HumanoidRootPart.Position
    
    -- Create shadow extensions
    self:createShadowExtensions(playerPos)
    
    -- Create wall shifting effects
    self:createWallShifts(playerPos)
end

function StillnessTrapController:createShadowExtensions(playerPos)
    -- Create temporary shadow parts around the player
    for i = 1, 3 do
        local shadow = Instance.new("Part")
        shadow.Size = Vector3.new(8, 0.1, 8)
        shadow.BrickColor = BrickColor.new("Really black")
        shadow.Material = Enum.Material.Neon
        shadow.Transparency = 0.7
        shadow.Anchored = true
        shadow.CanCollide = false
        
        -- Position shadows around player
        local angle = (i / 3) * math.pi * 2
        local offset = Vector3.new(math.cos(angle) * 10, 0, math.sin(angle) * 10)
        shadow.Position = playerPos + offset
        
        shadow.Parent = workspace
        
        -- Fade out and remove
        local tween = game:GetService("TweenService"):Create(
            shadow,
            TweenInfo.new(3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
            {Transparency = 1}
        )
        tween:Play()
        
        Debris:AddItem(shadow, 3)
    end
end

function StillnessTrapController:createWallShifts(playerPos)
    -- Find nearby walls and create subtle shifting effects
    -- GetPartsInPart is not available in this context; fall back to safe distance-based query.
    local nearbyParts = {}
    for _, part in ipairs(workspace:GetDescendants()) do
        if part and part:IsA and part:IsA("BasePart") then
            -- protect against parts without position (rare)
            local ok, pos = pcall(function() return part.Position end)
            if ok and pos and (pos - playerPos).Magnitude <= 20 then
                table.insert(nearbyParts, part)
            end
        end
    end

    for _, part in ipairs(nearbyParts) do
        -- Skip obviously decorative sanctuary parts
        if part:IsA("BasePart") and part.BrickColor ~= BrickColor.new("Bright blue") then
            -- Create a temporary visual shift
            local originalPos = part.Position

            -- Subtle position shift
            local shift = Vector3.new(
                math.random(-0.5, 0.5),
                0,
                math.random(-0.5, 0.5)
            )

            part.Position = originalPos + shift

            -- Restore after delay (non-blocking)
            spawn(function()
                task.wait(0.1)
                -- protect in case part was destroyed
                if part and part.Parent then
                    pcall(function() part.Position = originalPos end)
                end
            end)
        end
    end
end

function StillnessTrapController:destroy()
    -- Clean up when player leaves
    print("StillnessTrapController destroyed for player:", self.Player.Name)
end

return StillnessTrapController
