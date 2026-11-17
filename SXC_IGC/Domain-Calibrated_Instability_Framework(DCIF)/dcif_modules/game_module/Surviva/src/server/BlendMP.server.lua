--[[
    BlendMP.server.lua
    Phase 2 Critical Task: Blend M and P
    
    Stalker spawn probability = (M * 0.6) + (P * 0.4)
    Combines memory field and prediction field for stalker behavior
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

-- Dependencies
local Shared = ReplicatedStorage:WaitForChild("Shared")
local MemoryField = require(Shared:WaitForChild("MemoryField"))
local PredictionField = require(script.Parent.PredictionField)

-- Remote for client effects
local remote = ReplicatedStorage:FindFirstChild("V12_Sync") or Instance.new("RemoteEvent")
remote.Name = "V12_Sync"
remote.Parent = ReplicatedStorage

local BlendMP = {}
BlendMP.__index = BlendMP

-- Blend parameters
local BLEND_CONFIG = {
    memoryWeight = 0.6,        -- Weight for memory field (M)
    predictionWeight = 0.4,    -- Weight for prediction field (P)
    spawnThreshold = 0.3,      -- Minimum blended value for stalker spawn
    updateInterval = 0.5,      -- How often to update blend calculations
    spawnCheckInterval = 2.0,  -- How often to check for stalker spawns
    maxSpawnDistance = 50,     -- Maximum distance from player for stalker spawn
    minSpawnDistance = 10      -- Minimum distance from player for stalker spawn
}

function BlendMP.new(player, playerState)
    local self = setmetatable({}, BlendMP)
    
    self.Player = player
    self.PlayerState = playerState
    self.MemoryField = playerState and playerState.MemoryField
    self.PredictionField = playerState and playerState.PredictionField
    
    -- Blend grid
    self.BlendGrid = {}
    self.GridSize = self.MemoryField and self.MemoryField.GridSize
    self.GridDimensions = self.MemoryField and self.MemoryField.GridDimensions
    
    -- Initialize blend grid
    self:initializeBlendGrid()
    
    -- Stalker tracking
    self.ActiveStalkers = {}
    self.LastSpawnCheck = 0
    
    -- Start update loops
    self:startUpdateLoops()
    
    print("BlendMP initialized for player:", player.Name)
    return self
end

function BlendMP:initializeBlendGrid()
    for x = 1, self.GridDimensions.x do
        self.BlendGrid[x] = {}
        for z = 1, self.GridDimensions.z do
            self.BlendGrid[x][z] = {
                blendedValue = 0.0,
                memoryValue = 0.0,
                predictionValue = 0.0,
                lastUpdate = tick()
            }
        end
    end
end

function BlendMP:startUpdateLoops()
    -- Update blend calculations
    RunService.Heartbeat:Connect(function(dt)
        self:updateBlendCalculations(dt)
    end)
    
    -- Check for stalker spawns
    RunService.Heartbeat:Connect(function(dt)
        self:updateStalkerSpawns(dt)
    end)
end

function BlendMP:updateBlendCalculations(dt)
    local now = tick()
    if now - (self.lastBlendUpdate or 0) < BLEND_CONFIG.updateInterval then return end
    
    -- Update each grid cell
    for x = 1, self.GridDimensions.x do
        for z = 1, self.GridDimensions.z do
            self:updateBlendCell(x, z)
        end
    end
    
    self.lastBlendUpdate = now
end

function BlendMP:updateBlendCell(x, z)
    -- Get world coordinates for this cell
    local worldX, worldZ = self:gridToWorld(x, z)
    
    -- Get M and P values
    local memoryValue = self.MemoryField:getMemoryAt(worldX, worldZ)
    local predictionValue = self.PredictionField:getPredictionAt(worldX, worldZ)
    
    -- Calculate blended value: (M * 0.6) + (P * 0.4)
    local blendedValue = (memoryValue * BLEND_CONFIG.memoryWeight) + (predictionValue * BLEND_CONFIG.predictionWeight)
    
    -- Update blend grid
    local cell = self.BlendGrid[x][z]
    cell.memoryValue = memoryValue
    cell.predictionValue = predictionValue
    cell.blendedValue = blendedValue
    cell.lastUpdate = tick()
end

function BlendMP:updateStalkerSpawns(dt)
    local now = tick()
    if now - self.LastSpawnCheck < BLEND_CONFIG.spawnCheckInterval then return end
    
    -- Check if we should spawn a stalker
    local spawnLocation = self:findBestSpawnLocation()
    
    if spawnLocation then
        self:spawnStalker(spawnLocation)
    end
    
    -- Update existing stalkers
    self:updateExistingStalkers(dt)
    
    self.LastSpawnCheck = now
end

function BlendMP:findBestSpawnLocation()
    local character = self.Player.Character
    if not character then return nil end
    
    local hrp = character:FindFirstChild("HumanoidRootPart")
    if not hrp then return nil end
    
    local playerPos = hrp.Position
    local bestLocation = nil
    local bestValue = 0
    
    -- Search for high blend values near player
    for x = 1, self.GridDimensions.x do
        for z = 1, self.GridDimensions.z do
            local cell = self.BlendGrid[x][z]
            
            -- Skip if below threshold
            if cell.blendedValue < BLEND_CONFIG.spawnThreshold then continue end
            
            -- Get world position
            local worldX, worldZ = self:gridToWorld(x, z)
            local worldPos = Vector3.new(worldX, playerPos.Y, worldZ)
            
            -- Check distance from player
            local distance = (worldPos - playerPos).Magnitude
            if distance < BLEND_CONFIG.minSpawnDistance or distance > BLEND_CONFIG.maxSpawnDistance then
                continue
            end
            
            -- Check if this is the best location
            if cell.blendedValue > bestValue then
                bestValue = cell.blendedValue
                bestLocation = {
                    position = worldPos,
                    blendValue = cell.blendedValue,
                    memoryValue = cell.memoryValue,
                    predictionValue = cell.predictionValue,
                    gridX = x,
                    gridZ = z
                }
            end
        end
    end
    
    return bestLocation
end

function BlendMP:spawnStalker(location)
    print("Spawning stalker at blend value:", location.blendValue)
    
    -- Create stalker
    local stalker = self:createStalker(location)
    
    -- Add to active stalkers
    table.insert(self.ActiveStalkers, stalker)
    
    -- Send spawn notification to client
    remote:FireClient(self.Player, "stalker_spawn", {
        position = location.position,
        blendValue = location.blendedValue,
        memoryValue = location.memoryValue,
        predictionValue = location.predictionValue,
        stalkerId = #self.ActiveStalkers
    })
end

function BlendMP:createStalker(location)
    local stalker = Instance.new("Model")
    stalker.Name = "BlendStalker"
    
    -- Create stalker body
    local torso = Instance.new("Part")
    torso.Name = "Torso"
    torso.Size = Vector3.new(4, 6, 2)
    torso.BrickColor = BrickColor.new("Really black")
    torso.Material = Enum.Material.Neon
    torso.Transparency = 0.3
    torso.Position = location.position + Vector3.new(0, 3, 0)
    torso.Parent = stalker
    
    -- Add glow effect based on blend type
    local glow = Instance.new("PointLight")
    glow.Color = location.memoryValue > location.predictionValue and Color3.new(0.5, 0.2, 0.2) or Color3.new(0.2, 0.2, 0.5)
    glow.Brightness = location.blendedValue * 3
    glow.Range = 15
    glow.Parent = torso
    
    -- Add sound based on dominant factor
    local sound = Instance.new("Sound")
    sound.SoundId = location.memoryValue > location.predictionValue and "rbxassetid://9127599111" or "rbxassetid://9127608562"
    sound.Volume = location.blendedValue * 0.4
    sound.Looped = true
    sound.Parent = torso
    sound:Play()
    
    -- Stalker metadata
    stalker:SetAttribute("BlendValue", location.blendedValue)
    stalker:SetAttribute("MemoryValue", location.memoryValue)
    stalker:SetAttribute("PredictionValue", location.predictionValue)
    stalker:SetAttribute("SpawnTime", tick())
    stalker:SetAttribute("GridX", location.gridX)
    stalker:SetAttribute("GridZ", location.gridZ)
    
    -- Parent to workspace
    stalker.Parent = workspace
    
    return stalker
end

function BlendMP:updateExistingStalkers(dt)
    local now = tick()
    local stalkersToRemove = {}
    
    for i, stalker in ipairs(self.ActiveStalkers) do
        if not stalker or not stalker.Parent then
            table.insert(stalkersToRemove, i)
            continue
        end
        
        -- Update stalker behavior based on current blend values
        self:updateStalkerBehavior(stalker, dt)
        
        -- Remove old stalkers
        local spawnTime = stalker:GetAttribute("SpawnTime") or 0
        if now - spawnTime > 30 then -- Stalkers live for 30 seconds
            table.insert(stalkersToRemove, i)
        end
    end
    
    -- Remove dead stalkers
    for i = #stalkersToRemove, 1, -1 do
        local index = stalkersToRemove[i]
        local stalker = self.ActiveStalkers[index]
        if stalker then
            self:removeStalker(stalker)
        end
        table.remove(self.ActiveStalkers, index)
    end
end

function BlendMP:updateStalkerBehavior(stalker, dt)
    local gridX = stalker:GetAttribute("GridX")
    local gridZ = stalker:GetAttribute("GridZ")
    
    if not gridX or not gridZ then return end
    
    -- Get current blend values at stalker location
    local cell = self.BlendGrid[gridX][gridZ]
    if not cell then return end
    
    -- Update stalker appearance based on current values
    local torso = stalker:FindFirstChild("Torso")
    if torso then
        -- Update transparency based on blend value
        torso.Transparency = 0.3 + (1 - cell.blendedValue) * 0.5
        
        -- Update glow
        local glow = torso:FindFirstChild("PointLight")
        if glow then
            glow.Brightness = cell.blendedValue * 3
            
            -- Change color based on dominant factor
            if cell.memoryValue > cell.predictionValue then
                glow.Color = Color3.new(0.5, 0.2, 0.2) -- Red tint for memory
            else
                glow.Color = Color3.new(0.2, 0.2, 0.5) -- Blue tint for prediction
            end
        end
        
        -- Update sound
        local sound = torso:FindFirstChild("Sound")
        if sound then
            sound.Volume = cell.blendedValue * 0.4
        end
    end
    
    -- Update stalker attributes
    stalker:SetAttribute("BlendValue", cell.blendedValue)
    stalker:SetAttribute("MemoryValue", cell.memoryValue)
    stalker:SetAttribute("PredictionValue", cell.predictionValue)
end

function BlendMP:removeStalker(stalker)
    if stalker then
        -- Fade out effect
        local torso = stalker:FindFirstChild("Torso")
        if torso then
            local tween = game:GetService("TweenService"):Create(
                torso,
                TweenInfo.new(1, Enum.EasingStyle.Quad, Enum.EasingDirection.Out),
                {Transparency = 1}
            )
            tween:Play()
            
            tween.Completed:Connect(function()
                stalker:Destroy()
            end)
        else
            stalker:Destroy()
        end
        
        -- Send removal notification to client
        remote:FireClient(self.Player, "stalker_remove", {
            stalkerId = self:getStalkerId(stalker)
        })
    end
end

function BlendMP:getStalkerId(stalker)
    for i, activeStalker in ipairs(self.ActiveStalkers) do
        if activeStalker == stalker then
            return i
        end
    end
    return -1
end

function BlendMP:gridToWorld(gridX, gridZ)
    -- Convert grid coordinates to world coordinates
    local worldX = (gridX - 1) * self.GridSize - (self.GridDimensions.x * self.GridSize) / 2
    local worldZ = (gridZ - 1) * self.GridSize - (self.GridDimensions.z * self.GridSize) / 2
    return worldX, worldZ
end

function BlendMP:getBlendedValueAt(worldX, worldZ)
    -- Get blended value at world coordinates
    local gridX, gridZ = self.MemoryField:worldToGrid(worldX, worldZ)
    
    if self.BlendGrid[gridX] and self.BlendGrid[gridX][gridZ] then
        return self.BlendGrid[gridX][gridZ].blendedValue
    end
    
    return 0.0
end

function BlendMP:getBlendGrid()
    -- Return a copy of the blend grid for debugging/visualization
    local gridCopy = {}
    for x = 1, self.GridDimensions.x do
        gridCopy[x] = {}
        for z = 1, self.GridDimensions.z do
            local cell = self.BlendGrid[x][z]
            gridCopy[x][z] = {
                blendedValue = cell.blendedValue,
                memoryValue = cell.memoryValue,
                predictionValue = cell.predictionValue
            }
        end
    end
    return gridCopy
end

function BlendMP:destroy()
    -- Remove all active stalkers
    for _, stalker in ipairs(self.ActiveStalkers) do
        self:removeStalker(stalker)
    end
    self.ActiveStalkers = {}
    
    print("BlendMP destroyed for player:", self.Player.Name)
end

return BlendMP
