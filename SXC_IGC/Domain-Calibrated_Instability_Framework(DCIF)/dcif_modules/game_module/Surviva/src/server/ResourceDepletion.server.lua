--[[
    ResourceDepletion.server.lua
    Phase 1 Critical Task: Resource Depletion
    
    Overharvesting creates memory scars:
    - When players gather too many resources from an area, it creates permanent memory increases
    - Depleted areas have higher M values, making the stalker more likely to appear there
    - Visual feedback shows resource scarcity
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Workspace = workspace

-- Dependencies
local Shared = ReplicatedStorage:WaitForChild("Shared")
-- ResourceDepletion now consumes the authoritative PlayerState (owned by SystemManager)
-- so it should not require MemoryField directly here.

-- Remote for client effects
local remote = ReplicatedStorage:FindFirstChild("V12_Sync") or Instance.new("RemoteEvent")
remote.Name = "V12_Sync"
remote.Parent = ReplicatedStorage

local ResourceDepletion = {}
ResourceDepletion.__index = ResourceDepletion

-- Depletion parameters
local DEPLETION_CONFIG = {
    depletionThreshold = 5,           -- Resources gathered before depletion starts
    depletionMultiplier = 2.0,        -- How much M increases when depleted
    scarDuration = 300.0,             -- How long depletion scars last (5 minutes)
    respawnDelayMultiplier = 3.0,     -- Resources take longer to respawn in depleted areas
    visualFeedbackThreshold = 3,      -- When to start showing scarcity effects
    depletionRadius = 8,              -- Radius of depletion effect
    updateInterval = 1.0              -- How often to check for depletion
}

function ResourceDepletion.new(player, playerState)
    local self = setmetatable({}, ResourceDepletion)

    self.Player = player
    -- playerState is the authoritative container owning MemoryField, PredictionField, TensionEngine, etc.
    self.PlayerState = playerState
    
    -- Track resource gathering
    self.GatheringHistory = {} -- position -> resource count
    
    -- Track depletion scars
    self.DepletionScars = {} -- position -> scar data
    
    -- Connect events
    self:connectEvents()
    
    print("ResourceDepletion initialized for player:", player.Name)
    return self
end

function ResourceDepletion:connectEvents()
    -- Listen for resource gathering events
    remote.OnServerEvent:Connect(function(player, eventName, data)
        if player ~= self.Player then return end
        
        if eventName == "resource_gathered" then
            self:onResourceGathered(data)
        end
    end)
    
    -- Periodic cleanup
    RunService.Heartbeat:Connect(function(dt)
        self:updateDepletionScars(dt)
    end)
end

function ResourceDepletion:onResourceGathered(data)
    local position = data.position
    local resourceType = data.resourceType or "generic"
    local amount = data.amount or 1
    
    -- Update gathering history
    local posKey = self:getPositionKey(position)
    if not self.GatheringHistory[posKey] then
        self.GatheringHistory[posKey] = {
            totalGathered = 0,
            resourceType = resourceType,
            firstGathered = tick(),
            lastGathered = 0
        }
    end
    
    local history = self.GatheringHistory[posKey]
    history.totalGathered = history.totalGathered + amount
    history.lastGathered = tick()
    
    -- Check if area is becoming depleted
    self:checkForDepletion(posKey, position, history)
    
    print(string.format("Player %s gathered %d %s at %s (total: %d)", 
        self.Player.Name, amount, resourceType, tostring(position), history.totalGathered))
end

function ResourceDepletion:checkForDepletion(posKey, position, history)
    local totalGathered = history.totalGathered
    
    -- Check if we've exceeded the depletion threshold
    if totalGathered >= DEPLETION_CONFIG.depletionThreshold then
        self:createDepletionScar(posKey, position, history)
    elseif totalGathered >= DEPLETION_CONFIG.visualFeedbackThreshold then
        -- Show early warning of potential depletion
        self:showDepletionWarning(position, history)
    end
end

function ResourceDepletion:createDepletionScar(posKey, position, history)
    local now = tick()
    
    -- Create or update depletion scar
    if not self.DepletionScars[posKey] then
        self.DepletionScars[posKey] = {
            position = position,
            totalGathered = history.totalGathered,
            resourceType = history.resourceType,
            createdTime = now,
            lastUpdated = now,
            memoryIncrease = DEPLETION_CONFIG.depletionMultiplier
        }
        
        print(string.format("Depletion scar created at %s for %s", tostring(position), history.resourceType))
    else
        -- Update existing scar
        local scar = self.DepletionScars[posKey]
        scar.totalGathered = history.totalGathered
        scar.lastUpdated = now
        scar.memoryIncrease = DEPLETION_CONFIG.depletionMultiplier * (history.totalGathered / DEPLETION_CONFIG.depletionThreshold)
    end
    
    -- Apply memory scar
    self:applyMemoryScar(position, self.DepletionScars[posKey].memoryIncrease)
    
    -- Send client notification
    remote:FireClient(self.Player, "depletion_scar_created", {
        position = position,
        resourceType = history.resourceType,
        severity = math.min(history.totalGathered / DEPLETION_CONFIG.depletionThreshold, 3.0)
    })
end

function ResourceDepletion:applyMemoryScar(position, memoryIncrease)
    -- Increase memory field in the depleted area
    local ps = self.PlayerState
    if not ps or not ps.MemoryField or not ps.MemoryField.addMemoryAtPosition then
        return
    end

    local mem = ps.MemoryField
    -- Apply memory increase in a radius around the position
    local radius = DEPLETION_CONFIG.depletionRadius
    local gridSize = mem.GridSize or 10

    -- Convert world position to grid coordinates
    local centerX, centerZ = mem:worldToGrid(position.X, position.Z)

    -- Apply memory increase to surrounding cells
    local cellRadius = math.ceil(radius / gridSize)
    for dx = -cellRadius, cellRadius do
        for dz = -cellRadius, cellRadius do
            local x = centerX + dx
            local z = centerZ + dz

            if mem.Grid[x] and mem.Grid[x][z] then
                -- Distance-based falloff
                local distance = math.sqrt(dx * dx + dz * dz)
                local falloff = 1 - (distance / cellRadius)

                if falloff > 0 then
                    -- Add permanent memory increase
                    local worldX, worldZ = mem:gridToWorld(x, z)
                    mem:addMemoryAtPosition(Vector3.new(worldX, position.Y, worldZ), memoryIncrease * falloff)
                end
            end
        end
    end
end

function ResourceDepletion:showDepletionWarning(position, history)
    -- Send warning to client about potential depletion
    remote:FireClient(self.Player, "depletion_warning", {
        position = position,
        resourceType = history.resourceType,
        currentAmount = history.totalGathered,
        threshold = DEPLETION_CONFIG.depletionThreshold
    })
end

function ResourceDepletion:updateDepletionScars(dt)
    local now = tick()
    local expiredScars = {}
    
    -- Check for expired scars
    for posKey, scar in pairs(self.DepletionScars) do
        if now - scar.createdTime >= DEPLETION_CONFIG.scarDuration then
            table.insert(expiredScars, posKey)
        end
    end
    
    -- Remove expired scars
    for _, posKey in ipairs(expiredScars) do
        local scar = self.DepletionScars[posKey]
        print(string.format("Depletion scar expired at %s", tostring(scar.position)))
        
        -- Notify client of scar expiration
        remote:FireClient(self.Player, "depletion_scar_expired", {
            position = scar.position,
            resourceType = scar.resourceType
        })
        
        self.DepletionScars[posKey] = nil
    end
end

function ResourceDepletion:getDepletionAtPosition(position)
    -- Check if position has depletion effects
    local posKey = self:getPositionKey(position)
    local scar = self.DepletionScars[posKey]
    
    if scar then
        return {
            depleted = true,
            resourceType = scar.resourceType,
            severity = scar.memoryIncrease / DEPLETION_CONFIG.depletionMultiplier,
            timeRemaining = DEPLETION_CONFIG.scarDuration - (tick() - scar.createdTime)
        }
    end
    
    -- Check gathering history for early depletion
    local history = self.GatheringHistory[posKey]
    if history and history.totalGathered >= DEPLETION_CONFIG.visualFeedbackThreshold then
        return {
            depleted = false,
            warning = true,
            resourceType = history.resourceType,
            currentAmount = history.totalGathered,
            threshold = DEPLETION_CONFIG.depletionThreshold
        }
    end
    
    return { depleted = false, warning = false }
end

function ResourceDepletion:getPositionKey(position)
    -- Create a grid-based key for position grouping
    local gridSize = DEPLETION_CONFIG.depletionRadius
    local x = math.floor(position.X / gridSize) * gridSize
    local z = math.floor(position.Z / gridSize) * gridSize
    return string.format("%.1f_%.1f", x, z)
end

function ResourceDepletion:getDepletionScars()
    -- Return current depletion scars for debugging
    local scars = {}
    for posKey, scar in pairs(self.DepletionScars) do
        scars[posKey] = {
            position = scar.position,
            resourceType = scar.resourceType,
            severity = scar.memoryIncrease / DEPLETION_CONFIG.depletionMultiplier,
            age = tick() - scar.createdTime
        }
    end
    return scars
end

function ResourceDepletion:resetDepletionAt(position)
    -- Debug function to reset depletion at a position
    local posKey = self:getPositionKey(position)
    
    if self.DepletionScars[posKey] then
        self.DepletionScars[posKey] = nil
        print("Reset depletion at", tostring(position))
    end
    
    if self.GatheringHistory[posKey] then
        self.GatheringHistory[posKey] = nil
        print("Reset gathering history at", tostring(position))
    end
end

function ResourceDepletion:destroy()
    -- Clean up
    self.GatheringHistory = {}
    self.DepletionScars = {}
    
    print("ResourceDepletion destroyed for player:", self.Player.Name)
end

return ResourceDepletion
