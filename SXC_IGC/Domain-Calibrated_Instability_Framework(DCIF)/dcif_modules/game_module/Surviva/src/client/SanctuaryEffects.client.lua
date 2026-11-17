--[[
    SanctuaryEffects.client.lua
    Client-side visual and audio effects for sanctuary zones
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

local SanctuaryEffects = {}
SanctuaryEffects.__index = SanctuaryEffects

-- Effect parameters
local EFFECT_CONFIG = {
    vignetteMaxIntensity = 0.8,
    edgeDarkeningMax = 0.5,
    calmTransitionTime = 1.0,
    heartbeatFadeTime = 0.5,
    ambientVolumeNormal = 0.3,
    ambientVolumeCalm = 0.1
}

-- UI elements
local ScreenGui = nil
local Vignette = nil
local EdgeOverlay = nil

function SanctuaryEffects.new()
    local self = setmetatable({}, SanctuaryEffects)
    
    self.IsInSanctuary = false
    self.CurrentTension = 0
    self.CurrentState = "IDLE"
    self.DecayRate = 1.0
    
    -- Create UI elements
    self:createUI()
    
    -- Connect remote events
    self:connectEvents()
    
    print("SanctuaryEffects initialized")
    return self
end

function SanctuaryEffects:createUI()
    ScreenGui = Instance.new("ScreenGui")
    ScreenGui.Name = "SanctuaryEffects"
    ScreenGui.Parent = PlayerGui
    ScreenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    
    -- Create vignette effect (darkened edges)
    Vignette = Instance.new("Frame")
    Vignette.Name = "Vignette"
    Vignette.Size = UDim2.new(1, 0, 1, 0)
    Vignette.Position = UDim2.new(0, 0, 0, 0)
    Vignette.BackgroundColor3 = Color3.new(0, 0, 0)
    Vignette.BackgroundTransparency = 1.0
    Vignette.BorderSizePixel = 0
    Vignette.Parent = ScreenGui
    
    -- Create gradient for vignette
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
    
    -- Create edge overlay for additional darkening
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

function SanctuaryEffects:connectEvents()
    remote.OnClientEvent:Connect(function(eventName, ...)
        if eventName == "sanctuary_enter" then
            self:onEnterSanctuary()
        elseif eventName == "sanctuary_exit" then
            self:onExitSanctuary()
        elseif eventName == "sanctuary_update" then
            local data = ...
            self:onSanctuaryUpdate(data)
        end
    end)
end

function SanctuaryEffects:onEnterSanctuary()
    print("Player entered sanctuary - applying calm effects")
    self.IsInSanctuary = true
    
    -- Apply immediate calming effects
    self:applyCalmEffects()
    
    -- Modify ambient audio
    self:setAmbientAudioLevel(EFFECT_CONFIG.ambientVolumeCalm)
end

function SanctuaryEffects:onExitSanctuary()
    print("Player exited sanctuary - removing calm effects")
    self.IsInSanctuary = false
    
    -- Remove calming effects
    self:removeCalmEffects()
    
    -- Restore ambient audio
    self:setAmbientAudioLevel(EFFECT_CONFIG.ambientVolumeNormal)
end

function SanctuaryEffects:onSanctuaryUpdate(data)
    self.IsInSanctuary = data.inSanctuary
    self.CurrentTension = data.tension
    self.CurrentState = data.state
    self.DecayRate = data.decayRate
    
    -- Update effects based on current state
    if self.IsInSanctuary then
        self:updateSanctuaryEffects()
    end
end

function SanctuaryEffects:applyCalmEffects()
    -- Reduce vignette intensity
    local targetTransparency = 1.0 - (EFFECT_CONFIG.vignetteMaxIntensity * 0.3) -- Calmer in sanctuary
    
    local vignetteTween = TweenService:Create(
        Vignette,
        TweenInfo.new(EFFECT_CONFIG.calmTransitionTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {BackgroundTransparency = targetTransparency}
    )
    vignetteTween:Play()
    
    -- Reduce edge darkening
    local edgeTargetTransparency = 1.0 - (EFFECT_CONFIG.edgeDarkeningMax * 0.2)
    
    local edgeTween = TweenService:Create(
        EdgeOverlay,
        TweenInfo.new(EFFECT_CONFIG.calmTransitionTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {BackgroundTransparency = edgeTargetTransparency}
    )
    edgeTween:Play()
    
    -- Apply color correction for calm feeling
    self:applyCalmColorCorrection()
end

function SanctuaryEffects:removeCalmEffects()
    -- Restore normal vignette based on tension
    local targetTransparency = 1.0 - (EFFECT_CONFIG.vignetteMaxIntensity * self.CurrentTension)
    
    local vignetteTween = TweenService:Create(
        Vignette,
        TweenInfo.new(EFFECT_CONFIG.calmTransitionTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {BackgroundTransparency = targetTransparency}
    )
    vignetteTween:Play()
    
    -- Restore normal edge darkening
    local edgeTargetTransparency = 1.0 - (EFFECT_CONFIG.edgeDarkeningMax * self.CurrentTension)
    
    local edgeTween = TweenService:Create(
        EdgeOverlay,
        TweenInfo.new(EFFECT_CONFIG.calmTransitionTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {BackgroundTransparency = edgeTargetTransparency}
    )
    edgeTween:Play()
    
    -- Remove calm color correction
    self:removeCalmColorCorrection()
end

function SanctuaryEffects:updateSanctuaryEffects()
    -- Update effects based on tension and decay rate
    local calmFactor = self.DecayRate / 2.0 -- Normalize decay rate
    local tensionFactor = self.CurrentTension * (1 - calmFactor * 0.5) -- Reduce tension effect in sanctuary
    
    -- Update vignette
    local vignetteTransparency = 1.0 - (EFFECT_CONFIG.vignetteMaxIntensity * tensionFactor)
    Vignette.BackgroundTransparency = vignetteTransparency
    
    -- Update edge darkening
    local edgeTransparency = 1.0 - (EFFECT_CONFIG.edgeDarkeningMax * tensionFactor)
    EdgeOverlay.BackgroundTransparency = edgeTransparency
end

function SanctuaryEffects:applyCalmColorCorrection()
    local colorCorrection = Instance.new("ColorCorrectionEffect")
    colorCorrection.Name = "SanctuaryCalmEffect"
    colorCorrection.Parent = game:GetService("Lighting")
    
    -- Create a warm, calm color tone
    colorCorrection.TintColor = Color3.new(1.1, 1.05, 0.95)
    colorCorrection.Saturation = 0.1
    colorCorrection.Contrast = 0.95
    
    -- Animate the effect
    local tween = TweenService:Create(
        colorCorrection,
        TweenInfo.new(EFFECT_CONFIG.calmTransitionTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {
            TintColor = Color3.new(1.05, 1.02, 0.98),
            Saturation = 0.05,
            Contrast = 0.98
        }
    )
    tween:Play()
end

function SanctuaryEffects:removeCalmColorCorrection()
    local colorCorrection = Lighting:FindFirstChild("SanctuaryCalmEffect")
    if colorCorrection then
        local tween = TweenService:Create(
            colorCorrection,
            TweenInfo.new(EFFECT_CONFIG.calmTransitionTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
            {
                TintColor = Color3.new(1, 1, 1),
                Saturation = 0,
                Contrast = 1
            }
        )
        tween:Play()
        
        tween.Completed:Connect(function()
            colorCorrection:Destroy()
        end)
    end
end

function SanctuaryEffects:setAmbientAudioLevel(volume)
    -- Modify ambient sound volume
    local ambientSound = SoundService:FindFirstChild("Ambient")
    if ambientSound and ambientSound:IsA("Sound") then
        local tween = TweenService:Create(
            ambientSound,
            TweenInfo.new(EFFECT_CONFIG.heartbeatFadeTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
            {Volume = volume}
        )
        tween:Play()
    end
end

function SanctuaryEffects:destroy()
    -- Clean up UI elements
    if ScreenGui then
        ScreenGui:Destroy()
    end
    
    -- Remove color correction
    self:removeCalmColorCorrection()
    
    print("SanctuaryEffects destroyed")
end

return SanctuaryEffects
