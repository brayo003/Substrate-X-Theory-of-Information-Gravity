-- Minimal MemoryField implementation to satisfy runtime APIs used by server controllers.
local MemoryField = {}
MemoryField.__index = MemoryField

-- Configurable defaults (kept small and deterministic)
local DEFAULT = {
    gridSize = 10,          -- studs per cell
    gridX = 50,
    gridZ = 50,
    decayRate = 0.995,      -- per-second multiplicative decay
    initialValue = 0.0
}

function MemoryField.new(opts)
    opts = opts or {}
    local self = setmetatable({}, MemoryField)

    self.GridSize = opts.gridSize or DEFAULT.gridSize
    self.GridDimensions = { x = opts.gridX or DEFAULT.gridX, z = opts.gridZ or DEFAULT.gridZ }
    self.DecayRate = opts.decayRate or DEFAULT.decayRate

    -- Growth and signal multipliers that controllers can set
    self._growthMultiplier = 1.0
    self._signalMultiplier = 1.0

    -- Initialize grid (1-indexed tables matching other modules' expectations)
    self.Grid = {}
    for x = 1, self.GridDimensions.x do
        self.Grid[x] = {}
        for z = 1, self.GridDimensions.z do
            self.Grid[x][z] = { M = DEFAULT.initialValue, lastUpdate = tick() }
        end
    end

    return self
end

-- Convert world coordinates to grid indices
function MemoryField:worldToGrid(worldX, worldZ)
    local halfWidth = (self.GridDimensions.x * self.GridSize) / 2
    local halfDepth = (self.GridDimensions.z * self.GridSize) / 2

    local gridX = math.floor((worldX + halfWidth) / self.GridSize) + 1
    local gridZ = math.floor((worldZ + halfDepth) / self.GridSize) + 1

    gridX = math.max(1, math.min(self.GridDimensions.x, gridX))
    gridZ = math.max(1, math.min(self.GridDimensions.z, gridZ))
    return gridX, gridZ
end

function MemoryField:gridToWorld(gridX, gridZ)
    local worldX = (gridX - 1) * self.GridSize - (self.GridDimensions.x * self.GridSize) / 2
    local worldZ = (gridZ - 1) * self.GridSize - (self.GridDimensions.z * self.GridSize) / 2
    return worldX, worldZ
end

-- Add memory at a world Vector3 position (amount can be negative)
function MemoryField:addMemoryAtPosition(position, amount)
    if not position or not amount then return end
    local gridX, gridZ = self:worldToGrid(position.X, position.Z)
    local cell = self.Grid[gridX] and self.Grid[gridX][gridZ]
    if not cell then return end
    cell.M = math.max(0, cell.M + (amount * (self._growthMultiplier or 1)))
    cell.lastUpdate = tick()
end

-- Get memory value at world coords (0..inf)
function MemoryField:getMemoryAt(worldX, worldZ)
    local gridX, gridZ = self:worldToGrid(worldX, worldZ)
    local cell = self.Grid[gridX] and self.Grid[gridX][gridZ]
    if not cell then return 0 end
    return cell.M or 0
end

-- Return highest M location as (Vector3 position, value)
function MemoryField:getHighestMLocation()
    local best = 0
    local bx, bz = 1, 1
    for x = 1, self.GridDimensions.x do
        for z = 1, self.GridDimensions.z do
            local v = (self.Grid[x] and self.Grid[x][z] and self.Grid[x][z].M) or 0
            if v > best then
                best = v
                bx, bz = x, z
            end
        end
    end
    local wx, wz = self:gridToWorld(bx, bz)
    return Vector3.new(wx, 0, wz), best
end

-- Average memory across grid (0..1 expected scale in gameplay code)
function MemoryField:getAverageMemory()
    local sum = 0
    local count = 0
    for x = 1, self.GridDimensions.x do
        for z = 1, self.GridDimensions.z do
            sum = sum + ((self.Grid[x] and self.Grid[x][z] and self.Grid[x][z].M) or 0)
            count = count + 1
        end
    end
    if count == 0 then return 0 end
    return sum / count
end

-- Per-frame update: apply decay
function MemoryField:update(dt)
    -- apply multiplicative decay scaled by dt
    local decayFactor = math.pow(self.DecayRate, math.max(0, dt))
    for x = 1, self.GridDimensions.x do
        for z = 1, self.GridDimensions.z do
            local cell = self.Grid[x] and self.Grid[x][z]
            if cell then
                cell.M = cell.M * decayFactor
            end
        end
    end
end

function MemoryField:setGrowthMultiplier(mult)
    self._growthMultiplier = tonumber(mult) or 1.0
end

function MemoryField:getGrowthMultiplier()
    return self._growthMultiplier or 1.0
end

function MemoryField:setSignalMultiplier(mult)
    self._signalMultiplier = tonumber(mult) or 1.0
end

function MemoryField:destroy()
    -- best-effort cleanup
    self.Grid = nil
    self.GridDimensions = nil
    self.GridSize = nil
end

return MemoryField
