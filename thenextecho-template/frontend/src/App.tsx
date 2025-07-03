import { Button } from "@/components/ui/button";

function App() {
  return (
    <div className="dark container mx-auto p-4">
      <header className="text-center my-12">
        <h1 className="text-5xl font-extrabold tracking-tight">TheNextEcho</h1>
        <p className="text-muted-foreground mt-2">Titan Edition - Your AI Video Suite</p>
      </header>

      <main className="max-w-2xl mx-auto">
        <div className="p-8 border rounded-lg bg-card text-card-foreground">
          <h2 className="text-2xl font-semibold mb-6">Create New Project</h2>
          <div className="space-y-4">
            <div>
              <label htmlFor="theme" className="block text-sm font-medium mb-2">Video Theme</label>
              <input id="theme" className="w-full p-2 bg-input rounded-md" placeholder="e.g., The future of space exploration" />
            </div>
            <Button className="w-full" size="lg">Start Generation</Button>
          </div>
        </div>
      </main>
    </div>
  )
}

export default App
