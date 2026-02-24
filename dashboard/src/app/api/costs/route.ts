import { NextRequest, NextResponse } from "next/server";
import { getCosts, getLatestRunId } from "@/lib/queries";

export async function GET(request: NextRequest) {
  const runId =
    request.nextUrl.searchParams.get("run_id") || getLatestRunId();
  if (!runId) {
    return NextResponse.json({ error: "No runs found" }, { status: 404 });
  }
  const data = getCosts(runId);
  return NextResponse.json({ ...data, run_id: runId });
}
