--[[
    Phase2Controller.server.lua
    Main controller for Phase 2 critical tasks
    Integrates Prediction Field and Stalker Superposition
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

-- Dependencies
local Shared = ReplicatedStorage:WaitForChild("Shared")
local SystemManager = require(script.Parent.SystemManager)
local StalkerSuperposition = require(script.Parent.StalkerSuperposition)
local BlendMP = require(script.Parent.BlendMP)

local Phase2Controller = {}
Phase2Controller.__index = Phase2Controller

-- Player systems
local PlayerSystems = {}

function Phase2Controller.init()
    print("Phase2Controller initializing...")
    SystemManager.init()
    
    -- Connect player joining/leaving
    Players.PlayerAdded:Connect(onPlayerAdded)
    Players.PlayerRemoving:Connect(onPlayerRemoving)
    
    -- Initialize existing players
    for _, player in ipairs(Players:GetPlayers()) do
        onPlayerAdded(player)
    end
    
    print("Phase2Controller initialized - Prediction Field and Stalker Superposition active")
end

function onPlayerAdded(player)
    print("Setting up Phase 2 systems for player:", player.Name)
    
    -- Wait for character
    player.CharacterAdded:Wait()
    
    -- Obtain authoritative player state
    local ps = SystemManager and SystemManager.getPlayerState(player)
    if not ps then
        warn("Phase2Controller: PlayerState not yet available for", player.Name)
        return
    end

    local stalkerSuperposition = StalkerSuperposition.new(player, ps)
    local blendMP = BlendMP.new(player, ps)

    PlayerSystems[player.UserId] = {
        playerState = ps,
        stalkerSuperposition = stalkerSuperposition,
        blendMP = blendMP
    }
end

function onPlayerRemoving(player)
    print("Cleaning up Phase 2 systems for player:", player.Name)
    
    local systems = PlayerSystems[player.UserId]
    if systems then
        -- Clean up controllers
        if systems.stalkerSuperposition then
            systems.stalkerSuperposition:destroy()
        end
        if systems.blendMP then
            systems.blendMP:destroy()
        end
        
        PlayerSystems[player.UserId] = nil
    end
end

function Phase2Controller.getPlayerSystems(player)
    return PlayerSystems[player.UserId]
end

function Phase2Controller.activateSuperpositionForPlayer(player)
    local systems = PlayerSystems[player.UserId]
    if systems and systems.stalkerSuperposition then
        systems.stalkerSuperposition:activateSuperposition()
    end
end

function Phase2Controller.deactivateSuperpositionForPlayer(player)
    local systems = PlayerSystems[player.UserId]
    if systems and systems.stalkerSuperposition then
        systems.stalkerSuperposition:deactivateSuperposition()
    end
end

return Phase2Controller
