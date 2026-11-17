--[[
    BookMutationEffects.client.lua
    Client-side effects for book mutations
    
    When mutations occur:
    - Text warps and distorts
    - Colors shift to red/wrong
    - Screen effects during mutation events
    - Audio cues for unreliable information
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local TweenService = game:GetService("TweenService")
local SoundService = game:GetService("SoundService")
local RunService = game:GetService("RunService")

local Player = Players.LocalPlayer
local PlayerGui = Player:WaitForChild("PlayerGui")

-- Remote events
local remote = ReplicatedStorage:WaitForChild("V12_Sync")

local BookMutationEffects = {}
BookMutationEffects.__index = BookMutationEffects

-- Effect parameters
local EFFECT_CONFIG = {
    mutationFlashDuration = 0.5,
    textWarpIntensity = 0.8,
    colorShiftDuration = 1.0,
    audioGlitchDuration = 0.3,
    screenDistortionStrength = 0.2,
    heartbeatSpikeVolume = 0.6
}

-- State tracking
local MutationsActive = false
local CurrentMutations = {}
local MutationUI = nil

function BookMutationEffects.new()
    local self = setmetatable({}, BookMutationEffects)
    
    -- Create mutation UI
    self:createMutationUI()
    
    -- Connect remote events
    self:connectEvents()
    
    print("BookMutationEffects initialized")
    return self
end

function BookMutationEffects:createMutationUI()
    MutationUI = Instance.new("ScreenGui")
    MutationUI.Name = "BookMutationEffects"
    MutationUI.Parent = PlayerGui
    MutationUI.ZIndexBehavior = Enum.ZIndexBehavior.Sibling
    
    -- Create mutation flash overlay
    local flashOverlay = Instance.new("Frame")
    flashOverlay.Name = "MutationFlash"
    flashOverlay.Size = UDim2.new(1, 0, 1, 0)
    flashOverlay.Position = UDim2.new(0, 0, 0, 0)
    flashOverlay.BackgroundColor3 = Color3.new(1, 0, 0)
    flashOverlay.BackgroundTransparency = 1.0
    flashOverlay.BorderSizePixel = 0
    flashOverlay.Parent = MutationUI
end

function BookMutationEffects:connectEvents()
    remote.OnClientEvent:Connect(function(eventName, ...)
        if eventName == "book_mutations_activate" then
            self:onMutationsActivate()
        elseif eventName == "book_mutations_deactivate" then
            self:onMutationsDeactivate()
        elseif eventName == "book_entry_mutate" then
            local data = ...
            self:onEntryMutate(data)
        elseif eventName == "book_entry_restore" then
            local data = ...
            self:onEntryRestore(data)
        end
    end)
end

function BookMutationEffects:onMutationsActivate()
    print("Book mutations activated - unreliable mode")
    MutationsActive = true
    
    -- Visual indicator that book is unreliable
    self:showUnreliableIndicator()
    
    -- Change book UI colors to indicate unreliability
    self:setBookUnreliableColors()
end

function BookMutationEffects:onMutationsDeactivate()
    print("Book mutations deactivated - returning to normal")
    MutationsActive = false
    
    -- Remove unreliable indicators
    self:hideUnreliableIndicator()
    
    -- Restore book UI colors
    self:setBookNormalColors()
    
    -- Clear current mutations
    CurrentMutations = {}
end

function BookMutationEffects:onEntryMutate(data)
    local entryId = data.entryId
    local mutatedText = data.mutatedText
    local mutationType = data.mutationType
    
    print("Book entry mutated:", entryId)
    
    -- Store mutation
    CurrentMutations[entryId] = {
        mutatedText = mutatedText,
        mutationType = mutationType
    }
    
    -- Play mutation effects
    self:playMutationEffects(entryId, mutationType)
    
    -- Update book UI to show mutated text
    self:updateBookEntryText(entryId, mutatedText)
end

function BookMutationEffects:onEntryRestore(data)
    local entryId = data.entryId
    local originalText = data.originalText
    
    print("Book entry restored:", entryId)
    
    -- Remove from current mutations
    CurrentMutations[entryId] = nil
    
    -- Play restoration effects
    self:playRestorationEffects(entryId)
    
    -- Update book UI to show original text
    self:updateBookEntryText(entryId, originalText)
end

function BookMutationEffects:playMutationEffects(entryId, mutationType)
    -- Flash screen red
    self:flashScreenRed()
    
    -- Play audio glitch
    self:playAudioGlitch()
    
    -- Apply text warping effect
    self:warpBookText(entryId)
    
    -- Screen distortion
    self:applyScreenDistortion()
end

function BookMutationEffects:playRestorationEffects(entryId)
    -- Subtle positive flash
    self:flashScreenGreen()
    
    -- Clear text warping
    self:clearTextWarp(entryId)
end

function BookMutationEffects:flashScreenRed()
    if not MutationUI then return end
    
    local flashOverlay = MutationUI:FindFirstChild("MutationFlash")
    if not flashOverlay then return end
    
    -- Quick red flash
    local flashTween = TweenService:Create(
        flashOverlay,
        TweenInfo.new(EFFECT_CONFIG.mutationFlashDuration, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {BackgroundTransparency = 0.3}
    )
    flashTween:Play()
    
    flashTween.Completed:Connect(function()
        local fadeTween = TweenService:Create(
            flashOverlay,
            TweenInfo.new(EFFECT_CONFIG.mutationFlashDuration, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
            {BackgroundTransparency = 1.0}
        )
        fadeTween:Play()
    end)
end

function BookMutationEffects:flashScreenGreen()
    if not MutationUI then return end
    
    local flashOverlay = MutationUI:FindFirstChild("MutationFlash")
    if not flashOverlay then return end
    
    -- Quick green flash
    flashOverlay.BackgroundColor3 = Color3.new(0, 1, 0)
    
    local flashTween = TweenService:Create(
        flashOverlay,
        TweenInfo.new(EFFECT_CONFIG.mutationFlashDuration, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
        {BackgroundTransparency = 0.5}
    )
    flashTween:Play()
    
    flashTween.Completed:Connect(function()
        local fadeTween = TweenService:Create(
            flashOverlay,
            TweenInfo.new(EFFECT_CONFIG.mutationFlashDuration, Enum.EasingStyle.Quad, Enum.EasingDirection.In),
            {BackgroundTransparency = 1.0}
        )
        fadeTween:Play()
        
        fadeTween.Completed:Connect(function()
            flashOverlay.BackgroundColor3 = Color3.new(1, 0, 0)
        end)
    end)
end

function BookMutationEffects:playAudioGlitch()
    -- Create audio glitch sound
    local glitchSound = Instance.new("Sound")
    glitchSound.Name = "BookMutationGlitch"
    glitchSound.SoundId = "rbxassetid://131961136" -- Low frequency glitch
    glitchSound.Volume = 0.4
    glitchSound.Parent = workspace.CurrentCamera
    glitchSound:Play()
    
    -- Remove after duration
    game:GetService("Debris"):AddItem(glitchSound, EFFECT_CONFIG.audioGlitchDuration)
end

function BookMutationEffects:warpBookText(entryId)
    -- This would interface with the actual Book UI
    -- For now, create a temporary warp effect
    self:createTextWarpEffect(entryId)
end

function BookMutationEffects:createTextWarpEffect(entryId)
    -- Create a temporary text distortion effect
    local warpLabel = Instance.new("TextLabel")
    warpLabel.Name = "TextWarp_" .. entryId
    warpLabel.Size = UDim2.new(0, 300, 0, 50)
    warpLabel.Position = UDim2.new(0.5, -150, 0.5, -25)
    warpLabel.BackgroundTransparency = 1
    warpLabel.Text = "KNOWLEDGE CORRUPTED"
    warpLabel.TextColor3 = Color3.new(1, 0, 0)
    warpLabel.TextScaled = true
    warpLabel.Font = Enum.Font.SourceSansBold
    warpLabel.Parent = MutationUI
    
    -- Animate warping
    local warpTween = TweenService:Create(
        warpLabel,
        TweenInfo.new(2, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true),
        {TextTransparency = 0.3}
    )
    warpTween:Play()
    
    -- Remove after a few seconds
    game:GetService("Debris"):AddItem(warpLabel, 3)
end

function BookMutationEffects:clearTextWarp(entryId)
    -- Remove any warp effects for this entry
    local warpLabel = MutationUI:FindFirstChild("TextWarp_" .. entryId)
    if warpLabel then
        warpLabel:Destroy()
    end
end

function BookMutationEffects:applyScreenDistortion()
    -- Apply temporary screen distortion
    local distortion = Instance.new("DistortionEffect")
    distortion.Name = "BookMutationDistortion"
    distortion.Parent = game:GetService("Lighting")
    distortion.Distortion = EFFECT_CONFIG.screenDistortionStrength
    
    -- Remove after duration
    game:GetService("Debris"):AddItem(distortion, EFFECT_CONFIG.audioGlitchDuration)
end

function BookMutationEffects:showUnreliableIndicator()
    -- Create an indicator that the book is unreliable
    local indicator = Instance.new("TextLabel")
    indicator.Name = "UnreliableIndicator"
    indicator.Size = UDim2.new(0, 200, 0, 30)
    indicator.Position = UDim2.new(1, -210, 0.1, 0)
    indicator.BackgroundColor3 = Color3.new(0.5, 0, 0)
    indicator.BackgroundTransparency = 0.7
    indicator.Text = "BOOK UNRELIABLE"
    indicator.TextColor3 = Color3.new(1, 0.5, 0.5)
    indicator.TextScaled = true
    indicator.Font = Enum.Font.SourceSansBold
    indicator.Parent = MutationUI
    
    -- Pulse effect
    local pulseTween = TweenService:Create(
        indicator,
        TweenInfo.new(1, Enum.EasingStyle.Sine, Enum.EasingDirection.InOut, -1, true),
        {BackgroundTransparency = 0.9}
    )
    pulseTween:Play()
end

function BookMutationEffects:hideUnreliableIndicator()
    local indicator = MutationUI:FindFirstChild("UnreliableIndicator")
    if indicator then
        indicator:Destroy()
    end
end

function BookMutationEffects:setBookUnreliableColors()
    -- This would interface with the actual Book UI to change colors
    -- For now, apply global color correction
    local colorCorrection = Instance.new("ColorCorrectionEffect")
    colorCorrection.Name = "BookUnreliableCorrection"
    colorCorrection.Parent = game:GetService("Lighting")
    colorCorrection.TintColor = Color3.new(1.2, 0.8, 0.8)
    colorCorrection.Saturation = -0.2
    colorCorrection.Contrast = 1.1
end

function BookMutationEffects:setBookNormalColors()
    -- Remove unreliable color correction
    local colorCorrection = game:GetService("Lighting"):FindFirstChild("BookUnreliableCorrection")
    if colorCorrection then
        colorCorrection:Destroy()
    end
end

function BookMutationEffects:updateBookEntryText(entryId, text)
    -- This would interface with the actual Book UI
    -- For now, just log the change
    print("Book entry", entryId, "updated to:", text)
end

function BookMutationEffects:getCurrentMutations()
    -- Return current mutation state
    return CurrentMutations
end

function BookMutationEffects:destroy()
    -- Clean up UI elements
    if MutationUI then
        MutationUI:Destroy()
    end
    
    -- Remove color corrections
    self:setBookNormalColors()
    
    print("BookMutationEffects destroyed")
end

return BookMutationEffects
