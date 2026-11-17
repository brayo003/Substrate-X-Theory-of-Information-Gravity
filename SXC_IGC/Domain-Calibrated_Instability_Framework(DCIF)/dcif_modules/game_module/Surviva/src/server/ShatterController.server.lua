-- ShatterController.server.lua
-- Trigger: T_sys > 1.15 AND P_sys > 0.7
-- Effects: Input inversion, body trailing, control loss, The Grab

local ShatterController = {}
ShatterController.__index = ShatterController

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local RunService = game:GetService("RunService")
local Players = game:GetService("Players")

-- Configuration
local SHATTER_DURATION = 10  -- seconds before recovery
local TRAIL_DELAY = 2        -- seconds (body follows stalker's past position)
local GRAB_DEGRADATION = 0.9 -- movement speed multiplier after The Grab

-- Phase 4: Input Delay and Movement Buffer
local INPUT_DELAY_MS = 500  -- milliseconds of input lag
local MOVEMENT_BUFFER_DURATION = 2.0 -- seconds of movement trail

function ShatterController.new(tensionSystem, stalker, player)
    local self = setmetatable({}, ShatterController)
    self.TensionSystem = tensionSystem
    self.Stalker = stalker
    self.Player = player
    self.Active = false
    self.TrailBuffer = {}  -- stores stalker positions over time
    self.BufferSize = TRAIL_DELAY / 0.05  -- 40 frames at DT=0.05
    self.OriginalControls = nil
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
    
    -- 1. Control Loss: Disable player movement
    local character = self.Player.Character
    local humanoid = character and character:FindFirstChild("Humanoid")
    if humanoid then
        self.OriginalControls = humanoid.AutoRotate
        humanoid.AutoRotate = false
        humanoid.PlatformStand = true
    end
    
    -- 2. Input Inversion: Bind stalker movement to player inputs
    self:SetupInputInversion()
    
    -- 3. Body Trailing: Start recording stalker position
    self:StartBodyTrailing()
    
    -- 4. Notify client
    local remote = ReplicatedStorage:FindFirstChild("V12_Sync")
    if remote then
        remote:FireClient(self.Player, "shatter_start")
    end
    
    print("[Shatter] Activated for", self.Player.Name)
    
    -- 5. Recovery after duration
    task.wait(SHATTER_DURATION)
    self:Deactivate()
end

function ShatterController:SetupInputInversion()
    local UserInputService = game:GetService("UserInputService")
    local character = self.Player.Character
    local hrp = character and character:FindFirstChild("HumanoidRootPart")
    
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
    self.TrailBuffer = {}
    
    -- Record stalker position every frame
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
    
    -- Move player body to trail position
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
    -- The Grab: permanent degradation
    local character = self.Player.Character
    local humanoid = character and character:FindFirstChild("Humanoid")
    if humanoid then
        humanoid.WalkSpeed = humanoid.WalkSpeed * GRAB_DEGRADATION
    end
    
    local remote = ReplicatedStorage:FindFirstChild("V12_Sync")
    if remote then
        remote:FireClient(self.Player, "the_grab")
    end
    
    print("[Shatter] The Grab executed on", self.Player.Name)
end

function ShatterController:Deactivate()
    if not self.Active then return end
    self.Active = false

    -- Restore control
    local character = self.Player.Character
    local humanoid = character and character:FindFirstChild("Humanoid")
    if humanoid then
        humanoid.AutoRotate = self.OriginalControls ~= false
        humanoid.PlatformStand = false
    end

    -- Clean up connections
    if self.InputConnection then self.InputConnection:Disconnect() end
    if self.RecordConnection then self.RecordConnection:Disconnect() end
    if self.TrailConnection then self.TrailConnection:Disconnect() end

    -- Phase 4: Deactivate input delay and movement buffer
    self:DeactivateInputDelay()
    self:DeactivateMovementBuffer()

    local remote = ReplicatedStorage:FindFirstChild("V12_Sync")
    if remote then
        remote:FireClient(self.Player, "shatter_end")
    end

    print("[Shatter] Deactivated for", self.Player.Name)
end

function ShatterController:Update()
    if self:ShouldTrigger() then
        self:Activate()
    end
end

-- Phase 4: Input Delay and Movement Buffer Functions

function ShatterController:ActivateInputDelay()
    self.InputDelayActive = true
    self.InputQueue = {}
    self.LastInputTime = tick()

    local remote = ReplicatedStorage:FindFirstChild("V12_Sync")
    if remote then
        remote:FireClient(self.Player, "input_delay_start", {
            delayMs = INPUT_DELAY_MS
        })
    end
end

function ShatterController:ActivateMovementBuffer()
    self.MovementBufferActive = true
    self.PositionHistory = {}
    self.BufferSize = MOVEMENT_BUFFER_DURATION / 0.05 -- 40 frames

    local remote = ReplicatedStorage:FindFirstChild("V12_Sync")
    if remote then
        remote:FireClient(self.Player, "movement_buffer_start", {
            duration = MOVEMENT_BUFFER_DURATION
        })
    end
end

function ShatterController:DeactivateInputDelay()
    self.InputDelayActive = false
    self.InputQueue = {}

    local remote = ReplicatedStorage:FindFirstChild("V12_Sync")
    if remote then
        remote:FireClient(self.Player, "input_delay_end")
    end
end

function ShatterController:DeactivateMovementBuffer()
    self.MovementBufferActive = false
    self.PositionHistory = {}

    local remote = ReplicatedStorage:FindFirstChild("V12_Sync")
    if remote then
        remote:FireClient(self.Player, "movement_buffer_end")
    end
end

return ShatterController
