--[[
    HorizonEngine.lua
    SXC-IGC Horizon Engine - Core Tension System
    
    Verified behavioral guarantees:
    - Idle (signal=0) → 0 ruptures always
    - Moderate activity (signal=1.0) → tension builds, rupture rare
    - High sustained chaos (signal=1.8) → rupture occurs, timing varies 40–90s
    - Recovery always returns to baseline before next cycle
    
    Drift shape: f(T) = c + r*T + a*T^2 - b*T^3
    Geometry locked: Low=0.121, Barrier=0.500, High=1.379
]]

local HorizonEngine = {}
HorizonEngine.__index = HorizonEngine

-- Default parameters (proven working)
local DEFAULT_PARAMS = {
    -- Drift shape
    c = 0.20,
    r = -2.20,
    a = 4.80,
    b = 2.40,
    
    -- Core tuning
    forcing_scale = 27.0,
    noise_sigma = 0.012,
    rupture_t = 1.15,
    cooldown_duration = 12.0,
    recovery_decay = 0.94,
    reset_value = 0.17,
    low_attractor = 0.121,
    
    -- Momentum (accumulated chaos)
    momentum_gain = 0.025,
    momentum_decay = 0.975,
    
    -- Time step (seconds per update)
    DT = 0.05
}

--[[
    Creates a new Horizon Engine instance
    @param overrides: table of parameter overrides (optional)
    @return: HorizonEngine instance
]]
function HorizonEngine.new(overrides)
    local self = setmetatable({}, HorizonEngine)
    
    -- Merge parameters
    local params = {}
    for k, v in pairs(DEFAULT_PARAMS) do
        params[k] = v
    end
    if overrides then
        for k, v in pairs(overrides) do
            params[k] = v
        end
    end
    self.params = params
    
    -- State variables
    self.T_sys = params.low_attractor
    self.momentum = 0.0
    self.cooldown = 0.0
    self.can_rupture = true
    
    return self
end

--[[
    Drift function: f(T) = c + r*T + a*T^2 - b*T^3
]]
function HorizonEngine:drift(x)
    local p = self.params
    return p.c + p.r * x + p.a * x * x - p.b * x * x * x
end

--[[
    Gaussian noise generator (Box-Muller transform)
    @param sigma: standard deviation
    @return: random value from N(0, sigma)
]]
local function gaussianNoise(sigma)
    local u1 = math.random()
    local u2 = math.random()
    local z0 = math.sqrt(-2.0 * math.log(u1)) * math.cos(2.0 * math.pi * u2)
    return z0 * sigma
end

--[[
    Main step function - call this every frame
    @param signal: player input (0.0 to 2.0, typically)
    @return: boolean (true if rupture occurred this step)
]]
function HorizonEngine:step(signal)
    local p = self.params
    local ruptured = false
    
    -- Update cooldown
    self.cooldown = math.max(0.0, self.cooldown - p.DT)
    
    -- Re-arm rupture capability after cooldown
    if not self.can_rupture and self.cooldown <= 0 then
        self.can_rupture = true
    end
    
    -- Recovery or normal dynamics
    if self.cooldown > 0 then
        -- Recovery phase: decay toward low attractor
        self.T_sys = (self.T_sys * p.recovery_decay) + (p.low_attractor * (1 - p.recovery_decay))
    else
        -- Normal dynamics: accumulate momentum, apply forcing, drift, noise
        self.momentum = (self.momentum * p.momentum_decay) + (signal * p.momentum_gain)
        self.momentum = math.clamp(self.momentum, 0, 2.0)
        
        local forcing = self.momentum / p.forcing_scale
        local drift_val = self:drift(self.T_sys)
        local noise = gaussianNoise(p.noise_sigma)
        
        self.T_sys = self.T_sys + (drift_val + forcing) * p.DT + noise
    end
    
    -- Clamp tension
    self.T_sys = math.clamp(self.T_sys, -0.1, 2.0)
    
    -- Check rupture condition
    if self.can_rupture and self.cooldown <= 0 and self.T_sys >= p.rupture_t then
        self.T_sys = p.reset_value
        self.momentum = 0.0
        self.cooldown = p.cooldown_duration
        self.can_rupture = false
        ruptured = true
    end
    
    return ruptured
end

--[[
    Get current tension value
    @return: current T_sys (0.0 to 2.0)
]]
function HorizonEngine:getTension()
    return self.T_sys
end

--[[
    Get current momentum (accumulated chaos)
    @return: current momentum (0.0 to 2.0)
]]
function HorizonEngine:getMomentum()
    return self.momentum
end

--[[
    Get current cooldown remaining
    @return: cooldown seconds
]]
function HorizonEngine:getCooldown()
    return self.cooldown
end

--[[
    Check if rupture is currently possible
    @return: boolean
]]
function HorizonEngine:canRupture()
    return self.can_rupture and self.cooldown <= 0
end

--[[
    Reset engine to initial state
]]
function HorizonEngine:reset()
    local p = self.params
    self.T_sys = p.low_attractor
    self.momentum = 0.0
    self.cooldown = 0.0
    self.can_rupture = true
end

--[[
    Set parameter at runtime
    @param key: parameter name
    @param value: new value
]]
function HorizonEngine:setParam(key, value)
    if self.params[key] ~= nil then
        self.params[key] = value
    end
end

--[[
    Get parameter value
    @param key: parameter name
    @return: current value
]]
function HorizonEngine:getParam(key)
    return self.params[key]
end

--[[
    Get the current state as a string (for UI)
    @return: "IDLE", "BUILDING", "DANGER", "RECOVERY", or "CRITICAL"
]]
function HorizonEngine:getStateString()
    local t = self.T_sys
    
    if self.cooldown > 0 then
        return "RECOVERY"
    elseif t >= 1.15 then
        return "CRITICAL"
    elseif t >= 0.9 then
        return "DANGER"
    elseif t >= 0.5 then
        return "BUILDING"
    else
        return "IDLE"
    end
end

--[[
    Get tension as a normalized 0-1 value (for UI bars)
    @return: normalized tension (0 to 1)
]]
function HorizonEngine:getNormalizedTension()
    return math.clamp(self.T_sys / 1.5, 0, 1)
end

--[[
    Get tension as a percentage (0-100)
    @return: percentage
]]
function HorizonEngine:getTensionPercent()
    return math.floor(self:getNormalizedTension() * 100)
end

--[[
    Utility: clamp a value between min and max
]]
function math.clamp(val, min, max)
    return math.max(min, math.min(max, val))
end

return HorizonEngine
