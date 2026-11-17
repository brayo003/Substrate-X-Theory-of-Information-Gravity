local Player = game.Players.LocalPlayer
local PlayerGui = Player:WaitForChild("PlayerGui")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")
local Camera = workspace.CurrentCamera

local ScreenGui = Instance.new("ScreenGui", PlayerGui)
ScreenGui.Name = "V12_HUD"

local Frame = Instance.new("Frame", ScreenGui)
Frame.Size = UDim2.new(0, 200, 0, 50)
Frame.Position = UDim2.new(0.5, -100, 0.9, -60)
Frame.BackgroundColor3 = Color3.new(0, 0, 0)

local TensionBar = Instance.new("Frame", Frame)
TensionBar.Size = UDim2.new(0, 0, 1, 0)
TensionBar.BackgroundColor3 = Color3.new(0, 1, 0)

local Label = Instance.new("TextLabel", Frame)
Label.Size = UDim2.new(1, 0, 1, 0)
Label.BackgroundTransparency = 1
Label.TextColor3 = Color3.new(1, 1, 1)
Label.Text = "SUBSTRATE TENSION"

local tensionEvent = ReplicatedStorage:WaitForChild("V12_Sync")

-- =========================
-- V12 PROTOCOL (Client-side tension simulation)
-- =========================
local V12Engine = {}
V12Engine.__index = V12Engine

function V12Engine.new()
    local self = setmetatable({}, V12Engine)
    self.T_sys = 0.0
    self.phase = "NOMINAL"
    self.gamma_max = 0.8
    self.gamma = self.gamma_max
    self.beta = 3.5
    self.dt = 0.05
    self.decay_rate = 0.0005
    self.lastTime = tick()
    return self
end

function V12Engine:excitation_flux(signal)
    if signal < 45 then
        return 1 - math.exp(-signal / 40.0)
    end
    return 0.675 + ((signal - 45.0) / 20.0)
end

function V12Engine:apply_intervention(interventionType)
    if interventionType == "DEEP" then
        self.gamma = math.min(self.gamma_max, self.gamma * 1.15)
        self.T_sys = self.T_sys * 0.60
    else
        self.gamma = math.min(self.gamma_max, self.gamma * 1.05)
    end
end

function V12Engine:step(signal)
    local now = tick()
    local dt = math.min(0.1, now - self.lastTime)
    self.lastTime = now
    
    self.gamma = self.gamma * (1 - self.decay_rate)
    local E = self:excitation_flux(signal)
    local gamma_eff = (self.phase == "FIREWALL" and 2.2) or 1.0
    local inflow = E * self.beta
    local outflow = gamma_eff * self.gamma * self.T_sys
    self.T_sys = self.T_sys + (inflow - outflow) * dt
    
    if self.T_sys > 1.0 then
        self.phase = "FIREWALL"
    elseif self.phase == "FIREWALL" and self.T_sys < 0.4 then
        self.phase = "NOMINAL"
    end
    
    return self.T_sys, self.phase
end

-- Create client-side V12 engine
local clientV12 = V12Engine.new()

-- =========================
-- EFFECTS HANDLERS
-- =========================

-- Create a ghost stalker for false visual cues
local function createGhostStalker()
    local ghost = Instance.new("Part")
    ghost.Size = Vector3.new(4, 6, 2)
    ghost.BrickColor = BrickColor.new("Really black")
    ghost.Material = Enum.Material.Neon
    ghost.Transparency = 0.5
    ghost.Anchored = true
    ghost.CanCollide = false
    
    local offset = Vector3.new(
        math.random() > 0.5 and 15 or -15,
        3,
        -8
    )
    ghost.Position = Camera.CFrame.Position + (Camera.CFrame.RightVector * offset.X) + Vector3.new(0, offset.Y, offset.Z)
    ghost.Parent = workspace
    
    local tween = TweenService:Create(ghost, TweenInfo.new(0.5), {Transparency = 1})
    tween:Play()
    task.wait(0.5)
    ghost:Destroy()
end

-- Screen shake effect
local function screenShake(intensity, duration)
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

-- Screen distortion
local function screenDistortion(duration)
    local effect = Instance.new("ColorCorrectionEffect")
    effect.Parent = Camera
    effect.Saturation = -0.5
    effect.TintColor = Color3.new(1, 0, 0)
    task.wait(duration)
    effect:Destroy()
