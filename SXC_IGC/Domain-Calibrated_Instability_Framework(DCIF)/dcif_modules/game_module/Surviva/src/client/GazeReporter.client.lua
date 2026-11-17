local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

local remote = ReplicatedStorage:WaitForChild("V12_Gaze") -- assume created by server
local player = Players.LocalPlayer

spawn(function()
    while not player do
        player = Players.LocalPlayer
        task.wait(0.1)
    end
    while true do
        local char = player.Character
        if char and workspace.CurrentCamera then
            local userId = player.UserId
            local look = workspace.CurrentCamera.CFrame.LookVector
            local pos = char:FindFirstChild("HumanoidRootPart") and char.HumanoidRootPart.Position or Vector3.new()
            -- send minimal gaze report (non-sensitive)
            pcall(function()
                remote:FireServer({ UserId = userId, Position = pos, LookVector = look, Timestamp = tick() })
            end)
        end
        task.wait(0.5)
    end
end)
