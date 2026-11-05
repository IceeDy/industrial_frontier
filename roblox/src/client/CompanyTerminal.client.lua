local Players = game:GetService("Players")
local ReplicatedStorage = game:GetService("ReplicatedStorage")

local player = Players.LocalPlayer
local openCompanyUI = ReplicatedStorage:WaitForChild("Remotes"):WaitForChild("OpenCompanyUI")

local function buildDashboard(data)
    local playerGui = player:WaitForChild("PlayerGui")
    local existing = playerGui:FindFirstChild("CompanyDashboard")
    if existing then existing:Destroy() end

    local gui = Instance.new("ScreenGui")
    gui.Name = "CompanyDashboard"
    gui.ResetOnSpawn = false
    gui.IgnoreGuiInset = true
    gui.Parent = playerGui

    local panel = Instance.new("Frame")
    panel.Name = "MainPanel"
    panel.Size = UDim2.fromScale(0.58, 0.62)
    panel.Position = UDim2.fromScale(0.21, 0.19)
    panel.BackgroundColor3 = Color3.fromRGB(7, 17, 36)
    panel.BorderSizePixel = 0
    panel.Parent = gui

    local corner = Instance.new("UICorner")
    corner.CornerRadius = UDim.new(0, 12)
    corner.Parent = panel

    local stroke = Instance.new("UIStroke")
    stroke.Color = Color3.fromRGB(38, 190, 255)
    stroke.Thickness = 1.5
    stroke.Parent = panel

    local header = Instance.new("TextLabel")
    header.Size = UDim2.new(1, -70, 0, 58)
    header.Position = UDim2.fromOffset(24, 12)
    header.BackgroundTransparency = 1
    header.Text = "INDUSTRIAL FRONTIER  /  CENTRAL CORPORATIVA"
    header.TextColor3 = Color3.fromRGB(235, 244, 255)
    header.Font = Enum.Font.GothamBold
    header.TextSize = 20
    header.TextXAlignment = Enum.TextXAlignment.Left
    header.Parent = panel

    local close = Instance.new("TextButton")
    close.Size = UDim2.fromOffset(42, 42)
    close.Position = UDim2.new(1, -54, 0, 14)
    close.Text = "X"
    close.TextColor3 = Color3.new(1, 1, 1)
    close.BackgroundColor3 = Color3.fromRGB(20, 115, 220)
    close.Font = Enum.Font.GothamBold
    close.TextSize = 18
    close.Parent = panel
    close.MouseButton1Click:Connect(function() gui:Destroy() end)

    local company = Instance.new("TextLabel")
    company.Size = UDim2.new(1, -48, 0, 48)
    company.Position = UDim2.fromOffset(24, 88)
    company.BackgroundColor3 = Color3.fromRGB(10, 31, 61)
    company.Text = data.companyName or "Minha empresa"
    company.TextColor3 = Color3.fromRGB(38, 190, 255)
    company.Font = Enum.Font.GothamBold
    company.TextSize = 24
    company.Parent = panel

    local info = Instance.new("TextLabel")
    info.Size = UDim2.new(1, -48, 0, 92)
    info.Position = UDim2.fromOffset(24, 150)
    info.BackgroundTransparency = 1
    info.Text = "Diretor: " .. (data.displayName or player.DisplayName)
        .. "\nID da conta: " .. tostring(data.userId or player.UserId)
        .. "\nStatus: " .. (data.status or "Inicial")
    info.TextColor3 = Color3.fromRGB(210, 225, 240)
    info.Font = Enum.Font.Gotham
    info.TextSize = 17
    info.TextXAlignment = Enum.TextXAlignment.Left
    info.TextYAlignment = Enum.TextYAlignment.Top
    info.Parent = panel

    local note = Instance.new("TextLabel")
    note.Size = UDim2.new(1, -48, 0, 54)
    note.Position = UDim2.fromOffset(24, 260)
    note.BackgroundColor3 = Color3.fromRGB(10, 31, 61)
    note.Text = "Painel inicial de demonstração. Economia, produção e mercado serão conectados nas próximas etapas."
    note.TextWrapped = true
    note.TextColor3 = Color3.fromRGB(180, 205, 230)
    note.Font = Enum.Font.Gotham
    note.TextSize = 14
    note.Parent = panel
end

openCompanyUI.OnClientEvent:Connect(buildDashboard)
