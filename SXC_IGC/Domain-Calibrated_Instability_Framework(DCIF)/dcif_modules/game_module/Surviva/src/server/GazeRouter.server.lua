-- Server-side router to accept client gaze reports and forward them to PredictionField instances
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")

local remote = ReplicatedStorage:FindFirstChild("V12_Gaze") or Instance.new("RemoteEvent")
remote.Name = "V12_Gaze"
remote.Parent = ReplicatedStorage

local SystemManager = require(script.Parent.SystemManager)

local GazeRouter = {}
GazeRouter.__index = GazeRouter

function GazeRouter.init()
    if GazeRouter._init then return end
    GazeRouter._init = true

    remote.OnServerEvent:Connect(function(player, gazeData)
        -- gazeData expected: {Position = Vector3, LookVector = Vector3, Timestamp = number}
        local ps = SystemManager:getPlayerState(player)
        if not ps or not ps.PredictionField or not ps.PredictionField.receiveGaze then return end
        -- Forward gaze data to the player's PredictionField instance
        pcall(function() ps.PredictionField:receiveGaze(gazeData) end)
    end)
end

GazeRouter.init()

return GazeRouter
