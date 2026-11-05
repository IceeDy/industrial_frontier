local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")
local Workspace = game:GetService("Workspace")

local Config = require(ReplicatedStorage:WaitForChild("Shared"):WaitForChild("Config"))
local remotes = ReplicatedStorage:WaitForChild("Remotes")
local openCompanyUI = remotes:FindFirstChild("OpenCompanyUI") or Instance.new("RemoteEvent")
openCompanyUI.Name = "OpenCompanyUI"
openCompanyUI.Parent = remotes

local oldHub = Workspace:FindFirstChild("IndustrialFrontierHub")
if oldHub then oldHub:Destroy() end

local hub = Instance.new("Model")
hub.Name = "IndustrialFrontierHub"
hub.Parent = Workspace

local function part(name, size, position, color, material, parent)
    local p = Instance.new("Part")
    p.Name = name
    p.Size = size
    p.Position = position
    p.Anchored = true
    p.Color = color
    p.Material = material or Enum.Material.SmoothPlastic
    p.TopSurface = Enum.SurfaceType.Smooth
    p.BottomSurface = Enum.SurfaceType.Smooth
    p.Parent = parent or hub
    return p
end

local function sign(text, position, width, parent)
    local board = part("DepartmentSign", Vector3.new(width, 5, 0.5), position, Config.Colors.DeepBlue, Enum.Material.Metal, parent)
    local gui = Instance.new("SurfaceGui")
    gui.Face = Enum.NormalId.Front
    gui.CanvasSize = Vector2.new(800, 180)
    gui.Parent = board
    local label = Instance.new("TextLabel")
    label.Size = UDim2.fromScale(1, 1)
    label.BackgroundTransparency = 1
    label.Text = text
    label.TextColor3 = Config.Colors.White
    label.Font = Enum.Font.GothamBold
    label.TextScaled = true
    label.Parent = gui
    return board
end

-- Main corporate atrium
part("AtriumFloor", Config.Hub.FloorSize, Vector3.new(0, 0, 0), Config.Colors.Floor, Enum.Material.Marble)
part("RearWall", Vector3.new(180, 28, 2), Vector3.new(0, 14, -70), Config.Colors.Navy, Enum.Material.Metal)
part("LeftWall", Vector3.new(2, 28, 140), Vector3.new(-90, 14, 0), Config.Colors.DeepBlue, Enum.Material.Glass)
part("RightWall", Vector3.new(2, 28, 140), Vector3.new(90, 14, 0), Config.Colors.DeepBlue, Enum.Material.Glass)
part("FrontWallLeft", Vector3.new(55, 28, 2), Vector3.new(-62.5, 14, 70), Config.Colors.Navy, Enum.Material.Metal)
part("FrontWallRight", Vector3.new(55, 28, 2), Vector3.new(62.5, 14, 70), Config.Colors.Navy, Enum.Material.Metal)
part("RoofFrame", Vector3.new(180, 2, 140), Vector3.new(0, 29, 0), Config.Colors.DeepBlue, Enum.Material.Glass)

-- Brand wall and reception
sign(Config.Brand .. "  |  " .. Config.Tagline, Vector3.new(0, 18, -68.7), 52, hub)
part("ReceptionDesk", Vector3.new(22, 4, 6), Vector3.new(0, 2, 39), Config.Colors.DeepBlue, Enum.Material.Metal)
part("ReceptionFront", Vector3.new(20, 2.5, 0.4), Vector3.new(0, 2, 35.8), Config.Colors.Blue, Enum.Material.Neon)

-- Central company terminal
local terminal = part("CompanyTerminal", Vector3.new(8, 7, 5), Vector3.new(0, 3.5, -18), Config.Colors.Navy, Enum.Material.Metal)
part("TerminalScreen", Vector3.new(6.8, 4.2, 0.25), Vector3.new(0, 5, -20.65), Config.Colors.Cyan, Enum.Material.Neon)
local prompt = Instance.new("ProximityPrompt")
prompt.ActionText = "Acessar empresa"
prompt.ObjectText = "Terminal corporativo"
prompt.KeyboardKeyCode = Enum.KeyCode.E
prompt.HoldDuration = 0.35
prompt.MaxActivationDistance = 12
prompt.Parent = terminal

prompt.Triggered:Connect(function(player)
    -- Identity comes from the server-authenticated Player object.
    openCompanyUI:FireClient(player, {
        displayName = player.DisplayName,
        userId = player.UserId,
        companyName = player.DisplayName .. " Industries",
        status = "Empresa inicial"
    })
end)

-- Department markers around the atrium
for _, department in ipairs(Config.Departments) do
    local marker = part(department.name, Vector3.new(18, 1, 12), department.position, department.color, Enum.Material.Metal)
    local title = sign(department.name, department.position + Vector3.new(0, 7, -5), 18, hub)
    title.Name = department.name .. "Sign"
    part(department.name .. "Accent", Vector3.new(18, 0.35, 0.5), department.position + Vector3.new(0, 3, -5.3), Config.Colors.Cyan, Enum.Material.Neon)
end

-- Cafeteria props: counter, vending machine and coffee station
part("CafeCounter", Vector3.new(24, 3, 5), Vector3.new(-66, 1.5, 17), Config.Colors.DeepBlue, Enum.Material.Metal)
part("VendingMachine", Vector3.new(4, 8, 3), Vector3.new(-78, 4, 5), Config.Colors.Blue, Enum.Material.Metal)
part("CoffeeMachine", Vector3.new(3, 4, 3), Vector3.new(-56, 2, 7), Config.Colors.Metal, Enum.Material.Metal)

local spawn = Workspace:FindFirstChildOfClass("SpawnLocation") or Instance.new("SpawnLocation")
spawn.Name = "CorporateHubSpawn"
spawn.Size = Vector3.new(8, 1, 8)
spawn.Position = Config.Hub.SpawnPosition
spawn.Anchored = true
spawn.Neutral = true
spawn.Parent = hub

print("[Industrial Frontier] Corporate HUB generated.")
