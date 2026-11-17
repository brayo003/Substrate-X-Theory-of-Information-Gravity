-- MemoryFlooding.server.lua
-- Spawns ghost players from past runs when P_sys > 0.9

local MemoryFlooding = {}
MemoryFlooding.__index = MemoryFlooding

local DataStoreService = game:GetService("DataStoreService")
local RunService = game:GetService("RunService")
local PathDataStore = DataStoreService:GetDataStore("PlayerPaths")

-- Configuration
local GHOST_DURATION = 5  -- seconds ghosts remain
local MAX_GHOSTS = 3       -- max ghosts at once
local FLOOD_THRESHOLD = 0.9

function MemoryFlooding.new(tensionSystem, player)
    local self = setmetatable({}, MemoryFlooding)
    self.TensionSystem = tensionSystem
    self.Player = player
    self.Ghosts = {}
    self.LastSpawnTime = 0
    self.SpawnInterval = 10  -- seconds between spawns
    return self
end

function MemoryFlooding:ShouldSpawn()
    local p = self.TensionSystem:getPredictability()
    local now = tick()
    return p > FLOOD_THRESHOLD and #self.Ghosts < MAX_GHOSTS and (now - self.LastSpawnTime) > self.SpawnInterval
end

function MemoryFlooding:SpawnGhost()
    self.LastSpawnTime = tick()
    
    -- Load a past player path from DataStore
    local pastPath = self:LoadRandomPath()
    
    if pastPath then
        self:CreateGhostFromPath(pastPath)
    else
        -- Fallback: create a random ghost
        self:CreateRandomGhost()
    end
end

function MemoryFlooding:LoadRandomPath()
    -- Get list of saved paths for this game
    local keys = PathDataStore:GetKeys("Path_")
    if not keys or #keys == 0 then return nil end
    
    local randomKey = keys[math.random(1, #keys)]
    local path = PathDataStore:GetAsync(randomKey)
    return path
end

function MemoryFlooding:SaveCurrentPath()
    -- Record player's path during this session
    local path = {}
    local connection
    local startTime = tick()
    
    connection = RunService.Heartbeat:Connect(function()
        local hrp = self.Player.Character and self.Player.Character:FindFirstChild("HumanoidRootPart")
        if hrp then
            table.insert(path, {pos = hrp.Position, time = tick() - startTime})
        end
    end)
    
    -- Save when player leaves or ruptures
    self.PathConnection = connection
end

function MemoryFlooding:CreateGhostFromPath(path)
    local ghost = Instance.new("Model")
    ghost.Name = "MemoryGhost"
    
    -- Create ghost character
    local part = Instance.new("Part")
    part.Size = Vector3.new(4, 6, 2)
    part.BrickColor = BrickColor.new("White")
    part.Material = Enum.Material.Neon
    part.Transparency = 0.7
    part.Anchored = true
    part.CanCollide = false
    part.Parent = ghost
    
    ghost.Parent = workspace
    
    -- Replay the path
    local startTime = tick()
    local pathIndex = 1
    local replayConnection
    
    replayConnection = RunService.Heartbeat:Connect(function()
        if not ghost.Parent then
            replayConnection:Disconnect()
            return
        end
        
        local elapsed = tick() - startTime
        while pathIndex <= #path and path[pathIndex].time <= elapsed do
            part.Position = path[pathIndex].pos
            pathIndex = pathIndex + 1
        end
        
        if pathIndex > #path then
            replayConnection:Disconnect()
            ghost:Destroy()
        end
    end)
    
    table.insert(self.Ghosts, ghost)
    
    -- Remove ghost after duration
    task.wait(GHOST_DURATION)
    ghost:Destroy()
    for i, g in ipairs(self.Ghosts) do
        if g == ghost then table.remove(self.Ghosts, i) end
    end
end

function MemoryFlooding:CreateRandomGhost()
    local ghost = Instance.new("Model")
    ghost.Name = "MemoryGhost"
    
    local part = Instance.new("Part")
    part.Size = Vector3.new(4, 6, 2)
    part.BrickColor = BrickColor.new("White")
    part.Material = Enum.Material.Neon
    part.Transparency = 0.7
    part.Anchored = true
    part.CanCollide = false
    part.Parent = ghost
    
    ghost.Parent = workspace
    
    -- Random wandering behavior
    local startPos = self.Player.Character and self.Player.Character:FindFirstChild("HumanoidRootPart")
    if startPos then
        part.Position = startPos.Position + Vector3.new(math.random(-20, 20), 0, math.random(-20, 20))
    end
    
    -- Wander in straight line
    local direction = Vector3.new(math.random(-1, 1), 0, math.random(-1, 1)).Unit
    local speed = 5
    
    local wanderConnection
    wanderConnection = RunService.Heartbeat:Connect(function(dt)
        if not ghost.Parent then
            wanderConnection:Disconnect()
            return
        end
        part.Position = part.Position + direction * speed * dt
    end)
    
    table.insert(self.Ghosts, ghost)
    
    task.wait(GHOST_DURATION)
    ghost:Destroy()
    wanderConnection:Disconnect()
    for i, g in ipairs(self.Ghosts) do
        if g == ghost then table.remove(self.Ghosts, i) end
    end
end

function MemoryFlooding:Update()
    if self:ShouldSpawn() then
        self:SpawnGhost()
    end
end

return MemoryFlooding
