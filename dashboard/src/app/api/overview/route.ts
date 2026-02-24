import { NextRequest, NextResponse } from "next/server";
import { getEngineOverview, getLatestRunId } from "@/lib/queries";

export async function GET(request: NextRequest) {
  const runId =
    request.nextUrl.searchParams.get("run_id") || getLatestRunId();
  if (!runId) {
    return NextResponse.json({ error: "No runs found" }, { status: 404 });
  }
  const engines = getEngineOverview(runId);
  return NextResponse.json({ engines, run_id: runId });
}
