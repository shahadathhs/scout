import { BackendStatus } from "@/components/backend-status";
import { Button } from "@/components/ui/button";

export default function Home() {
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-8 px-6 text-center">
      <div className="flex flex-col items-center gap-3">
        <h1 className="text-5xl font-semibold tracking-tight">scout</h1>
        <p className="max-w-md text-lg text-muted-foreground">
          Self-hosted deep research. Ask a question — scout plans, researches in parallel, and
          delivers a report where every claim cites a source.
        </p>
      </div>
      <div className="flex flex-col items-center gap-4">
        <Button disabled>Start researching — coming soon</Button>
        <BackendStatus />
      </div>
    </div>
  );
}