end

-- Flicker lights
local function flickerLights()
    local originalBrightness = game:GetService("Lighting").Brightness
    for i = 1, 3 do
        game:GetService("Lighting").Brightness = originalBrightness * (0.3 + math.random() * 0.4)
        task.wait(0.1)
        game:GetService("Lighting").Brightness = originalBrightness
        task.wait(0.1)
    end
end

-- Stretch shadows (stillness trap)
local function stretchShadows()
    local shadowEffect = Instance.new("BlurEffect")
    shadowEffect.Parent = game:GetService("Lighting")
    shadowEffect.Size = 10
    local tween = TweenService:Create(shadowEffect, TweenInfo.new(1), {Size = 0})
    tween:Play()
    task.wait(1)
    shadowEffect:Destroy()
end

-- Walls closing effect
local function wallsClosingEffect()
    screenShake(1, 0.5)
    local sound = Instance.new("Sound")
    sound.SoundId = "rbxassetid://9127599111"
    sound.Volume = 0.6
    sound.Parent = Camera
    sound:Play()
    task.wait(0.5)
    sound:Destroy()
end

-- Locked door effect
local function showLockedDoorEffect(position)
    local lockEffect = Instance.new("Part")
    lockEffect.Size = Vector3.new(1, 1, 0.5)
    lockEffect.BrickColor = BrickColor.new("Bright red")
    lockEffect.Material = Enum.Material.Neon
    lockEffect.Position = position + Vector3.new(0, 2, 0)
    lockEffect.Anchored = true
    lockEffect.CanCollide = false
    lockEffect.Parent = workspace
    task.wait(0.5)
    lockEffect:Destroy()
end

-- Floor collapse effect
local function floorCollapseEffect()
    screenShake(2, 0.5)
    for i = 1, 20 do
        local particle = Instance.new("Part")
        particle.Size = Vector3.new(0.2, 0.2, 0.2)
        particle.BrickColor = BrickColor.new("Grey")
        particle.Material = Enum.Material.SmoothPlastic
        particle.Anchored = false
        particle.CanCollide = false
        particle.Position = Player.Character and Player.Character.HumanoidRootPart.Position + Vector3.new(math.random(-3, 3), 0, math.random(-3, 3))
        particle.Velocity = Vector3.new(math.random(-10, 10), math.random(10, 30), math.random(-10, 10))
        particle.Parent = workspace
        task.wait(0.05)
        game:GetService("Debris"):AddItem(particle, 2)
    end
end

-- Stalker manifest effect
local function stalkerManifestEffect()
    screenShake(1, 0.3)
    local sound = Instance.new("Sound")
    sound.SoundId = "rbxassetid://9127608562"
    sound.Volume = 0.8
    sound.Parent = Camera
    sound:Play()
    task.wait(0.3)
    sound:Destroy()
end

-- Input lag effect
local inputLagActive = false
local inputLagAmount = 0

local function applyInputLag(ms)
    inputLagActive = true
    inputLagAmount = ms / 1000
    task.wait(inputLagAmount)
    inputLagActive = false
end

UserInputService.InputBegan:Connect(function(input, gameProcessed)
    if inputLagActive and not gameProcessed then
        task.wait(inputLagAmount)
    end
end)

-- Rupture effect
local function ruptureEffect()
    screenShake(3, 1.5)
    screenDistortion(1.5)
    local flash = Instance.new("Part")
    flash.Size = Vector3.new(100, 100, 100)
    flash.BrickColor = BrickColor.new("White")
    flash.Material = Enum.Material.Neon
    flash.Anchored = true
    flash.CanCollide = false
    flash.Position = Camera.CFrame.Position
    flash.Parent = workspace
    task.wait(0.1)
    flash:Destroy()
    local heartbeat = Instance.new("Sound")
    heartbeat.SoundId = "rbxassetid://9127608562"
    heartbeat.Volume = 0.5
    heartbeat.Parent = Player.Character
    heartbeat:Play()
    task.wait(3)
    heartbeat:Destroy()
end

