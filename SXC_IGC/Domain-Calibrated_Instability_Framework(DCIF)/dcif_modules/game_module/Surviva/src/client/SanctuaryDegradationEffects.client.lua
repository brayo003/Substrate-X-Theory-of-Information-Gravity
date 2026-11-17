--[[
    SanctuaryDegradationEffects.client.lua
    Client-side effects for sanctuary degradation
    
    - Lights flicker after 2 minutes
    - Shadows move after 5 minutes
    - Circling stalker appears
    - Memory field increases visibly
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local Lighting = game:GetService("Lighting")
local SoundService = game:GetService("SoundService")
local RunService = game:GetService("RunService")

local Player = Players.LocalPlayer
local PlayerGui = Player:WaitForChild("PlayerGui")

-- Remote events
local remote = ReplicatedStorage:WaitForChild("V12_Sync")

local SanctuaryDegradationEffects = {}
SanctuaryDegradationEffects.__index = SanctuaryDegradationEffects

-- Effect parameters
local EFFECT_CONFIG = {
    flickerFlashIntensity = 0.7,
    flickerDuration = 0.5,
    shadowMoveDistance = 3,
    shadowMoveDuration = 2,
    memoryIncreaseVisualDuration = 1.0,
    circlingStalkerTransparency = 0.6,
    circlingSoundVolume = 0.4
}

-- State tracking
local FlickeringActive = false
local StalkerCircling = false
local CirclingStalker = nil
local DegradationUI = nil

function SanctuaryDegradationEffects.new()
    local self = setmetatable({}, SanctuaryDegradationEffects)
    
    -- Create degradation UI
    self:createDegradationUI()
    
    -- Connect remote events
    self:connectEvents()
    
    print("SanctuaryDegradationEffects initialized")
    return self
end

function SanctuaryDegradationEffects:createDegradationUI()
    DegradationUI = Instance.new("ScreenGui")
    DegradationUI.Name = "SanctuaryDegradationEffects"
    DegradationUI.Parent = PlayerGui
    DegradationUI.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    
    -- Create memory increase indicator
    local memoryIndicator = Instance.new("Frame")
    memoryIndicator.Name = "MemoryIncreaseIndicator"
    memoryIndicator.Size = UDim2.new(0, 200, 0, 4)
    memoryIndicator.Position = UDim2.new(0.5, -100, 0.95, -10)
    memoryIndicator.BackgroundColor3 = Color3.new(0.5, 0, 0.5)
    memoryIndicator.BackgroundTransparency = 1.0
    memoryIndicator.BorderSizePixel = 0
    memoryIndicator.Parent = DegradationUI
    
    -- Create flicker overlay
    local flickerOverlay = Instance.new("Frame")
    flickerOverlay.Name = "FlickerOverlay"
    flickerOverlay.Size = UDim2.new(1, 0, 1, 0)
    flickerOverlay.Position = UDim2.new(0, 0, 0, 0)
    flickerOverlay.BackgroundColor3 = Color3.new(1, 1, 1)
    flickerOverlay.BackgroundTransparency = 1.0
    flickerOverlay.BorderSizePixel = 0
    flickerOverlay.Parent = DegradationUI
end

function SanctuaryDegradationEffects:connectEvents()
    remote.OnClientEvent:Connect(function(eventName, ...)
        if eventName == "sanctuary_flickering_start" then
            self:onFlickeringStart()
        elseif eventName == "sanctuary_flicker" then
            self:onFlicker()
        elseif eventName == "sanctuary_shadow_move" then
            self:onShadowMove()
        elseif eventName == "sanctuary_stalker_circle" then
            self:onStalkerCircle()
        elseif eventName == "circling_stalker_spawn" then
            local data = ...
            self:onCirclingStalkerSpawn(data)
        elseif eventName == "sanctuary_degradation_reset" then
            self:onDegradationReset()
        end
    end)
end

function SanctuaryDegradationEffects:onFlickeringStart()
    print("Sanctuary flickering started")
    FlickeringActive = true
    
    -- Show flickering indicator
    self:showFlickeringIndicator()
end

function SanctuaryDegradationEffects:onFlicker()
    if not FlickeringActive then return end
    
    -- Create flicker effect
    self:createFlickerEffect()
    
    -- Play flicker sound
    self:playFlickerSound()
end

function SanctuaryDegradationEffects:createFlickerEffect()
    if not DegradationUI then return end
    
    local flickerOverlay = DegradationUI:FindFirstChild("FlickerOverlay")
    if not flickerOverlay then return end
    
    -- Quick white flash
    local flashTween = TweenService:Create(
        flickerOverlay,
        TweenInfo.new(EFFECT_CONFIG.flickerDuration / 2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {BackgroundTransparency = 1 - EFFECT_CONFIG.flickerFlashIntensity}
    )
    flashTween:Play()
    
    flashTween.Completed:Connect(function()
        local fadeTween = TweenService:Create(
            flickerOverlay,
            TweenInfo.new(EFFECT_CONFIG.flickerDuration / 2, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
            {BackgroundTransparency = 1.0}
        )
        fadeTween:Play()
    end)
end

function SanctuaryDegradationEffects:playFlickerSound()
    -- Create flicker sound
    local flickerSound = Instance.new("Sound")
    flickerSound.Name = "SanctuaryFlickerSound"
    flickerSound.SoundId = "rbxassetid://9127599111" -- Quick static sound
    flickerSound.Volume = 0.3
    flickerSound.Parent = workspace.CurrentCamera
    flickerSound:Play()
    
    -- Remove after playing
    game:GetService("Debris"):AddItem(flickerSound, 1)
end

function SanctuaryDegradationEffects:onShadowMove()
    print("Sanctuary shadow movement")
    
    -- Create shadow movement effect
    self:createShadowMovementEffect()
    
    -- Play shadow sound
    self:playShadowSound()
end

function SanctuaryDegradationEffects:createShadowMovementEffect()
    -- Create screen-space shadow effect
    local shadowEffect = Instance.new("Frame")
    shadowEffect.Name = "ShadowMovementEffect"
    shadowEffect.Size = UDim2.new(1, 0, 1, 0)
    shadowEffect.Position = UDim2.new(0, 0, 0, 0)
    shadowEffect.BackgroundColor3 = Color3.new(0, 0, 0)
    shadowEffect.BackgroundTransparency = 0.8
    shadowEffect.BorderSizePixel = 0
    shadowEffect.Parent = DegradationUI
    
    -- Animate shadow movement
    local moveTween = TweenService:Create(
        shadowEffect,
        TweenInfo.new(EFFECT_CONFIG.shadowMoveDuration, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut),
        {BackgroundTransparency = 0.9}
    )
    moveTween:Play()
    
    moveTween.Completed:Connect(function()
        shadowEffect:Destroy()
    end)
end

function SanctuaryDegradationEffects:playShadowSound()
    -- Create shadow movement sound
    local shadowSound = Instance.new("Sound")
    shadowSound.Name = "SanctuaryShadowSound"
    shadowSound.SoundId = "rbxassetid://9127608562" -- Low ominous sound
    shadowSound.Volume = 0.2
    shadowSound.Parent = workspace.CurrentCamera
    shadowSound:Play()
    
    -- Remove after playing
    game:GetService("Debris"):AddItem(shadowSound, 2)
end

function SanctuaryDegradationEffects:onStalkerCircle()
    print("Stalker circling sanctuary")
    StalkerCircling = true
    
    -- Show circling indicator
    self:showCirclingIndicator()
end

function SanctuaryDegradationEffects:onCirclingStalkerSpawn(data)
    local position = data.position
    local stalkerId = data.stalkerId
    
    print("Circling stalker spawned at", position)
    
    -- Create client-side circling stalker visual
    self:createCirclingStalkerVisual(position, stalkerId)
end

function SanctuaryDegradationEffects:createCirclingStalkerVisual(position, stalkerId)
    -- Create a semi-transparent stalker visual
    local stalkerVisual = Instance.new("Part")
    stalkerVisual.Name = "CirclingStalkerVisual_" .. stalkerId
    stalkerVisual.Size = Vector3.new(4, 6, 2)
    stalkerVisual.BrickColor = BrickColor.new("Really black")
    stalkerVisual.Material = Enum.Material.Neon
    stalkerVisual.Transparency = EFFECT_CONFIG.circlingStalkerTransparency
    stalkerVisual.Anchored = true
    stalkerVisual.CanCollide = false
    stalkerVisual.Position = position
    stalkerVisual.Parent = workspace
    
    -- Add subtle glow
    local glow = Instance.new("PointLight")
    glow.Color = Color3.new(0.8, 0, 0)
    glow.Brightness = 1
    glow.Range = 8
    glow.Parent = stalkerVisual
    
    -- Add sound
    local sound = Instance.new("Sound")
    sound.SoundId = "rbxassetid://9127608562"
    sound.Volume = EFFECT_CONFIG.circlingSoundVolume
    sound.Looped = true
    sound.Parent = stalkerVisual
    sound:Play()
    
    -- Store reference
    CirclingStalker = stalkerVisual
    
    -- Start circling animation on client
    self:startClientCirclingAnimation(stalkerVisual)
end

function SanctuaryDegradationEffects:startClientCirclingAnimation(stalkerVisual)
    if not stalkerVisual then return end
    
    local character = Player.Character
    if not character then return end
    
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end
    
    local centerPos = hrp.Position
    local radius = 15
    local speed = 0.5 -- radians per second
    
    local startTime = tick()
    
    local connection
    connection = RunService.Heartbeat:Connect(function(dt)
        if not stalkerVisual.Parent then
            connection:Disconnect()
            return
        end
        
        -- Update center position to follow player
        centerPos = hrp.Position
        
        local elapsed = tick() - startTime
        local angle = elapsed * speed
        
        -- Update position in circle
        local newPos = centerPos + Vector3.new(
            math.cos(angle) * radius,
            0,
            math.sin(angle) * radius
        )
        
        stalkerVisual.Position = newPos
    end)
end

function SanctuaryDegradationEffects:onDegradationReset()
    print("Sanctuary degradation reset")
    
    FlickeringActive = false
    StalkerCircling = false
    
    -- Remove circling stalker
    if CirclingStalker then
        CirclingStalker:Destroy()
        CirclingStalker = nil
    end
    
    -- Hide indicators
    self:hideFlickeringIndicator()
    self:hideCirclingIndicator()
end

function SanctuaryDegradationEffects:showFlickeringIndicator()
    -- Create flickering warning indicator
    local indicator = Instance.new("TextLabel")
    indicator.Name = "FlickeringIndicator"
    indicator.Size = UDim2.new(0, 150, 0, 25)
    indicator.Position = UDim2.new(0.05, 0, 0.15, 0)
    indicator.BackgroundColor3 = Color3.new(0.5, 0, 0)
    indicator.BackgroundTransparency = 0.7
    indicator.Text = "SANCTUARY WEAKENING"
    indicator.TextColor3 = Color3.new(1, 0.5, 0.5)
    indicator.TextScaled = true
    indicator.Font = Enum.Font.SourceSansBold
    indicator.Parent = DegradationUI
    
    -- Pulse effect
    local pulseTween = TweenService:Create(
        indicator,
        TweenInfo.new(1.5, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true),
        {BackgroundTransparency = 0.9}
    )
    pulseTween:Play()
end

function SanctuaryDegradationEffects:hideFlickeringIndicator()
    local indicator = DegradationUI:FindFirstChild("FlickeringIndicator")
    if indicator then
        indicator:Destroy()
    end
end

function SanctuaryDegradationEffects:showCirclingIndicator()
    -- Create circling warning indicator
    local indicator = Instance.new("TextLabel")
    indicator.Name = "CirclingIndicator"
    indicator.Size = UDim2.new(0, 180, 0, 25)
    indicator.Position = UDim2.new(0.05, 0, 0.2, 0)
    indicator.BackgroundColor3 = Color3.new(0.5, 0, 0)
    indicator.BackgroundTransparency = 0.7
    indicator.Text = "STALKER CIRCLES OUTSIDE"
    indicator.TextColor3 = Color3.new(1, 0.5, 0.5)
    indicator.TextScaled = true
    indicator.Font = Enum.Font.SourceSansBold
    indicator.Parent = DegradationUI
    
    -- Pulse effect
    local pulseTween = TweenService:Create(
        indicator,
        TweenInfo.new(2, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true),
        {BackgroundTransparency = 0.9}
    )
    pulseTween:Play()
end

function SanctuaryDegradationEffects:hideCirclingIndicator()
    local indicator = DegradationUI:FindFirstChild("CirclingIndicator")
    if indicator then
        indicator:Destroy()
    end
end

function SanctuaryDegradationEffects:destroy()
    -- Clean up UI elements
    if DegradationUI then
        DegradationUI:Destroy()
    end
    
    -- Remove circling stalker
    if CirclingStalker then
        CirclingStalker:Destroy()
    end
    
    print("SanctuaryDegradationEffects destroyed")
end

return SanctuaryDegradationEffects
