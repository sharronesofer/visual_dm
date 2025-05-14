export interface SocialInteraction {
  id: string;
  type: string;
  participants: string[];
  context: {
    location: string;
    time: number;
    witnesses?: string[];
  };
  details: {
    success: boolean;
    type: string;
    subtype?: string;
    data?: any;
  };
  outcome: {
    reputationChange?: number;
    emotionalResponse?: string;
    economicImpact?: any;
    memoryImportance?: number;
  };
} 