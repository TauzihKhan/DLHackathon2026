import { httpGetJson } from "../lib/http";

export type FactValue = string | number;

export type InsightResponse = {
  learner_id: string;
  generated_at: string;
  weak_subtopics: string[];
  priority_subtopic_id: string | null;
  recommended_action: string;
  reason_codes: string[];
  explanation_facts: Record<string, FactValue>;
};

export type PracticeQuestion = {
  question: string;
  intent: string;
  difficulty: number;
};

export type NarrativeInsightResponse = {
  learner_id: string;
  generated_at: string;
  generation_mode: "llm" | "fallback";
  priority_subtopic_id: string | null;
  weak_subtopics: string[];
  reason_codes: string[];
  recommended_action: string;
  narrative_summary: string;
  narrative_explanation: string;
  practice_questions: PracticeQuestion[];
  source_explanation_facts: Record<string, FactValue>;
};

export type InsightsRequestOptions = {
  baseUrl?: string;
  timeoutMs?: number;
};

function encodeLearnerId(learnerId: string): string {
  const trimmed = learnerId.trim();
  if (!trimmed) {
    throw new Error("learnerId cannot be empty");
  }
  return encodeURIComponent(trimmed);
}

export async function getStudentInsights(
  learnerId: string,
  options?: InsightsRequestOptions,
): Promise<InsightResponse> {
  const encodedLearnerId = encodeLearnerId(learnerId);
  return httpGetJson<InsightResponse>(
    `/students/${encodedLearnerId}/insights`,
    options,
  );
}

export async function getStudentNarrativeInsights(
  learnerId: string,
  options?: InsightsRequestOptions,
): Promise<NarrativeInsightResponse> {
  const encodedLearnerId = encodeLearnerId(learnerId);
  return httpGetJson<NarrativeInsightResponse>(
    `/students/${encodedLearnerId}/insights/narrative`,
    options,
  );
}

