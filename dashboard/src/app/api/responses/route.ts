import { NextRequest, NextResponse } from "next/server";
import { getResponses, getLatestRunId } from "@/lib/queries";

export async function GET(request: NextRequest) {
  const runId =
    request.nextUrl.searchParams.get("run_id") || getLatestRunId();
  const promptId = request.nextUrl.searchParams.get("prompt_id");
  const provider = request.nextUrl.searchParams.get("provider");

  if (!runId) {
    return NextResponse.json({ error: "No runs found" }, { status: 404 });
  }
  if (!promptId || !provider) {
    return NextResponse.json(
      { error: "prompt_id and provider are required" },
      { status: 400 }
    );
  }

  const responses = getResponses(runId, promptId, provider);
  return NextResponse.json({ responses, run_id: runId });
}
