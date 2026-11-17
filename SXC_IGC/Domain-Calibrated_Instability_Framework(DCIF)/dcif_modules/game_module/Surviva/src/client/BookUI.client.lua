-- BookUI.client.lua
-- Displays Book entries, predictions, and visual effects

local Player = game.Players.LocalPlayer
local PlayerGui = Player:WaitForChild("PlayerGui")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local UserInputService = game:GetService("UserInputService")
local TweenService = game:GetService("TweenService")

local tensionEvent = ReplicatedStorage:WaitForChild("V12_Sync")

-- Create Book UI Frame (hidden by default)
local BookFrame = Instance.new("Frame")
BookFrame.Name = "BookUI"
BookFrame.Size = UDim2.new(0, 400, 0, 500)
BookFrame.Position = UDim2.new(0.5, -200, 0.5, -250)
BookFrame.BackgroundColor3 = Color3.new(0.1, 0.05, 0.05)
BookFrame.BackgroundTransparency = 0.1
BookFrame.BorderSizePixel = 2
BookFrame.BorderColor3 = Color3.new(0.5, 0.3, 0.1)
BookFrame.Visible = false
BookFrame.Parent = PlayerGui

-- Book title
local Title = Instance.new("TextLabel", BookFrame)
Title.Size = UDim2.new(1, 0, 0, 40)
Title.Position = UDim2.new(0, 0, 0, 0)
Title.BackgroundTransparency = 1
Title.TextColor3 = Color3.new(0.8, 0.6, 0.3)
Title.Text = "THE SUBSTRATE CHRONICLES"
Title.Font = Enum.Font.GothamBold
Title.TextSize = 18

-- Entry display area
local EntryFrame = Instance.new("ScrollingFrame", BookFrame)
EntryFrame.Size = UDim2.new(0.9, 0, 0.7, 0)
EntryFrame.Position = UDim2.new(0.05, 0, 0.1, 0)
EntryFrame.BackgroundTransparency = 1
EntryFrame.CanvasSize = UDim2.new(0, 0, 0, 0)
EntryFrame.ScrollBarThickness = 5

local EntryList = Instance.new("UIListLayout", EntryFrame)
EntryList.SortOrder = Enum.SortOrder.LayoutOrder
EntryList.Padding = UDim.new(0, 10)

-- Prediction popup (temporary)
local PredictionFrame = Instance.new("Frame", PlayerGui)
PredictionFrame.Size = UDim2.new(0, 300, 0, 60)
PredictionFrame.Position = UDim2.new(0.5, -150, 0.7, 0)
PredictionFrame.BackgroundColor3 = Color3.new(0, 0, 0)
PredictionFrame.BackgroundTransparency = 0.3
PredictionFrame.BorderSizePixel = 1
PredictionFrame.BorderColor3 = Color3.new(0.8, 0.2, 0.2)
PredictionFrame.Visible = false

local PredictionText = Instance.new("TextLabel", PredictionFrame)
PredictionText.Size = UDim2.new(1, 0, 1, 0)
PredictionText.BackgroundTransparency = 1
PredictionText.TextColor3 = Color3.new(1, 1, 1)
PredictionText.Text = ""
PredictionText.TextWrapped = true

-- Toggle Book with 'B' key
UserInputService.InputBegan:Connect(function(input, gameProcessed)
    if gameProcessed then return end
    if input.KeyCode == Enum.KeyCode.B then
        BookFrame.Visible = not BookFrame.Visible
        if BookFrame.Visible then
            -- Request latest entries from server (optional)
            local remote = ReplicatedStorage:FindFirstChild("V12_Sync")
            if remote then
                remote:FireServer("request_book_entries")
            end
        end
    end
end)

-- Add an entry to the Book UI
local function addBookEntry(text, entryType)
    local entry = Instance.new("TextLabel")
    entry.Size = UDim2.new(1, 0, 0, 40)
    entry.BackgroundTransparency = 1
    entry.TextColor3 = (entryType == "prescriptive" and Color3.new(1, 0.5, 0.5)) or (entryType == "interpretive" and Color3.new(0.8, 0.8, 0.5)) or Color3.new(0.7, 0.7, 0.7)
    entry.Text = text
    entry.TextWrapped = true
    entry.TextXAlignment = Enum.TextXAlignment.Left
    entry.Font = Enum.Font.Gotham
    entry.TextSize = 14
    entry.Parent = EntryFrame
    
    -- Animate entry appearance
    entry.BackgroundTransparency = 1
    local tween = TweenService:Create(entry, TweenInfo.new(0.3), {BackgroundTransparency = 1})
    tween:Play()
    
    -- Update canvas size
    task.wait(0.05)
    EntryFrame.CanvasSize = UDim2.new(0, 0, 0, EntryList.AbsoluteContentSize.Y + 20)
end

-- Show prediction popup
local function showPrediction(text)
    PredictionText.Text = text
    PredictionFrame.Visible = true
    PredictionFrame.BackgroundTransparency = 0.3
    
    local tween = TweenService:Create(PredictionFrame, TweenInfo.new(0.2), {BackgroundTransparency = 0})
    tween:Play()
    
    task.wait(3)
    
    local outTween = TweenService:Create(PredictionFrame, TweenInfo.new(0.5), {BackgroundTransparency = 0.3})
    outTween:Play()
    task.wait(0.5)
    PredictionFrame.Visible = false
end

-- Handle remote events
tensionEvent.OnClientEvent:Connect(function(eventName, ...)
    if eventName == "book_entry" then
        local text, entryType = ...
        addBookEntry(text, entryType)
    elseif eventName == "book_prediction" then
        local prediction = ...
        showPrediction(prediction)
    elseif eventName == "artifact_collected" then
        local artifactName, lore = ...
        addBookEntry("[" .. artifactName .. "]\n" .. lore, "observational")
        -- Optional: play sound effect
    elseif eventName == "artifact_lost" then
        local artifactId = ...
        addBookEntry("You have lost an artifact: " .. artifactId, "prescriptive")
    end
end)

print("BookUI is online")
