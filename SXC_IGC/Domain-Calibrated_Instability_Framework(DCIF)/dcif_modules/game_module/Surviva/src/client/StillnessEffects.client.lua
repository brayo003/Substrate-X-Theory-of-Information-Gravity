--[[
    StillnessEffects.client.lua
    Client-side visual and audio effects for stillness trap
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local Lighting = game:GetService("Lighting")
local SoundService = game:GetService("SoundService")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")

local Player = Players.LocalPlayer
local PlayerGui = Player:WaitForChild("PlayerGui")
local Camera = workspace.CurrentCamera

-- Remote events
local remote = ReplicatedStorage:WaitForChild("V12_Sync")

local StillnessEffects = {}
StillnessEffects.__index = StillnessEffects

-- Effect parameters
local EFFECT_CONFIG = {
    geometryWarpIntensity = 0.3,
    screenDarkenMax = 0.4,
    shadowExtendDuration = 2.0,
    silenceTransitionTime = 3.0,
    wallShiftAmount = 0.2,
    heartbeatInterval = 1.5
}

-- State tracking
local TrapActive = false
local SevereEffectsActive = false
local OriginalAmbientVolume = 0
local OriginalSoundEffects = {}

-- UI elements
local ScreenGui = nil
local DarkeningOverlay = nil
local GeometryWarp = nil

function StillnessEffects.new()
    local self = setmetatable({}, StillnessEffects)
    
    -- Create UI elements
    self:createUI()
    
    -- Store original audio settings
    self:storeOriginalAudioSettings()
    
    -- Connect remote events
    self:connectEvents()
    
    print("StillnessEffects initialized")
    return self
end

function StillnessEffects:createUI()
    ScreenGui = Instance.new("ScreenGui")
    ScreenGui.Name = "StillnessEffects"
    ScreenGui.Parent = PlayerGui
    ScreenGui.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    
    -- Create darkening overlay
    DarkeningOverlay = Instance.new("Frame")
    DarkeningOverlay.Name = "DarkeningOverlay"
    DarkeningOverlay.Size = UDim2.new(1, 0, 1, 0)
    DarkeningOverlay.Position = UDim2.new(0, 0, 0, 0)
    DarkeningOverlay.BackgroundColor3 = Color3.new(0, 0, 0)
    DarkeningOverlay.BackgroundTransparency = 1.0
    DarkeningOverlay.BorderSizePixel = 0
    DarkeningOverlay.Parent = ScreenGui
    
    -- Create geometry warp effect using distortion
    GeometryWarp = Instance.new("Frame")
    GeometryWarp.Name = "GeometryWarp"
    GeometryWarp.Size = UDim2.new(1, 0, 1, 0)
    GeometryWarp.Position = UDim2.new(0, 0, 0, 0)
    GeometryWarp.BackgroundColor3 = Color3.new(0.2, 0, 0.2)
    GeometryWarp.BackgroundTransparency = 1.0
    GeometryWarp.BorderSizePixel = 0
    GeometryWarp.Parent = ScreenGui
end

function StillnessEffects:storeOriginalAudioSettings()
    -- Store original ambient volume
    local ambientSound = SoundService:FindFirstChild("Ambient")
    if ambientSound and ambientSound:IsA("Sound") then
        OriginalAmbientVolume = ambientSound.Volume
    end
    
    -- Store other sound settings
    OriginalSoundEffects = {
        AmbientVolume = SoundService.AmbientVolume,
        MusicVolume = SoundService.MusicVolume,
        SoundEffectVolume = SoundService.SoundEffectVolume
    }
end

function StillnessEffects:connectEvents()
    remote.OnClientEvent:Connect(function(eventName, ...)
        if eventName == "stillness_trap_activate" then
            self:onTrapActivated()
        elseif eventName == "stillness_end" then
            self:onTrapEnded()
        elseif eventName == "stillness_silence" then
            self:onSilenceActivated()
        elseif eventName == "stillness_environment_close" then
            self:onEnvironmentClose()
        end
    end)
end

function StillnessEffects:onTrapActivated()
    print("Stillness trap activated - applying effects")
    TrapActive = true
    
    -- Start visual effects
    self:startGeometryWarping()
    self:startScreenDarkening()
    self:createShadowExtensions()
    
    -- Start audio effects
    self:startStillnessAudio()
end

function StillnessEffects:onTrapEnded()
    print("Stillness trap ended - removing effects")
    TrapActive = false
    SevereEffectsActive = false
    
    -- Remove visual effects
    self:stopGeometryWarping()
    self:stopScreenDarkening()
    
    -- Restore audio
    self:restoreAudio()
end

function StillnessEffects:onSilenceActivated()
    print("Silence effect activated - creating dread")
    SevereEffectsActive = true
    
    -- Create silence effect
    self:createSilence()
    
    -- Intensify visual effects
    self:intensifyVisualEffects()
end

function StillnessEffects:onEnvironmentClose()
    print("Environment closing in - creating environmental effects")
    self:createEnvironmentalEffects()
end

function StillnessEffects:startGeometryWarping()
    -- Subtle geometry warping effect
    local warpTween = TweenService:Create(
        GeometryWarp,
        TweenInfo.new(2, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true),
        {BackgroundTransparency = 1 - EFFECT_CONFIG.geometryWarpIntensity}
    )
    warpTween:Play()
    
    -- Apply screen distortion
    local distortion = Instance.new("DistortionEffect")
    distortion.Name = "StillnessDistortion"
    distortion.Parent = Lighting
    distortion.Distortion = 0.1
    
    local distortionTween = TweenService:Create(
        distortion,
        TweenInfo.new(3, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true),
        {Distortion = 0.2}
    )
    distortionTween:Play()
end

function StillnessEffects:stopGeometryWarping()
    -- Stop geometry warping
    if GeometryWarp then
        GeometryWarp.BackgroundTransparency = 1.0
    end
    
    -- Remove distortion effect
    local distortion = Lighting:FindFirstChild("StillnessDistortion")
    if distortion then
        distortion:Destroy()
    end
end

function StillnessEffects:startScreenDarkening()
    -- Gradual screen darkening at edges
    local targetDarkness = EFFECT_CONFIG.screenDarkenMax
    
    local darkeningTween = TweenService:Create(
        DarkeningOverlay,
        TweenInfo.new(5, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {BackgroundTransparency = 1 - targetDarkness}
    )
    darkeningTween:Play()
end

function StillnessEffects:stopScreenDarkening()
    -- Remove screen darkening
    local darkeningTween = TweenService:Create(
        DarkeningOverlay,
        TweenInfo.new(2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {BackgroundTransparency = 1.0}
    )
    darkeningTween:Play()
end

function StillnessEffects:createShadowExtensions()
    -- Create extending shadow effects
    local shadowEffect = Instance.new("BlurEffect")
    shadowEffect.Name = "StillnessShadowBlur"
    shadowEffect.Parent = Lighting
    shadowEffect.Size = 5
    
    local shadowTween = TweenService:Create(
        shadowEffect,
        TweenInfo.new(EFFECT_CONFIG.shadowExtendDuration, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {Size = 15}
    )
    shadowTween:Play()
    
    -- Extend existing shadows
    Lighting.GlobalShadows = true
    Lighting.ShadowSoftness = math.max(Lighting.ShadowSoftness, 0.5)
end

function StillnessEffects:startStillnessAudio()
    -- Create unsettling heartbeat sound
    local heartbeat = Instance.new("Sound")
    heartbeat.Name = "StillnessHeartbeat"
    heartbeat.SoundId = "rbxassetid://9127608562"
    heartbeat.Volume = 0.3
    heartbeat.Looped = true
    heartbeat.Parent = Camera
    heartbeat:Play()
    
    -- Create low frequency drone
    local drone = Instance.new("Sound")
    drone.Name = "StillnessDrone"
    drone.SoundId = "rbxassetid://131961136" -- Low frequency drone
    drone.Volume = 0.2
    drone.Looped = true
    drone.Parent = Camera
    drone:Play()
end

function StillnessEffects:createSilence()
    -- Create absolute silence by reducing all audio
    local silenceTween = TweenService:Create(
        SoundService,
        TweenInfo.new(EFFECT_CONFIG.silenceTransitionTime, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {
            AmbientVolume = 0,
            MusicVolume = 0,
            SoundEffectVolume = 0.1 -- Keep very low for player sounds
        }
    )
    silenceTween:Play()
    
    -- Stop ambient sounds
    local ambientSound = SoundService:FindFirstChild("Ambient")
    if ambientSound and ambientSound:IsA("Sound") then
        ambientSound.Volume = 0
    end
    
    -- Create visual indicator of silence
    self:createSilenceIndicator()
end

function StillnessEffects:createSilenceIndicator()
    -- Create a subtle visual cue for silence
    local silenceIndicator = Instance.new("TextLabel")
    silenceIndicator.Name = "SilenceIndicator"
    silenceIndicator.Size = UDim2.new(0, 200, 0, 30)
    silenceIndicator.Position = UDim2.new(0.5, -100, 0.1, 0)
    silenceIndicator.BackgroundTransparency = 1
    silenceIndicator.Text = "..."
    silenceIndicator.TextColor3 = Color3.new(0.3, 0.3, 0.3)
    silenceIndicator.TextScaled = true
    silenceIndicator.Font = Enum.Font.SourceSansLight
    silenceIndicator.Parent = ScreenGui
    
    -- Fade in and out
    local fadeIn = TweenService:Create(
        silenceIndicator,
        TweenInfo.new(2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {TextTransparency = 0.3}
    )
    fadeIn:Play()
    
    task.wait(3)
    
    local fadeOut = TweenService:Create(
        silenceIndicator,
        TweenInfo.new(2, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
        {TextTransparency = 1}
    )
    fadeOut:Play()
    
    fadeOut.Completed:Connect(function()
        silenceIndicator:Destroy()
    end)
end

function StillnessEffects:intensifyVisualEffects()
    -- Intensify geometry warping
    if GeometryWarp then
        local intensifyTween = TweenService:Create(
            GeometryWarp,
            TweenInfo.new(3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
            {BackgroundTransparency = 1 - (EFFECT_CONFIG.geometryWarpIntensity * 1.5)}
        )
        intensifyTween:Play()
    end
    
    -- Increase screen darkening
    if DarkeningOverlay then
        local intensifyTween = TweenService:Create(
            DarkeningOverlay,
            TweenInfo.new(3, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
            {BackgroundTransparency = 1 - (EFFECT_CONFIG.screenDarkenMax * 1.2)}
        )
        intensifyTween:Play()
    end
end

function StillnessEffects:createEnvironmentalEffects()
    -- Create wall shifting visual effect
    self:createWallShiftEffect()
    
    -- Create particle effects for dust/debris
    self:createDustParticles()
end

function StillnessEffects:createWallShiftEffect()
    -- Create visual effect of walls shifting
    local shiftOverlay = Instance.new("Frame")
    shiftOverlay.Name = "WallShiftEffect"
    shiftOverlay.Size = UDim2.new(1, 0, 1, 0)
    shiftOverlay.Position = UDim2.new(0, 0, 0, 0)
    shiftOverlay.BackgroundColor3 = Color3.new(0.1, 0.05, 0.05)
    shiftOverlay.BackgroundTransparency = 1
    shiftOverlay.BorderSizePixel = 0
    shiftOverlay.Parent = ScreenGui
    
    -- Quick flash to simulate wall movement
    local flashTween = TweenService:Create(
        shiftOverlay,
        TweenInfo.new(0.1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {BackgroundTransparency = 0.7}
    )
    flashTween:Play()
    
    flashTween.Completed:Connect(function()
        local fadeTween = TweenService:Create(
            shiftOverlay,
            TweenInfo.new(0.5, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
            {BackgroundTransparency = 1}
        )
        fadeTween:Play()
        
        fadeTween.Completed:Connect(function()
            shiftOverlay:Destroy()
        end)
    end)
    
    -- Apply camera shake
    self:applyCameraShake(0.5, 0.3)
end

function StillnessEffects:createDustParticles()
    -- Create dust particle effect
    local character = Player.Character
    if not character then return end
    
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return end
    
    for i = 1, 10 do
        local particle = Instance.new("Part")
        particle.Size = Vector3.new(0.2, 0.2, 0.2)
        particle.BrickColor = BrickColor.new("Brown")
        particle.Material = Enum.Material.Sand
        particle.Anchored = false
        particle.CanCollide = false
        particle.Position = hrp.Position + Vector3.new(math.random(-5, 5), math.random(-2, 2), math.random(-5, 5))
        particle.Parent = workspace
        
        -- Apply slight gravity and random movement
        particle.Velocity = Vector3.new(math.random(-2, 2), -1, math.random(-2, 2))
        
        game:GetService("Debris"):AddItem(particle, 3)
    end
end

function StillnessEffects:applyCameraShake(intensity, duration)
    local originalCFrame = Camera.CFrame
    local elapsed = 0
    
    local connection
    connection = RunService.RenderStepped:Connect(function(dt)
        elapsed = elapsed + dt
        if elapsed >= duration then
            Camera.CFrame = originalCFrame
            connection:Disconnect()
            return
        end
        
        local offset = Vector3.new(
            (math.random() - 0.5) * intensity,
            (math.random() - 0.5) * intensity,
            0
        )
        Camera.CFrame = originalCFrame * CFrame.new(offset)
    end)
end

function StillnessEffects:restoreAudio()
    -- Restore original audio settings
    local restoreTween = TweenService:Create(
        SoundService,
        TweenInfo.new(2, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        OriginalSoundEffects
    )
    restoreTween:Play()
    
    -- Remove heartbeat and drone sounds
    local heartbeat = Camera:FindFirstChild("StillnessHeartbeat")
    if heartbeat then
        heartbeat:Stop()
        heartbeat:Destroy()
    end
    
    local drone = Camera:FindFirstChild("StillnessDrone")
    if drone then
        drone:Stop()
        drone:Destroy()
    end
    
    -- Remove shadow blur effect
    local shadowBlur = Lighting:FindFirstChild("StillnessShadowBlur")
    if shadowBlur then
        shadowBlur:Destroy()
    end
end

function StillnessEffects:destroy()
    -- Clean up UI elements
    if ScreenGui then
        ScreenGui:Destroy()
    end
    
    -- Remove all effects
    self:onTrapEnded()
    
    print("StillnessEffects destroyed")
end

return StillnessEffects
