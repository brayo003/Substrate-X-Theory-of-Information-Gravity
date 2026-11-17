--[[
    PredictionField.server.lua
    Phase 2 Critical Task: Prediction Field (P)
    
    Tracks where player looks and predicts future movement
    P increases when player looks toward a direction for >2 seconds
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")
local Workspace = workspace

local PredictionField = {}
PredictionField.__index = PredictionField

-- Prediction field parameters
local PREDICTION_CONFIG = {
    gridSize = 10,                    -- Size of each grid cell
    gridDimensions = {x = 50, z = 50}, -- Grid dimensions
    lookThreshold = 2.0,              -- Seconds of looking to increase P
    lookTolerance = math.rad(15),     -- Angle tolerance for "looking at"
    pDecayRate = 0.98,                -- P decay per second
    pGrowthRate = 0.1,                -- P growth per second when looking
    maxPrediction = 1.0,              -- Maximum P value
    updateInterval = 0.5              -- How often to update prediction
}

-- Weak memory-to-prediction gain (small influence)
local MEMORY_TO_P_GAIN = 0.02

function PredictionField.new(memoryField)
    local self = setmetatable({}, PredictionField)
    
    -- Initialize prediction grid
    self.Grid = {}
    self.GridSize = PREDICTION_CONFIG.gridSize
    self.GridDimensions = PREDICTION_CONFIG.gridDimensions
    -- Optional reference to the player's MemoryField for weak one-way coupling
    self.MemoryField = memoryField

    self:initializeGrid()
    
    -- Player tracking
    self.PlayerLookData = {}
    
    -- Start update loop
    self:startUpdateLoop()
    
    print("PredictionField initialized")
    return self
end

function PredictionField:initializeGrid()
    for x = 1, self.GridDimensions.x do
        self.Grid[x] = {}
        for z = 1, self.GridDimensions.z do
            self.Grid[x][z] = {
                P = 0.0,  -- Prediction value
                lastUpdate = tick()
            }
        end
    end
end

function PredictionField:startUpdateLoop()
    RunService.Heartbeat:Connect(function(dt)
        self:update(dt)
    end)
end

function PredictionField:update(dt)
    local now = tick()
    
    -- Update each player's look tracking
    for _, player in ipairs(Players:GetPlayers()) do
        self:updatePlayerLookData(player, dt)
    end
    
    -- Decay prediction values
    self:decayPrediction(dt)
    
    -- Weak memory -> prediction coupling (one-way): small additive contribution
    -- Memory influences P but P never writes back to Memory.
    if self.MemoryField and self.MemoryField.getMemoryAt then
        for x = 1, self.GridDimensions.x do
            for z = 1, self.GridDimensions.z do
                local worldX, worldZ = self:gridToWorld(x, z)
                local memVal = self.MemoryField:getMemoryAt(worldX, worldZ) or 0
                local inc = memVal * MEMORY_TO_P_GAIN * math.max(0, dt)
                local cell = self.Grid[x] and self.Grid[x][z]
                if cell then
                    cell.P = math.min(PREDICTION_CONFIG.maxPrediction, cell.P + inc)
                    cell.lastUpdate = tick()
                end
            end
        end
    end

    -- Update prediction based on look data
    if now - (self.lastUpdate or 0) >= PREDICTION_CONFIG.updateInterval then
        self:updatePredictionFromLook()
        self.lastUpdate = now
    end
end

function PredictionField:updatePlayerLookData(player, dt)
    -- Server-side: prefer injected gaze data if present, else fall back to camera (rare)
    local gazeEntry = self.PlayerLookData[player.UserId]
    local lookDirection = nil
    if gazeEntry and gazeEntry.injectedLook then
        lookDirection = gazeEntry.injectedLook
    else
        local character = player.Character
        if not character then return end
        local hrp = character:FindFirstChild("HumanoidRootPart")
        if not hrp then return end
        local camera = workspace.CurrentCamera
        if not camera then return end
        lookDirection = camera.CFrame.LookVector
    end
    
    -- Initialize player data if needed
    if not self.PlayerLookData[player.UserId] then
        self.PlayerLookData[player.UserId] = {
            currentLook = lookDirection,
            lookStartTime = 0,
            lookDuration = 0,
            isLookingConsistently = false
        }
    end
    
    local playerData = self.PlayerLookData[player.UserId]
    
    -- Check if look direction changed significantly
    local lookChange = (lookDirection - playerData.currentLook).Magnitude
    local isLookingConsistently = lookChange < 0.1 -- Threshold for "consistent looking"
    
    if isLookingConsistently then
        if not playerData.isLookingConsistently then
            -- Player started looking consistently
            playerData.lookStartTime = tick()
            playerData.isLookingConsistently = true
        end
        
        playerData.lookDuration = tick() - playerData.lookStartTime
        playerData.currentLook = lookDirection
    else
        -- Look direction changed, reset tracking
        playerData.lookStartTime = 0
        playerData.lookDuration = 0
        playerData.isLookingConsistently = false
        playerData.currentLook = lookDirection
    end
end

-- Allow server to receive gaze reports forwarded from clients
-- gazeData: {Position = Vector3, LookVector = Vector3, Timestamp = number}
function PredictionField:receiveGaze(gazeData)
    if not gazeData or not gazeData.LookVector or not gazeData.Timestamp or not gazeData.Position then return end
    -- map to player by looking up Players list by position heuristic is not reliable here; instead the router forwards to the player's PredictionField
    -- store injected look vector so updatePlayerLookData consumes it
    local userId = gazeData.UserId
    if not userId then
        return
    end
    if not self.PlayerLookData[userId] then
        self.PlayerLookData[userId] = { currentLook = gazeData.LookVector, lookStartTime = gazeData.Timestamp or tick(), lookDuration = 0, isLookingConsistently = false, injectedLook = gazeData.LookVector }
    else
        self.PlayerLookData[userId].injectedLook = gazeData.LookVector
    end
end

function PredictionField:decayPrediction(dt)
    for x = 1, self.GridDimensions.x do
        for z = 1, self.GridDimensions.z do
            local cell = self.Grid[x][z]
            cell.P = cell.P * math.pow(PREDICTION_CONFIG.pDecayRate, dt)
            cell.P = math.max(0, cell.P)
        end
    end
end

function PredictionField:updatePredictionFromLook()
    for userId, playerData in pairs(self.PlayerLookData) do
        local player = Players:GetPlayerByUserId(userId)
        if not player then continue end
        
        local character = player.Character
        if not character then continue end
        
        local hrp = character:FindFirstChild("HumanoidRootPart")
        if not hrp then continue end
        
        -- If player has been looking consistently for threshold time
        if playerData.lookDuration >= PREDICTION_CONFIG.lookThreshold then
            -- Calculate where player is looking
            local lookPosition = self:getLookTarget(hrp.Position, playerData.currentLook)
            
            -- Convert to grid coordinates
            local gridX, gridZ = self:worldToGrid(lookPosition.X, lookPosition.Z)
            
            -- Increase P in the looked-at area
            self:increasePredictionAt(gridX, gridZ)
        end
    end
end

function PredictionField:getLookTarget(origin, lookDirection)
    -- Cast a ray to find where player is looking
    local rayLength = 50 -- Look ahead 50 studs
    local rayDirection = lookDirection * rayLength
    local targetPosition = origin + rayDirection
    
    -- Simple raycast to find actual target
    local raycastResult = workspace:Raycast(origin, rayDirection)
    if raycastResult then
        targetPosition = raycastResult.Position
    end
    
    return targetPosition
end

function PredictionField:worldToGrid(worldX, worldZ)
    -- Convert world coordinates to grid indices
    local gridX = math.floor((worldX + (self.GridDimensions.x * self.GridSize) / 2) / self.GridSize) + 1
    local gridZ = math.floor((worldZ + (self.GridDimensions.z * self.GridSize) / 2) / self.GridSize) + 1
    
    -- Clamp to grid bounds
    gridX = math.max(1, math.min(self.GridDimensions.x, gridX))
    gridZ = math.max(1, math.min(self.GridDimensions.z, gridZ))
    
    return gridX, gridZ
end

function PredictionField:gridToWorld(gridX, gridZ)
    -- Convert grid indices to world coordinates
    local worldX = (gridX - 1) * self.GridSize - (self.GridDimensions.x * self.GridSize) / 2
    local worldZ = (gridZ - 1) * self.GridSize - (self.GridDimensions.z * self.GridSize) / 2
    
    return worldX, worldZ
end

function PredictionField:increasePredictionAt(gridX, gridZ)
    -- Increase P at the specified grid location
    if self.Grid[gridX] and self.Grid[gridX][gridZ] then
        local cell = self.Grid[gridX][gridZ]
        cell.P = math.min(PREDICTION_CONFIG.maxPrediction, cell.P + PREDICTION_CONFIG.pGrowthRate)
        cell.lastUpdate = tick()
        
        -- Also increase P in neighboring cells (spread effect)
        self:spreadPrediction(gridX, gridZ, 0.5)
    end
end

function PredictionField:spreadPrediction(centerX, centerZ, strength)
    -- Spread prediction to neighboring cells
    local radius = 2 -- Spread radius in grid cells
    
    for dx = -radius, radius do
        for dz = -radius, radius do
            if dx == 0 and dz == 0 then continue end -- Skip center cell
            
            local x = centerX + dx
            local z = centerZ + dz
            
            if x >= 1 and x <= self.GridDimensions.x and z >= 1 and z <= self.GridDimensions.z then
                local distance = math.sqrt(dx * dx + dz * dz)
                local falloff = strength * (1 - distance / (radius + 1))
                
                local cell = self.Grid[x][z]
                cell.P = math.min(PREDICTION_CONFIG.maxPrediction, cell.P + falloff * PREDICTION_CONFIG.pGrowthRate)
                cell.lastUpdate = tick()
            end
        end
    end
end

function PredictionField:getPredictionAt(worldX, worldZ)
    -- Get P value at world coordinates
    local gridX, gridZ = self:worldToGrid(worldX, worldZ)
    
    if self.Grid[gridX] and self.Grid[gridX][gridZ] then
        return self.Grid[gridX][gridZ].P
    end
    
    return 0.0
end

function PredictionField:getHighestPLocation()
    -- Find the location with highest P value
    local highestP = 0
    local highestX, highestZ = 1, 1
    
    for x = 1, self.GridDimensions.x do
        for z = 1, self.GridDimensions.z do
            local cell = self.Grid[x][z]
            if cell.P > highestP then
                highestP = cell.P
                highestX, highestZ = x, z
            end
        end
    end
    
    local worldX, worldZ = self:gridToWorld(highestX, highestZ)
    return Vector3.new(worldX, 0, worldZ), highestP
end

function PredictionField:getPredictionGrid()
    -- Return a copy of the prediction grid for debugging/visualization
    local gridCopy = {}
    for x = 1, self.GridDimensions.x do
        gridCopy[x] = {}
        for z = 1, self.GridDimensions.z do
            gridCopy[x][z] = self.Grid[x][z].P
        end
    end
    return gridCopy
end

function PredictionField:reset()
    -- Reset all prediction values
    for x = 1, self.GridDimensions.x do
        for z = 1, self.GridDimensions.z do
            local cell = self.Grid[x][z]
            cell.P = 0.0
            cell.lastUpdate = tick()
        end
    end
    
    -- Reset player look data
    self.PlayerLookData = {}
end

function PredictionField:destroy()
    -- Clean up
    print("PredictionField destroyed")
end

return PredictionField
