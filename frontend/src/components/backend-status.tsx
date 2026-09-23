"use client";

import { Badge } from "@/components/ui/badge";
import { apiBaseUrl } from "@/lib/api";
import { useEffect, useState } from "react";

type Status = "checking" | "online" | "offline";

export function BackendStatus() {
  const [status, setStatus] = useState<Status>("checking");
  const [latencyMs, setLatencyMs] = useState<number | null>(null);

  useEffect(() => {
    const check = async () => {
      const started = performance.now();
      try {
        const res = await fetch(`${apiBaseUrl()}/health`);
        if (!res.ok) throw new Error(String(res.status));
        setStatus("online");
        setLatencyMs(Math.round(performance.now() - started));
      } catch {
        setStatus("offline");
        setLatencyMs(null);
      }
    };
    check();
    const interval = setInterval(check, 10_000);
    return () => clearInterval(interval);
  }, []);

  if (status === "checking") {
    return <Badge variant="secondary">backend: checking…</Badge>;
  }

  return status === "online" ? (
    <Badge>backend: online · {latencyMs}ms</Badge>
  ) : (
    <Badge variant="destructive">backend: offline</Badge>
  );
}
