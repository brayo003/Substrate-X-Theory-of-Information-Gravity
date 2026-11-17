--[[
    BookMutations.server.lua
    Phase 5 Critical Task: Mislearning Mutations
    
    Book becomes unreliable at high T, P(correct) < 1
    When T_sys > 1.0, book entries mutate and give wrong advice
    Player must learn to ignore the book at high tension
]]

local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Players = game:GetService("Players")
local RunService = game:GetService("RunService")

-- Dependencies
local Shared = ReplicatedStorage:WaitForChild("Shared")
-- BookMutations consumes PlayerState (authoritative) instead of requiring TensionEngine directly

-- Remote for client effects
local remote = ReplicatedStorage:FindFirstChild("V12_Sync") or Instance.new("RemoteEvent")
remote.Name = "V12_Sync"
remote.Parent = ReplicatedStorage

local BookMutations = {}
BookMutations.__index = BookMutations

-- Mutation parameters
local MUTATION_CONFIG = {
    mutationThreshold = 1.0,         -- T_sys threshold for mutations
    mutationProbability = 0.7,       -- Chance of mutation when above threshold
    mutationCheckInterval = 2.0,     -- How often to check for mutations
    textWarpIntensity = 0.8,         -- How much text warps
    colorShiftProbability = 0.6,     -- Chance of color shifting
    falseAdviceProbability = 0.5,    -- Chance of giving false advice
    mutationDuration = 10.0          -- How long mutations last
}

-- Original book entries (should match BookController)
local ORIGINAL_ENTRIES = {
    memory_first = "You remember this place. The world remembers with you.",
    belief_first = "Your belief becomes real.",
    identity_first = "You move like it.",
    sanctuary_first = "It remembers where you hide.",
    memory_growth = "The forest remembers your steps.",
    prediction_strength = "Your belief shapes reality.",
    sanctuary_decay = "The sanctuary remembers your fear.",
    path_punishment = "Walk where you have not."
}

-- Mutation templates
local MUTATION_TEMPLATES = {
    memory_first = {
        "You remember nothing. The world forgets you.",
        "This place remembers you too well.",
        "Forget what you remember. Start over."
    },
    belief_first = {
        "Your doubts become real. Believe nothing.",
        "Reality rejects your beliefs.",
        "What you believe is false."
    },
    identity_first = {
        "You become yourself. It copies you perfectly.",
        "You move differently. It adapts instantly.",
        "Identity is meaningless. You are becoming it."
    },
    sanctuary_first = {
        "It knows exactly where you hide. Stay out forever.",
        "Sanctuary welcomes it as much as you.",
        "Your hiding places are obvious."
    },
    memory_growth = {
        "The forest erases your steps. Go back where you came.",
        "Your path is remembered. Take it again.",
        "Memory grows in safe places. Avoid them."
    },
    prediction_strength = {
        "Your predictions fail. Trust nothing you think.",
        "Reality mocks your beliefs.",
        "What you expect is exactly what won't happen."
    },
    sanctuary_decay = {
        "The sanctuary loves your fear. Stay longer.",
        "Fear strengthens the sanctuary. Embrace it.",
        "The sanctuary feeds on your terror."
    },
    path_punishment = {
        "Return to familiar paths. They protect you.",
        "Walk where you remember. It's safe there.",
        "Repetition brings safety. Do it again."
    }
}

function BookMutations.new(player, playerState, bookController)
    local self = setmetatable({}, BookMutations)

    self.Player = player
    self.PlayerState = playerState
    self.TensionEngine = playerState and playerState.TensionEngine
    self.BookController = bookController
    
    -- Mutation state
    self.MutationsActive = false
    self.ActiveMutations = {}
    self.LastMutationCheck = 0
    self.MutationHistory = {}
    
    -- Connect events
    self:connectEvents()
    
    print("BookMutations initialized for player:", player.Name)
    return self
end

function BookMutations:connectEvents()
    -- Check for mutations periodically
    RunService.Heartbeat:Connect(function(dt)
        self:updateMutations(dt)
    end)
end

function BookMutations:updateMutations(dt)
    local now = tick()
    local tension = self.TensionEngine:getTension()
    
    -- Check if mutations should be active
    local shouldBeActive = tension >= MUTATION_CONFIG.mutationThreshold
    local wasActive = self.MutationsActive
    
    if shouldBeActive and not wasActive then
        self:activateMutations()
    elseif not shouldBeActive and wasActive then
        self:deactivateMutations()
    end
    
    -- Update active mutations
    if self.MutationsActive then
        self:updateActiveMutations(dt)
    end
    
    -- Periodic mutation checks
    if now - self.LastMutationCheck >= MUTATION_CONFIG.mutationCheckInterval then
        self:checkForNewMutations()
        self.LastMutationCheck = now
    end
end

function BookMutations:activateMutations()
    print("Book mutations activated for player:", self.Player.Name)
    self.MutationsActive = true
    
    -- Send client notification
    remote:FireClient(self.Player, "book_mutations_activate")
    
    -- Initial mutation sweep
    self:mutateAllEntries()
end

function BookMutations:deactivateMutations()
    print("Book mutations deactivated for player:", self.Player.Name)
    self.MutationsActive = false
    
    -- Restore all entries to original
    self:restoreAllEntries()
    
    -- Send client notification
    remote:FireClient(self.Player, "book_mutations_deactivate")
end

