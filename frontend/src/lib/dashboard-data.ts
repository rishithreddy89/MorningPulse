export type Urgency = "high" | "medium" | "low";

export interface Alert {
  id: string;
  title: string;
  summary: string;
  urgency: Urgency;
  impact: number;
  whyItMatters: string;
  recommendedAction: string;
  source: string;
  sourceUrl: string;
}

export interface Trend {
  id: string;
  name: string;
  explanation: string;
  direction: "increasing" | "decreasing" | "stable";
  change: string;
}

export interface PainPoint {
  id: string;
  statement: string;
  sentiment: "negative" | "neutral";
  source: string;
}

export interface CompetitorUpdate {
  id: string;
  company: string;
  title: string;
  summary: string;
  impact: number;
  recommendedAction: string;
}

export const summary =
  "Today's intelligence brief surfaces three high-priority shifts across the K-12 administrative software landscape. Two competitors announced AI-assisted reporting features, district procurement teams are signaling renewed interest in compliance tooling, and parent communication remains the most cited pain point across surveyed administrators this week.";

export const alerts: Alert[] = [
  {
    id: "a1",
    title: "Competitor launches AI reporting suite for districts",
    summary:
      "PowerSchool announced an AI-driven analytics module targeting superintendents, with early access for 200 districts.",
    urgency: "high",
    impact: 92,
    whyItMatters: "Direct overlap with our Q3 roadmap and core ICP.",
    recommendedAction: "Accelerate AI summary feature release; brief sales on differentiators.",
    source: "EdSurge",
    sourceUrl: "#",
  },
  {
    id: "a2",
    title: "New federal compliance guidance on student data",
    summary:
      "The Department of Education issued updated guidance on AI use in classrooms, effective next quarter.",
    urgency: "high",
    impact: 87,
    whyItMatters: "Affects onboarding messaging for public school customers.",
    recommendedAction: "Publish compliance one-pager; update security documentation.",
    source: "ED.gov",
    sourceUrl: "#",
  },
  {
    id: "a3",
    title: "Spike in admin discussions around chronic absenteeism",
    summary:
      "Conversations across district forums increased 38% week-over-week, focused on early-warning systems.",
    urgency: "medium",
    impact: 64,
    whyItMatters: "Adjacent to our attendance analytics module.",
    recommendedAction: "Schedule customer interviews; prototype absenteeism dashboard.",
    source: "District Administration",
    sourceUrl: "#",
  },
  {
    id: "a4",
    title: "Vendor consolidation trend in mid-size districts",
    summary:
      "Three regional districts publicly committed to reducing SaaS tools by 40% this year.",
    urgency: "low",
    impact: 41,
    whyItMatters: "Opportunity to position as a consolidation play.",
    recommendedAction: "Develop bundled pricing tier for mid-market.",
    source: "K-12 Dive",
    sourceUrl: "#",
  },
];

export const trends: Trend[] = [
  {
    id: "t1",
    name: "AI-assisted lesson planning",
    explanation: "Mentions across teacher forums and district RFPs continue to climb.",
    direction: "increasing",
    change: "+24% WoW",
  },
  {
    id: "t2",
    name: "Parent communication apps",
    explanation: "Steady growth in procurement interest for unified parent messaging tools.",
    direction: "increasing",
    change: "+11% WoW",
  },
  {
    id: "t3",
    name: "Standalone gradebook tools",
    explanation: "Interest declining as districts favor integrated platforms.",
    direction: "decreasing",
    change: "-9% WoW",
  },
  {
    id: "t4",
    name: "Data privacy certifications",
    explanation: "RFPs increasingly require SOC 2 and state-specific attestations.",
    direction: "increasing",
    change: "+17% WoW",
  },
];

export const painPoints: PainPoint[] = [
  {
    id: "p1",
    statement: "Parent communication tools require too many separate logins.",
    sentiment: "negative",
    source: "District CTO survey, Apr 2026",
  },
  {
    id: "p2",
    statement: "Reporting exports take days to reconcile across systems.",
    sentiment: "negative",
    source: "r/k12sysadmin thread",
  },
  {
    id: "p3",
    statement: "Onboarding new staff to the SIS remains slow but manageable.",
    sentiment: "neutral",
    source: "Customer interview, Westfield USD",
  },
  {
    id: "p4",
    statement: "Mobile experience for principals is inconsistent across vendors.",
    sentiment: "negative",
    source: "EdWeek roundtable",
  },
];

export const competitors: CompetitorUpdate[] = [
  {
    id: "c1",
    company: "PowerSchool",
    title: "AI Insights module general availability",
    summary:
      "Released district-wide AI summaries for attendance, grades, and behavior, bundled into the Unified Insights tier.",
    impact: 88,
    recommendedAction: "Update battlecard; emphasize our source citations.",
  },
  {
    id: "c2",
    company: "Infinite Campus",
    title: "New parent portal redesign",
    summary:
      "Launched a streamlined parent portal with consolidated messaging and translation in 14 languages.",
    impact: 71,
    recommendedAction: "Audit our parent UX; prioritize translation parity.",
  },
  {
    id: "c3",
    company: "Schoology",
    title: "Pricing model adjustment for SMB districts",
    summary:
      "Introduced a per-student tier targeted at districts under 5,000 students.",
    impact: 58,
    recommendedAction: "Evaluate SMB pricing response with finance.",
  },
];
