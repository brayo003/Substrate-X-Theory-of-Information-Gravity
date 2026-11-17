-- AnimalController.server.lua
-- 5 states based on T_sys: Observer → Encirclement → Alarm → Necrosis → Rupture

local AnimalController = {}
AnimalController.__index = AnimalController

local RunService = game:GetService("RunService")

-- Animal states
local ANIMAL_STATES = {
    NORMAL = 0,
    OBSERVER = 1,
    ENCIRCLEMENT = 2,
    ALARM = 3,
    NECROSIS = 4
}

function AnimalController.new(tensionSystem, player)
    local self = setmetatable({}, AnimalController)
    self.TensionSystem = tensionSystem
    self.Player = player
    self.Animals = {}  -- table of animal instances
    self.CurrentState = ANIMAL_STATES.NORMAL
    self.EncirclementRadius = 30
    return self
end

function AnimalController:RegisterAnimal(animal)
    table.insert(self.Animals, animal)
end

function AnimalController:GetCurrentState()
    local tension = self.TensionSystem:getTension()
    
    if tension > 1.1 then
        return ANIMAL_STATES.NECROSIS
    elseif tension > 0.9 then
        return ANIMAL_STATES.ALARM
    elseif tension > 0.7 then
        return ANIMAL_STATES.ENCIRCLEMENT
    elseif tension > 0.4 then
        return ANIMAL_STATES.OBSERVER
    else
        return ANIMAL_STATES.NORMAL
    end
end

function AnimalController:Update()
    local newState = self:GetCurrentState()
    
    if newState ~= self.CurrentState then
        self.CurrentState = newState
        self:OnStateChange()
    end
    
    self:UpdateAnimalBehaviors()
end

function AnimalController:OnStateChange()
    print("[Animals] State changed to", self.CurrentState)
    
    -- Notify client of state change for visual effects
    local remote = game:GetService("ReplicatedStorage"):FindFirstChild("V12_Sync")
    if remote then
        remote:FireAllClients("animal_state", self.CurrentState)
    end
end

function AnimalController:UpdateAnimalBehaviors()
    local playerPos = self.Player.Character and self.Player.Character:FindFirstChild("HumanoidRootPart")
    if not playerPos then return end
    
    for _, animal in ipairs(self.Animals) do
        if animal and animal.Parent then
            self:UpdateAnimalBehavior(animal, playerPos.Position)
        end
    end
end

function AnimalController:UpdateAnimalBehavior(animal, playerPos)
    local humanoid = animal:FindFirstChild("Humanoid")
    local hrp = animal:FindFirstChild("HumanoidRootPart")
    if not humanoid or not hrp then return end
    
    local dist = (hrp.Position - playerPos).Magnitude
    
    if self.CurrentState == ANIMAL_STATES.NORMAL then
        -- Normal AI (existing behavior)
        humanoid.WalkSpeed = 16
        
    elseif self.CurrentState == ANIMAL_STATES.OBSERVER then
        -- Animal stops and stares at player
        if dist < 40 then
            humanoid.WalkSpeed = 0
            hrp.CFrame = CFrame.lookAt(hrp.Position, playerPos)
        end
        
    elseif self.CurrentState == ANIMAL_STATES.ENCIRCLEMENT then
        -- Animals circle the player
        if dist < 30 and dist > 15 then
            local direction = (hrp.Position - playerPos).Unit
            local perpendicular = Vector3.new(-direction.Z, 0, direction.X)
            local targetPos = playerPos + perpendicular * self.EncirclementRadius
            humanoid:MoveTo(targetPos)
            humanoid.WalkSpeed = 12
        end
        
    elseif self.CurrentState == ANIMAL_STATES.ALARM then
        -- Scream, block paths
        if dist < 20 then
            -- Block player path
            local direction = (playerPos - hrp.Position).Unit
            local blockPos = playerPos + direction * 5
            humanoid:MoveTo(blockPos)
            humanoid.WalkSpeed = 8
            
            -- Random screaming
            if math.random() < 0.01 then
                local sound = Instance.new("Sound")
                sound.SoundId = "rbxassetid://9127608562"  -- Replace with animal scream
                sound.Volume = 0.7
                sound.Parent = hrp
                sound:Play()
                task.wait(1)
                sound:Destroy()
            end
        end
        
    elseif self.CurrentState == ANIMAL_STATES.NECROSIS then
        -- Twitching, glitching, dying
        if dist < 30 then
            -- Twitch effect
            hrp.CFrame = hrp.CFrame * CFrame.Angles(0, math.sin(tick() * 20) * 0.1, 0)
            
            -- Random death
            if math.random() < 0.005 then
                animal:Destroy()
                print("[Animals] Animal died from necrosis")
            end
        end
    end
end

function AnimalController:CleanupDeadAnimals()
    for i = #self.Animals, 1, -1 do
        if not self.Animals[i].Parent then
            table.remove(self.Animals, i)
        end
    end
end

return AnimalController
