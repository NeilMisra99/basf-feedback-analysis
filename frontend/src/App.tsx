import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { MessageSquare, LayoutDashboard } from "lucide-react";
import { Suspense, lazy } from "react";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { FeedbackFormSkeleton } from "./components/ui/loading";
import Dashboard from "./components/Dashboard";

// Lazy load only the feedback form
// Dashboard loads immediately for faster tab switching
const FeedbackForm = lazy(() => import("./components/FeedbackForm"));

function App() {
  return (
    <div className="min-h-screen bg-background py-10">
      <div className="container mx-auto px-4">
        {/* Header */}
        <header className="text-center mb-8">
          <h1 className="text-4xl font-bold text-foreground mb-2">
            Feedback Analysis System
          </h1>
          <p className="text-lg text-muted-foreground">
            AI-powered sentiment analysis and response generation
          </p>
        </header>

        {/* Main Content with Tabs */}
        <main className="max-w-6xl mx-auto">
          <Tabs defaultValue="submit" className="w-full">
            <TabsList className="flex justify-center gap-8 mb-8 bg-transparent w-fit mx-auto">
              <TabsTrigger
                value="submit"
                className="flex items-center gap-2 rounded-xl p-6 border-none data-[state=active]:shadow-none shadow-none"
              >
                <MessageSquare className="h-4 w-4" />
                Submit Feedback
              </TabsTrigger>
              <TabsTrigger
                value="dashboard"
                className="flex items-center gap-2 rounded-xl p-6 border-none data-[state=active]:shadow-none shadow-none"
              >
                <LayoutDashboard className="h-4 w-4" />
                Dashboard
              </TabsTrigger>
            </TabsList>

            <TabsContent value="submit" className="bg-muted p-8 rounded-2xl">
              <ErrorBoundary>
                <Suspense fallback={<FeedbackFormSkeleton />}>
                  <FeedbackForm />
                </Suspense>
              </ErrorBoundary>
            </TabsContent>

            <TabsContent
              value="dashboard"
              className="bg-muted p-8 rounded-2xl h-[600px]"
            >
              <ErrorBoundary>
                <Dashboard />
              </ErrorBoundary>
            </TabsContent>
          </Tabs>
        </main>
      </div>
    </div>
  );
}

export default App;
