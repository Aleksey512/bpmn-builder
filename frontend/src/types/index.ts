export type ProcessMode = "create" | "edit";

export interface BpmnError {
  id: string;
  type: "topological" | "logical";
  message: string;
  elementId?: string;
}

export interface BpmnRequest {
  user_id: string;
  text: string;
  bpmn_xml?: string;
}