-- Game over effect
local function gameOverEffect(reason)
    local frame = Instance.new("Frame")
    frame.Size = UDim2.new(1, 0, 1, 0)
    frame.BackgroundColor3 = Color3.new(0, 0, 0)
    frame.BackgroundTransparency = 0.5
    frame.Parent = ScreenGui
    
    local text = Instance.new("TextLabel", frame)
    text.Size = UDim2.new(1, 0, 0, 50)
    text.Position = UDim2.new(0, 0, 0.5, -25)
    text.Text = reason == "absorbed" and "YOU WERE ABSORBED BY THE SUBSTRATE" or "GAME OVER"
    text.TextColor3 = Color3.new(1, 0, 0)
    text.TextScaled = true
    text.BackgroundTransparency = 1
    
    task.wait(3)
    frame:Destroy()
end

-- =========================
-- CLIENT-SIDE TENSION LOOP (Heartbeat)
-- =========================
-- This runs the V12 Protocol locally for responsive UI
-- Also sends player signals to the server
local lastSendTime = 0
local sendInterval = 0.5  -- Send signal to server every 0.5 seconds

RunService.Heartbeat:Connect(function(dt)
    -- Get player movement speed
    local character = Player.Character
    local hrp = character and character:FindFirstChild("HumanoidRootPart")
    local velocity = hrp and hrp.Velocity.Magnitude or 0
    
    -- Convert velocity to signal (0-100 scale for V12 Protocol)
    -- Velocity 16 (sprinting) maps to ~60-80 signal
    local rawSignal = math.min(100, velocity * 5)
    
    -- Step the client-side V12 engine
    local clientTension, phase = clientV12:step(rawSignal)
    
    -- Update UI with client tension (responsive)
    local normalized = math.clamp(clientTension / 1.5, 0, 1)
    TensionBar.Size = UDim2.new(normalized, 0, 1, 0)
    TensionBar.BackgroundColor3 = Color3.fromHSV(0.33 * (1 - normalized), 1, 1)
    
    if clientTension > 1.2 then
        Label.Text = "!!! INSTABILITY !!!"
    elseif clientTension > 0.8 then
        Label.Text = "WARNING"
    else
        Label.Text = "SUBSTRATE TENSION: " .. math.floor(clientTension * 100) .. "%"
    end
    
    -- Send signal to server periodically (for anti-cheat and world state)
    local now = tick()
    if now - lastSendTime >= sendInterval then
        lastSendTime = now
        -- Send the raw signal (velocity-based) to server
        -- Server will use its own SXC-IGC engine to decide rupture
        local signalToSend = math.min(2.0, rawSignal / 50)  -- Normalize to 0-2 scale
        local remote = ReplicatedStorage:FindFirstChild("PlayerSignal")
        if remote then
            remote:FireServer(signalToSend)
        end
    end
end)

-- =========================
-- MAIN REMOTE EVENT HANDLER (Server sync)
-- =========================
tensionEvent.OnClientEvent:Connect(function(eventName, ...)
    if type(eventName) == "number" then
        -- Server sends authoritative tension (optional)
        -- We don't override client tension, but could use for correction
        -- For now, client tension drives UI
        return
    end
    
    if eventName == "false_visual" then
        createGhostStalker()
    elseif eventName == "sanctuary_flicker" then
        flickerLights()
    elseif eventName == "stillness_shadow" then
        stretchShadows()
    elseif eventName == "walls_closing" then
        wallsClosingEffect()
    elseif eventName == "rupture_effect" then
        ruptureEffect()
    elseif eventName == "stalker_manifest" then
        stalkerManifestEffect()
    elseif eventName == "input_lag" then
        local lagMs = ...
        applyInputLag(lagMs)
    elseif eventName == "door_lock" then
        local doorPos = ...
        showLockedDoorEffect(doorPos)
    elseif eventName == "floor_collapse" then
        floorCollapseEffect()
    elseif eventName == "resource_decay" then
        local effect = Instance.new("ColorCorrectionEffect")
        effect.Parent = Camera
        effect.TintColor = Color3.new(0.5, 0.3, 0.1)
        task.wait(0.5)
        effect:Destroy()
    elseif eventName == "game_over" then
        local reason = ...
        gameOverEffect(reason)
    end
end)

print("Bartholomew is online with V12 Protocol and full effect handlers.")

