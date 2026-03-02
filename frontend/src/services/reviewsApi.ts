import { httpGetJson } from "../lib/http";

export type DueReviewItem = {
  module_id: string;
  topic_id: string;
  subtopic_id: string;
  mastery: number;
  confidence: number;
  decay_risk_score: number;
  review_interval_days: number;
  next_review_at: string;
  days_overdue: number;
  priority_score: number;
};

export type DueReviewsResponse = {
  learner_id: string;
  generated_at: string;
  due_count: number;
  items: DueReviewItem[];
};

export type ReviewsRequestOptions = {
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

export async function getDueReviews(
  learnerId: string,
  options?: ReviewsRequestOptions,
): Promise<DueReviewsResponse> {
  const encodedLearnerId = encodeLearnerId(learnerId);
  return httpGetJson<DueReviewsResponse>(
    `/students/${encodedLearnerId}/reviews/due`,
    options,
  );
}

