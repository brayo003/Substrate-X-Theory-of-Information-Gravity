--[[
    Phase1Controller.server.lua
    Main controller for Phase 1 critical tasks
    Integrates Sanctuary and Stillness Trap systems
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

-- Dependencies
local Shared = ReplicatedStorage:WaitForChild("Shared")
local SystemManager = require(script.Parent.SystemManager)
local SanctuaryController = require(script.SanctuaryController)
local StillnessTrapController = require(script.StillnessTrapController)
-- Ensure gaze router is loaded so server receives client gaze inputs
local GazeRouter = require(script.Parent:FindFirstChild("GazeRouter") or script.Parent.GazeRouter)
local StateLogger = require(script.Parent:FindFirstChild("StateLogger") or script.Parent.StateLogger)

local Phase1Controller = {}
Phase1Controller.__index = Phase1Controller

-- Player systems
local PlayerSystems = {}

function Phase1Controller.init()
    print("Phase1Controller initializing...")
    SystemManager.init()
    
    -- Connect player joining/leaving
    Players.PlayerAdded:Connect(onPlayerAdded)
    Players.PlayerRemoving:Connect(onPlayerRemoving)
    
    -- Initialize existing players
    for _, player in ipairs(Players:GetPlayers()) do
        onPlayerAdded(player)
    end
    
    print("Phase1Controller initialized - Sanctuary Zone and Stillness Trap active")
end

function onPlayerAdded(player)
    print("Setting up Phase 1 systems for player:", player.Name)
    
    -- Wait for character
    player.CharacterAdded:Wait()
    
    -- Obtain authoritative player state from SystemManager
    local ps = SystemManager and SystemManager.getPlayerState(player)
    if not ps then
        warn("Phase1Controller: PlayerState not yet available for", player.Name)
        return
    end

    local sanctuaryController = SanctuaryController.new(player, ps)
    local stillnessTrapController = StillnessTrapController.new(player, ps)

    PlayerSystems[player.UserId] = {
        playerState = ps,
        sanctuaryController = sanctuaryController,
        stillnessTrapController = stillnessTrapController
    }
end

function onPlayerRemoving(player)
    print("Cleaning up Phase 1 systems for player:", player.Name)
    
    local systems = PlayerSystems[player.UserId]
    if systems then
        -- Clean up controllers
        if systems.sanctuaryController then
            systems.sanctuaryController:destroy()
        end
        if systems.stillnessTrapController then
            systems.stillnessTrapController:destroy()
        end
        
        PlayerSystems[player.UserId] = nil
    end
end

function Phase1Controller.getPlayerSystems(player)
    return PlayerSystems[player.UserId]
end

return Phase1Controller
