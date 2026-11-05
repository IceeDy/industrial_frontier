local Config = {}

Config.Brand = "INDUSTRIAL FRONTIER"
Config.Tagline = "CORPORATE HEADQUARTERS"

Config.Colors = {
    Navy = Color3.fromRGB(7, 17, 36),
    DeepBlue = Color3.fromRGB(10, 31, 61),
    Blue = Color3.fromRGB(20, 115, 220),
    Cyan = Color3.fromRGB(38, 190, 255),
    White = Color3.fromRGB(235, 244, 255),
    Metal = Color3.fromRGB(105, 125, 148),
    Floor = Color3.fromRGB(183, 197, 213),
    Glass = Color3.fromRGB(95, 180, 225),
}

Config.Hub = {
    FloorSize = Vector3.new(180, 2, 140),
    WallHeight = 28,
    SpawnPosition = Vector3.new(0, 4, 48),
}

Config.Departments = {
    { name = "CENTRO DE OPERACOES", position = Vector3.new(-42, 0, -18), color = Color3.fromRGB(18, 91, 170) },
    { name = "FINANCEIRO", position = Vector3.new(42, 0, -18), color = Color3.fromRGB(24, 105, 160) },
    { name = "MERCADO", position = Vector3.new(67, 0, 12), color = Color3.fromRGB(25, 115, 180) },
    { name = "LOGISTICA", position = Vector3.new(67, 0, -48), color = Color3.fromRGB(25, 115, 180) },
    { name = "PESQUISA E DESENVOLVIMENTO", position = Vector3.new(42, 0, -58), color = Color3.fromRGB(20, 100, 160) },
    { name = "SALA DE REUNIOES", position = Vector3.new(-42, 0, -58), color = Color3.fromRGB(20, 100, 160) },
    { name = "CAFETERIA", position = Vector3.new(-67, 0, 12), color = Color3.fromRGB(20, 100, 160) },
}

return Config
