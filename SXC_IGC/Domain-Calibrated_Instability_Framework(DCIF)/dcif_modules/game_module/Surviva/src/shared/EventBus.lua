local EventBus = {}
EventBus.__index = EventBus

function EventBus.new()
    local self = setmetatable({}, EventBus)
    self.listeners = {}
    return self
end

function EventBus:subscribe(eventName, fn)
    self.listeners[eventName] = self.listeners[eventName] or {}
    table.insert(self.listeners[eventName], fn)
end

function EventBus:emit(eventName, ...)
    local list = self.listeners[eventName]
    if not list then return end
    for _, fn in ipairs(list) do
        -- protected call to ensure bus stability
        local ok, err = pcall(fn, ...)
        if not ok then
            warn("EventBus handler error on", eventName, err)
        end
    end
end

return EventBus
