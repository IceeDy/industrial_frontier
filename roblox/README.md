# Industrial Frontier — Roblox prototype

This folder contains the first Roblox experience scaffold. It is isolated from the existing Python economic engine and HTML prototype.

## First milestone
- Corporate headquarters lobby generated in Luau at server startup.
- Shared physical HUB for all players.
- Departments: reception, operations, finance, market, logistics, R&D, meeting room and cafeteria.
- Company terminal opens a player-specific dashboard. The server derives identity from the authenticated Roblox Player; clients cannot select another UserId.

## Requirements
Roblox Studio (Windows/macOS) and Rojo 7.x are required to sync and run the experience. This repository can be edited without Studio, but gameplay validation and publishing require Studio.

## Run
1. Install Rojo 7.x and Roblox Studio.
2. From this folder run: `rojo serve default.project.json`
3. Connect the Rojo plugin in Studio.
4. Press Play. The server generates the HUB.

The existing Python engine and HTML prototype are untouched. This is a visual/interaction slice; persistent company data and economy integration are later milestones.
