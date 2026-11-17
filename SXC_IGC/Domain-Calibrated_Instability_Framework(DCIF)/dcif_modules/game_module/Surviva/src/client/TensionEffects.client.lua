--[[
    TensionEffects.client.lua
    Phase 3 Critical Task: Visual/Audio Link
    
    Maps T_sys to:
    - Screen vignette intensity (0 to 0.8)
    - Edge darkening (0 to 0.5)
    - Heartbeat sound (starts at T>0.6, volume = T_sys)
    - Ambient audio intensity (calm → tense → critical loops)
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

local TensionEffects = {}
TensionEffects.__index = TensionEffects

-- Effect parameters
local EFFECT_CONFIG = {
    vignetteMaxIntensity = 0.8,
    edgeDarkeningMax = 0.5,
    heartbeatThreshold = 0.6,
    heartbeatMaxVolume = 1.0,
    ambientCalmVolume = 0.1,
    ambientTenseVolume = 0.4,
    ambientCriticalVolume = 0.8,
    transitionTime = 1.0
}

-- Current state
local CurrentTension = 0
local CurrentState = "IDLE"
local HeartbeatSound = nil
local AmbientSound = nil

-- UI elements
local ScreenGui = nil
local Vignette = nil
local EdgeOverlay = nil

function TensionEffects.new()
    local self = setmetatable({}, TensionEffects)
    
    -- Create UI elements
    self:createUI()
    
    -- Initialize audio
    self:initializeAudio()
    
    -- Connect remote events
    self:connectEvents()
    
    print("TensionEffects initialized")
    return self
end

function TensionEffects:createUI()
    ScreenGui = Instance.new("ScreenGui")
    ScreenGui.Name = "TensionEffects"
    ScreenGui.Parent = PlayerGui
    ScreenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    
    -- Create vignette effect
    Vignette = Instance.new("Frame")
    Vignette.Name = "Vignette"
    Vignette.Size = UDim2.new(1, 0, 1, 0)
    Vignette.Position = UDim2.new(0, 0, 0, 0)
    Vignette.BackgroundColor3 = Color3.new(0, 0, 0)
    Vignette.BackgroundTransparency = 1.0
    Vignette.BorderSizePixel = 0
    Vignette.Parent = ScreenGui
    
    -- Create vignette gradient
    local vignetteGradient = Instance.new("UIGradient")
    vignetteGradient.Color = ColorSequence.new{
        ColorSequenceKeypoint.new(0, Color3.new(0, 0, 0)),
        ColorSequenceKeypoint.new(0.7, Color3.new(0, 0, 0)),
        ColorSequenceKeypoint.new(1, Color3.new(0, 0, 0))
    }
    vignetteGradient.Transparency = NumberSequence.new{
        NumberSequenceKeypoint.new(0, 1),
        NumberSequenceKeypoint.new(0.7, 0.8),
        NumberSequenceKeypoint.new(1, 0)
    }
    vignetteGradient.Rotation = 45
    vignetteGradient.Parent = Vignette
    
    -- Create edge overlay
    EdgeOverlay = Instance.new("Frame")
    EdgeOverlay.Name = "EdgeOverlay"
    EdgeOverlay.Size = UDim2.new(1, 0, 1, 0)
    EdgeOverlay.Position = UDim2.new(0, 0, 0, 0)
    EdgeOverlay.BackgroundColor3 = Color3.new(0, 0, 0)
    EdgeOverlay.BackgroundTransparency = 1.0
    EdgeOverlay.BorderSizePixel = 0
    EdgeOverlay.Parent = ScreenGui
    
    -- Create edge gradient
    local edgeGradient = Instance.new("UIGradient")
    edgeGradient.Color = ColorSequence.new{
        ColorSequenceKeypoint.new(0, Color3.new(0, 0, 0)),
        ColorSequenceKeypoint.new(0.5, Color3.new(0, 0, 0)),
        ColorSequenceKeypoint.new(1, Color3.new(0, 0, 0))
    }
    edgeGradient.Transparency = NumberSequence.new{
        NumberSequenceKeypoint.new(0, 1),
        NumberSequenceKeypoint.new(0.5, 1),
        NumberSequenceKeypoint.new(1, 0.5)
    }
    edgeGradient.Parent = EdgeOverlay
end

function TensionEffects:initializeAudio()
    -- Create heartbeat sound
    HeartbeatSound = Instance.new("Sound")
    HeartbeatSound.Name = "TensionHeartbeat"
    HeartbeatSound.SoundId = "rbxassetid://9127608562"
    HeartbeatSound.Volume = 0
    HeartbeatSound.Looped = true
    HeartbeatSound.Parent = workspace.CurrentCamera
    HeartbeatSound:Play()
    
    -- Find ambient sound
    AmbientSound = SoundService:FindFirstChild("Ambient")
    if not AmbientSound then
        AmbientSound = Instance.new("Sound")
        AmbientSound.Name = "Ambient"
        AmbientSound.SoundId = "rbxassetid://9127599111"
        AmbientSound.Volume = EFFECT_CONFIG.ambientCalmVolume
        AmbientSound.Looped = true
        AmbientSound.Parent = SoundService
        AmbientSound:Play()
    end
end

function TensionEffects:connectEvents()
    remote.OnClientEvent:Connect(function(eventName, ...)
        if eventName == "tension_update" then
            local data = ...
            self:onTensionUpdate(data)
        end
    end)
end

function TensionEffects:onTensionUpdate(data)
    CurrentTension = data.tension or 0
    CurrentState = data.state or "IDLE"
    
    -- Update all effects
    self:updateVisualEffects()
    self:updateAudioEffects()
end

function TensionEffects:updateVisualEffects()
    -- Calculate effect intensities based on tension
    local vignetteIntensity = math.clamp(CurrentTension / 1.5, 0, EFFECT_CONFIG.vignetteMaxIntensity)
    local edgeIntensity = math.clamp(CurrentTension / 1.5, 0, EFFECT_CONFIG.edgeDarkeningMax)
    
    -- Update vignette
    if Vignette then
        local vignetteTargetTransparency = 1.0 - vignetteIntensity
        local vignetteTween = TweenService:Create(
            Vignette,
            TweenInfo.new(EFFECT_CONFIG.transitionTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
            {BackgroundTransparency = vignetteTargetTransparency}
        )
        vignetteTween:Play()
    end
    
    -- Update edge darkening
    if EdgeOverlay then
        local edgeTargetTransparency = 1.0 - edgeIntensity
        local edgeTween = TweenService:Create(
            EdgeOverlay,
            TweenInfo.new(EFFECT_CONFIG.transitionTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
            {BackgroundTransparency = edgeTargetTransparency}
        )
        edgeTween:Play()
    end
    
    -- Add color correction based on tension
    self:updateColorCorrection()
end

function TensionEffects:updateColorCorrection()
    -- Remove existing color correction
    local existingCorrection = Lighting:FindFirstChild("TensionColorCorrection")
    if existingCorrection then
        existingCorrection:Destroy()
    end
    
    -- Create new color correction based on tension
    local colorCorrection = Instance.new("ColorCorrectionEffect")
    colorCorrection.Name = "TensionColorCorrection"
    colorCorrection.Parent = Lighting
    
    -- Adjust based on tension
    if CurrentTension < 0.4 then
        -- Calm: slight warm tint
        colorCorrection.TintColor = Color3.new(1.05, 1.02, 0.98)
        colorCorrection.Saturation = 0.05
        colorCorrection.Contrast = 0.98
    elseif CurrentTension < 0.9 then
        -- Tense: slight desaturation
        colorCorrection.TintColor = Color3.new(0.95, 0.92, 0.9)
        colorCorrection.Saturation = -0.1
        colorCorrection.Contrast = 1.02
    else
        -- Critical: red tint and high contrast
        colorCorrection.TintColor = Color3.new(1.1, 0.8, 0.8)
        colorCorrection.Saturation = -0.2
        colorCorrection.Contrast = 1.1
    end
end

function TensionEffects:updateAudioEffects()
    -- Update heartbeat sound
    if HeartbeatSound then
        local targetVolume = 0
        
        if CurrentTension >= EFFECT_CONFIG.heartbeatThreshold then
            -- Heartbeat volume based on tension above threshold
            local tensionAboveThreshold = CurrentTension - EFFECT_CONFIG.heartbeatThreshold
            local normalizedTension = tensionAboveThreshold / (1.5 - EFFECT_CONFIG.heartbeatThreshold)
            targetVolume = normalizedTension * EFFECT_CONFIG.heartbeatMaxVolume
        end
        
        local heartbeatTween = TweenService:Create(
            HeartbeatSound,
            TweenInfo.new(EFFECT_CONFIG.transitionTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
            {Volume = targetVolume}
        )
        heartbeatTween:Play()
    end
    
    -- Update ambient sound
    if AmbientSound then
        local targetVolume = EFFECT_CONFIG.ambientCalmVolume
        
        if CurrentTension < 0.4 then
            targetVolume = EFFECT_CONFIG.ambientCalmVolume
        elseif CurrentTension < 0.9 then
            targetVolume = EFFECT_CONFIG.ambientTenseVolume
        else
            targetVolume = EFFECT_CONFIG.ambientCriticalVolume
        end
        
        local ambientTween = TweenService:Create(
            AmbientSound,
            TweenInfo.new(EFFECT_CONFIG.transitionTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
            {Volume = targetVolume}
        )
        ambientTween:Play()
        
        -- Change ambient sound based on tension
        self:updateAmbientSoundType()
    end
end

function TensionEffects:updateAmbientSoundType()
    if not AmbientSound then return end
    
    local soundId = "rbxassetid://9127599111" -- Default calm sound
    
    if CurrentTension < 0.4 then
        soundId = "rbxassetid://9127599111" -- Calm ambient
    elseif CurrentTension < 0.9 then
        soundId = "rbxassetid://9127608562" -- Tense ambient
    else
        soundId = "rbxassetid://131961136" -- Critical ambient (low frequency)
    end
    
    if AmbientSound.SoundId ~= soundId then
        -- Fade out current sound
        local fadeOut = TweenService:Create(
            AmbientSound,
            TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
            {Volume = 0}
        )
        fadeOut:Play()
        
        fadeOut.Completed:Connect(function()
            AmbientSound.SoundId = soundId
            
            -- Fade back in
            local fadeIn = TweenService:Create(
                AmbientSound,
                TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
                {Volume = self:getAmbientTargetVolume()}
            )
            fadeIn:Play()
        end)
    end
end

function TensionEffects:getAmbientTargetVolume()
    if CurrentTension < 0.4 then
        return EFFECT_CONFIG.ambientCalmVolume
    elseif CurrentTension < 0.9 then
        return EFFECT_CONFIG.ambientTenseVolume
    else
        return EFFECT_CONFIG.ambientCriticalVolume
    end
end

function TensionEffects:destroy()
    -- Clean up UI elements
    if ScreenGui then
        ScreenGui:Destroy()
    end
    
    -- Stop and remove sounds
    if HeartbeatSound then
        HeartbeatSound:Stop()
        HeartbeatSound:Destroy()
    end
    
    -- Remove color correction
    local colorCorrection = Lighting:FindFirstChild("TensionColorCorrection")
    if colorCorrection then
        colorCorrection:Destroy()
    end
    
    print("TensionEffects destroyed")
end

return TensionEffects
