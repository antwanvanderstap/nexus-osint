export type EntityType =
  | "person" | "company" | "domain" | "email"
  | "phone" | "address" | "ip" | "username"
  | "document" | "vessel" | "aircraft";

export type UseCase =
  | "research" | "fraud_prevention" | "due_diligence"
  | "journalism" | "security"
  | "fcra_decision" | "employment" | "housing" | "credit";

export type TosRisk = "none" | "low" | "medium" | "high";

export interface Entity {
  id: string;
  type: EntityType;
  label: string;
  properties: Record<string, unknown>;
  source_module: string;
  source_url?: string;
}

export interface Relationship {
  source_id: string;
  target_id: string;
  type: string;
  properties: Record<string, unknown>;
  source_module: string;
}

export interface ModuleMetadata {
  name: string;
  display_name: string;
  description: string;
  version: string;
  data_source: string;
  legal_uses: UseCase[];
  prohibited_uses: UseCase[];
  tos_risk: TosRisk;
  requires_api_key: boolean;
  pii_returned: boolean;
  input_types: EntityType[];
  output_types: EntityType[];
}

export interface Case {
  id: string;
  name: string;
  description: string;
  declared_purpose: UseCase;
  created_at: string;
  updated_at: string;
  entities: Entity[];
  relationships: Relationship[];
}
