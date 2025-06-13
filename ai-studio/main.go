package main

import (
	"embed"
	"log"

	"github.com/wailsapp/wails/v2"
	"github.com/wailsapp/wails/v2/pkg/options"
	"github.com/wailsapp/wails/v2/pkg/options/assetserver"

	"github.com/ai-studio/backend/infrastructure/container"
)

//go:embed all:frontend/dist
var assets embed.FS

func main() {
	// Initialize dependency injection container
	c := container.NewContainer()

	// Create application with options
	err := wails.Run(&options.App{
		Title:  "AI Launcher - Universal AI Tool Manager",
		Width:  1200,
		Height: 800,
		AssetServer: &assetserver.Options{
			Assets: assets,
		},
		BackgroundColour: &options.RGBA{R: 27, G: 38, B: 54, A: 1},
		OnStartup:        c.WailsApp.Startup,
		Bind: []interface{}{
			c.WailsApp,
		},
	})

	if err != nil {
		log.Fatalf("Error starting application: %v", err)
	}
}
