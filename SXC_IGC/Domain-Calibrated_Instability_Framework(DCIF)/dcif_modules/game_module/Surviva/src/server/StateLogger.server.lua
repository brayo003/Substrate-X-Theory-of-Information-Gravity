local RunService = game:GetService("RunService")
local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local SystemManager = require(script.Parent.SystemManager)

local StateLogger = {}
StateLogger.__index = StateLogger

local SAMPLE_INTERVAL = 10 -- seconds
local SUMMARY_TIMES = {60, 120} -- seconds to print summary heuristics

local startTime = tick()
local snapshots = {} -- snapshots[playerUserId] = { {t=secs, M=, P=, T=}, ... }

local function sampleOnce()
    local now = tick()
    local elapsed = math.floor(now - startTime)

    for _, player in ipairs(Players:GetPlayers()) do
        local ps = SystemManager:getPlayerState(player)
        if ps then
            local M = 0
            local P = 0
            local T = 0
            -- Prefer direct getters when available
            if ps.MemoryField and ps.MemoryField.getAverageMemory then
                pcall(function() M = ps.MemoryField:getAverageMemory() end)
            else
                M = ps.Metrics and ps.Metrics.AverageMemory or 0
            end
            if ps.PredictionField and ps.PredictionField.getGlobalPredictability then
                pcall(function() P = ps.PredictionField:getGlobalPredictability() end)
            else
                P = ps.Metrics and ps.Metrics.Predictability or 0
            end
            if ps.TensionEngine and ps.TensionEngine.getTension then
                pcall(function() T = ps.TensionEngine:getTension() end)
            else
                T = ps.Metrics and ps.Metrics.Tension or 0
            end

            snapshots[player.UserId] = snapshots[player.UserId] or {}
            table.insert(snapshots[player.UserId], { t = elapsed, M = M, P = P, T = T })
        end
    end

    -- Print compact per-player snapshot
    print(string.format("[StateLogger] Time %ds — Snapshot:" , elapsed))
    for userId, hist in pairs(snapshots) do
        local last = hist[#hist]
        if last then
            print(string.format("  Player %d: M=%.4f P=%.4f T=%.4f", userId, last.M, last.P, last.T))
        end
    end

    -- If we've reached any summary times, compute heuristics
    for _, S in ipairs(SUMMARY_TIMES) do
        if elapsed == S then
            print(string.format("[StateLogger] === Summary @ %ds ===", S))
            for userId, hist in pairs(snapshots) do
                local t0 = hist[1]
                local tN = hist[#hist]
                if t0 and tN then
                    local deltaM = tN.M - t0.M
                    local deltaP = tN.P - t0.P
                    local deltaT = tN.T - t0.T

                    local mem_answer = (deltaM > 0.005) and "YES" or "NO"
                    local pred_answer = (deltaP > 0.005) and "YES" or "NO"
                    local tense_answer = ((deltaT > 0.005) and (deltaM > 0 or deltaP > 0)) and "YES" or "NO"

                    -- Stalker detection: look for ghost or real stalker parts in workspace
                    local stalker_found = false
                    for _, obj in ipairs(workspace:GetDescendants()) do
                        if obj and obj.Name and (string.find(obj.Name, "GhostStalker") or string.find(obj.Name, "RealStalker")) then
                            stalker_found = true
                            break
                        end
                    end
                    local stalker_answer = stalker_found and "YES" or "NO"

                    -- Feedback is manual; logger cannot reliably infer player subjective change
                    local feedback_answer = "MANUAL"

                    print(string.format("  Player %d — Memory: %s (Δ=%.4f), Prediction: %s (Δ=%.4f), Tension: %s (Δ=%.4f), Stalker: %s, Feedback: %s",
                        userId, mem_answer, deltaM, pred_answer, deltaP, tense_answer, deltaT, stalker_answer, feedback_answer))
                end
            end
            print(string.format("[StateLogger] === End Summary @ %ds ===", S))
        end
    end
end

-- Start sampling loop (non-blocking)
spawn(function()
    while true do
        pcall(sampleOnce)
        task.wait(SAMPLE_INTERVAL)
    end
end)

return StateLogger