function BookMutations:checkForNewMutations()
    if not self.MutationsActive then return end
    
    -- Random chance to mutate entries
    if math.random() < MUTATION_CONFIG.mutationProbability then
        self:mutateRandomEntry()
    end
end

function BookMutations:mutateAllEntries()
    -- Mutate all unlocked entries
    for entryId, _ in pairs(ORIGINAL_ENTRIES) do
        if self:isEntryUnlocked(entryId) then
            self:mutateEntry(entryId)
        end
    end
end

function BookMutations:mutateRandomEntry()
    -- Get list of unlocked entries
    local unlockedEntries = {}
    for entryId, _ in pairs(ORIGINAL_ENTRIES) do
        if self:isEntryUnlocked(entryId) then
            table.insert(unlockedEntries, entryId)
        end
    end
    
    if #unlockedEntries == 0 then return end
    
    -- Pick random entry to mutate
    local randomIndex = math.random(1, #unlockedEntries)
    local entryId = unlockedEntries[randomIndex]
    
    self:mutateEntry(entryId)
end

function BookMutations:mutateEntry(entryId)
    if not MUTATION_TEMPLATES[entryId] then return end
    
    -- Get mutation options
    local mutations = MUTATION_TEMPLATES[entryId]
    if #mutations == 0 then return end
    
    -- Pick random mutation
    local mutationIndex = math.random(1, #mutations)
    local mutatedText = mutations[mutationIndex]
    
    -- Apply mutation to book controller
    self:setBookEntryText(entryId, mutatedText)
    
    -- Track active mutation
    self.ActiveMutations[entryId] = {
        originalText = ORIGINAL_ENTRIES[entryId],
        mutatedText = mutatedText,
        startTime = tick(),
        mutationIndex = mutationIndex
    }
    
    -- Send mutation notification to client
    remote:FireClient(self.Player, "book_entry_mutate", {
        entryId = entryId,
        mutatedText = mutatedText,
        mutationType = "text_warp"
    })
    
    print("Mutated book entry:", entryId, "to:", mutatedText)
end

function BookMutations:updateActiveMutations(dt)
    local now = tick()
    local expiredMutations = {}
    
    -- Check for expired mutations
    for entryId, mutation in pairs(self.ActiveMutations) do
        if now - mutation.startTime >= MUTATION_CONFIG.mutationDuration then
            table.insert(expiredMutations, entryId)
        end
    end
    
    -- Restore expired mutations
    for _, entryId in ipairs(expiredMutations) do
        self:restoreEntry(entryId)
    end
end

function BookMutations:restoreEntry(entryId)
    local mutation = self.ActiveMutations[entryId]
    if not mutation then return end
    
    -- Restore original text
    self:setBookEntryText(entryId, mutation.originalText)
    
    -- Remove from active mutations
    self.ActiveMutations[entryId] = nil
    
    -- Send restoration notification to client
    remote:FireClient(self.Player, "book_entry_restore", {
        entryId = entryId,
        originalText = mutation.originalText
    })
    
    print("Restored book entry:", entryId)
end

function BookMutations:restoreAllEntries()
    -- Restore all mutated entries
    for entryId, mutation in pairs(self.ActiveMutations) do
        self:setBookEntryText(entryId, mutation.originalText)
    end
    
    self.ActiveMutations = {}
end

function BookMutations:setBookEntryText(entryId, text)
    -- Interface with BookController to set entry text
    if self.BookController and self.BookController.SetEntryText then
        self.BookController:SetEntryText(entryId, text)
    end
end

function BookMutations:isEntryUnlocked(entryId)
    -- Check if entry is unlocked in BookController
    if self.BookController and self.BookController.IsEntryUnlocked then
        return self.BookController:IsEntryUnlocked(entryId)
    end
    return true -- Assume unlocked if no controller available
end

function BookMutations:getMutationProbability(entryId)
    -- Calculate mutation probability based on tension and entry type
    local tension = self.TensionEngine:getTension()
    local baseProbability = MUTATION_CONFIG.mutationProbability
    
    -- Higher tension = higher mutation probability
    local tensionMultiplier = math.clamp(tension / MUTATION_CONFIG.mutationThreshold, 1, 2)
    
    -- Some entries mutate more easily
    local entryMultiplier = 1.0
    if entryId:find("sanctuary") then
        entryMultiplier = 1.2 -- Sanctuary entries mutate more
    elseif entryId:find("prediction") then
        entryMultiplier = 1.3 -- Prediction entries mutate more
    end
    
    return math.min(1.0, baseProbability * tensionMultiplier * entryMultiplier)
end

function BookMutations:getCurrentMutations()
    -- Return current mutation state
    local mutations = {}
    for entryId, mutation in pairs(self.ActiveMutations) do
        mutations[entryId] = {
            mutatedText = mutation.mutatedText,
            timeRemaining = MUTATION_CONFIG.mutationDuration - (tick() - mutation.startTime)
        }
    end
    return mutations
end

function BookMutations:forceMutation(entryId)
    -- Debug function to force a mutation
    if ORIGINAL_ENTRIES[entryId] then
        self:mutateEntry(entryId)
    end
end

function BookMutations:forceRestore(entryId)
    -- Debug function to force a restore
    self:restoreEntry(entryId)
end

function BookMutations:destroy()
    -- Clean up all mutations
    self:restoreAllEntries()
    
    print("BookMutations destroyed for player:", self.Player.Name)
end

return BookMutations
